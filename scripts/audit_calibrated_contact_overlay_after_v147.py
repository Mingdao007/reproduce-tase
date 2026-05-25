#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
import xml.etree.ElementTree as ET
from typing import Any

import mujoco
import numpy as np
import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.kinematics import load_model, make_data, set_qpos, site_position, site_rotation_matrix  # noqa: E402
from tase_repro.contact_ladder import positive_contact_normal_force_between  # noqa: E402


DEFAULT_SOURCE_CONFIG = "configs/mujoco_ur10e_calibrated_20260525T1641_tcp_offset.yaml"
DEFAULT_PREVIOUS_METRICS = "runs/calibrated_mjcf_replay_after_v147/20260525T212000/metrics.yaml"
DEFAULT_OVERLAY_MJCF = "assets/mjcf/ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.xml"
DEFAULT_OVERLAY_CONFIG = "configs/mujoco_ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.yaml"
DEFAULT_TIP_RADIUS_M = 0.045
DEFAULT_PLANE_TILT_RAD_ABOUT_Y = 0.1745329252
DEFAULT_NORMAL_WORLD = [0.1736481777, 0.0, 0.9848077530]
DEFAULT_TOLERANCE_M = 1.0e-6
DEFAULT_ACTIVATION_PROBE_PENETRATION_M = 1.0e-3


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


def resolve(path: str | pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(path)
    if path.is_absolute():
        return path
    return ROOT / path


def rel(path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def fmt_vec(values: np.ndarray | list[float]) -> str:
    return " ".join(f"{float(value):.17g}" for value in values)


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(payload, f, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True)


def git_value(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def write_git_state(out_dir: pathlib.Path, *, command: list[str]) -> None:
    branch = git_value(["branch", "--show-current"])
    commit = git_value(["rev-parse", "HEAD"])
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
    lines = [
        "# Git State",
        "",
        f"- Branch: `{branch}`",
        f"- Commit: `{commit}`",
        f"- Dirty tree: `{bool(status)}`",
        "- Status:",
        "",
        "```text",
        status,
        "```",
        "",
        "- Command:",
        "",
        "```bash",
        " ".join(command),
        "```",
        "",
    ]
    (out_dir / "git_state.md").write_text("\n".join(lines), encoding="utf-8")


def remove_named_child(parent: ET.Element, tag: str, name: str) -> None:
    for child in list(parent):
        if child.tag == tag and child.attrib.get("name") == name:
            parent.remove(child)


def disable_existing_geom_contacts(root: ET.Element) -> list[str]:
    disabled: list[str] = []
    for geom in root.iter("geom"):
        name = geom.attrib.get("name", "")
        if name in {"diagnostic_contact_plane_unaccepted", "diagnostic_contact_tip_unaccepted"}:
            continue
        geom.set("contype", "0")
        geom.set("conaffinity", "0")
        if name:
            disabled.append(name)
    return disabled


def find_body(root: ET.Element, name: str) -> ET.Element:
    for body in root.iter("body"):
        if body.attrib.get("name") == name:
            return body
    raise ValueError(f"body not found: {name}")


def write_overlay_mjcf(
    *,
    source_mjcf_path: pathlib.Path,
    output_mjcf_path: pathlib.Path,
    plane_point_world_m: np.ndarray,
    plane_tilt_rad_about_y: float,
    tip_radius_m: float,
    tip_center_local_offset_m: np.ndarray,
) -> None:
    tree = ET.parse(source_mjcf_path)
    root = tree.getroot()
    root.set("model", "ur10e_calibrated_20260525T1641_diagnostic_contact_overlay")
    disable_existing_geom_contacts(root)
    worldbody = root.find("worldbody")
    if worldbody is None:
        raise ValueError("source MJCF has no worldbody")

    remove_named_child(worldbody, "geom", "diagnostic_contact_plane_unaccepted")
    plane = ET.Element(
        "geom",
        {
            "name": "diagnostic_contact_plane_unaccepted",
            "type": "plane",
            "pos": fmt_vec(plane_point_world_m),
            "euler": f"0 {plane_tilt_rad_about_y:.17g} 0",
            "size": "1.2 1.2 0.02",
            "rgba": "0.78 0.74 0.62 0.45",
            "friction": "1 0.005 0.0001",
            "contype": "1",
            "conaffinity": "1",
        },
    )
    worldbody.insert(0, plane)

    tcp_body = find_body(root, "tcp_live_offset_body")
    remove_named_child(tcp_body, "body", "diagnostic_contact_tip_center_unaccepted")
    tip_body = ET.SubElement(
        tcp_body,
        "body",
        {
            "name": "diagnostic_contact_tip_center_unaccepted",
            "pos": fmt_vec(tip_center_local_offset_m),
        },
    )
    ET.SubElement(
        tip_body,
        "geom",
        {
            "name": "diagnostic_contact_tip_unaccepted",
            "type": "sphere",
            "size": f"{tip_radius_m:.17g}",
            "rgba": "0.95 0.35 0.12 0.72",
            "density": "700",
            "friction": "1 0.005 0.0001",
            "contype": "1",
            "conaffinity": "1",
        },
    )

    ET.indent(tree, space="  ")
    output_mjcf_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_mjcf_path, encoding="utf-8", xml_declaration=False)


def build_overlay_config(
    *,
    source_config: dict[str, Any],
    source_config_path: pathlib.Path,
    overlay_mjcf_path: pathlib.Path,
    overlay_config_path: pathlib.Path,
    plane_point_world_m: np.ndarray,
    normal_world: np.ndarray,
    plane_tilt_rad_about_y: float,
    tip_radius_m: float,
    tip_center_local_offset_m: np.ndarray,
) -> dict[str, Any]:
    source_ur = source_config["ur10e_mujoco"]
    return {
        "v1": {
            "model_status": "v148_diagnostic_contact_overlay_from_v147_calibrated_seed",
            "contact_status": "diagnostic_unaccepted_overlay_only",
            "claim_boundary": "offline_contact_geometry_proposal_not_contact_or_hardware_evidence",
        },
        "ur10e_mujoco": {
            "mjcf_path": rel(overlay_mjcf_path),
            "source_kinematic_config_path": rel(source_config_path),
            "source_kinematic_mjcf_path": source_ur["mjcf_path"],
            "source_seed_path": source_ur["source_seed_path"],
            "source_calibration_path": source_ur["source_calibration_path"],
            "timestep_s": float(source_ur["timestep_s"]),
            "tcp_site": source_ur["tcp_site"],
            "payload_kg": float(source_ur["payload_kg"]),
            "payload_cog_m": [float(v) for v in source_ur["payload_cog_m"]],
            "joint_names": list(source_ur["joint_names"]),
            "joint_limit_rad": source_ur["joint_limit_rad"],
            "contact": {
                "status": "diagnostic_unaccepted_overlay_only",
                "plane_geom_name": "diagnostic_contact_plane_unaccepted",
                "tip_geom_name": "diagnostic_contact_tip_unaccepted",
                "source_convention": "v54 tilted 10deg normal, translated through v147 current RTDE TCP site",
                "plane_point_world_m": [float(v) for v in plane_point_world_m],
                "plane_tilt_rad_about_y": float(plane_tilt_rad_about_y),
                "expected_normal_world": [float(v) for v in normal_world],
                "contact_tip_radius_m": float(tip_radius_m),
                "tip_center_local_offset_m_from_tcp": [float(v) for v in tip_center_local_offset_m],
                "acceptance_status": "not_accepted",
                "reason": (
                    "This overlay creates an offline diagnostic start-contact geometry for "
                    "simulation continuation only; it is not contact calibration evidence."
                ),
            },
        },
        "claim_boundary": {
            "approved_read_only_evidence": False,
            "contact_setup_target_acceptance": False,
            "orientation_gate_acceptance": False,
            "hardware_readiness": False,
            "completion_claim_allowed": False,
        },
    }


def geom_id(model: mujoco.MjModel, name: str) -> int:
    idx = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, name)
    if idx < 0:
        raise ValueError(f"geom not found: {name}")
    return int(idx)


def contact_pair_counts(
    data: mujoco.MjData,
    *,
    plane_idx: int,
    tip_idx: int,
) -> tuple[int, int]:
    target_pair = {int(plane_idx), int(tip_idx)}
    target_count = 0
    non_target_count = 0
    for idx in range(data.ncon):
        pair = {int(data.contact[idx].geom[0]), int(data.contact[idx].geom[1])}
        if pair == target_pair:
            target_count += 1
        else:
            non_target_count += 1
    return int(target_count), int(non_target_count)


def build_payload(
    *,
    source_config_path: pathlib.Path,
    previous_metrics_path: pathlib.Path,
    overlay_mjcf_path: pathlib.Path,
    overlay_config_path: pathlib.Path,
    run_id: str,
    tip_radius_m: float,
    plane_tilt_rad_about_y: float,
    normal_world: list[float],
    tolerance_m: float,
    activation_probe_penetration_m: float,
    write_overlay: bool,
) -> dict[str, Any]:
    violations: list[str] = []
    source_config = load_yaml(source_config_path)
    previous = load_yaml(previous_metrics_path)
    source_ur = source_config["ur10e_mujoco"]
    seed_path = resolve(source_ur["source_seed_path"])
    seed = load_yaml(seed_path)
    source_mjcf_path = resolve(source_ur["mjcf_path"])
    q = np.asarray(seed["current_rtde_state"]["actual_q_rad"], dtype=float)
    normal = np.asarray(normal_world, dtype=float)
    normal = normal / np.linalg.norm(normal)

    if previous.get("summary", {}).get("calibrated_mjcf_replay_matches_rtde_tcp") is not True:
        violations.append("previous calibrated MJCF replay audit did not pass")
    if previous.get("summary", {}).get("completion_claim_allowed") is not False:
        violations.append("previous calibrated MJCF replay audit drifted into completion claim")

    source_model = load_model(source_mjcf_path)
    source_data = make_data(source_model)
    set_qpos(source_model, source_data, q)
    tcp_site = str(source_ur["tcp_site"])
    tcp_position = site_position(source_model, source_data, tcp_site)
    tcp_rotation = site_rotation_matrix(source_model, source_data, tcp_site)
    tip_center_local_offset = tcp_rotation.T @ (float(tip_radius_m) * normal)

    if write_overlay:
        write_overlay_mjcf(
            source_mjcf_path=source_mjcf_path,
            output_mjcf_path=overlay_mjcf_path,
            plane_point_world_m=tcp_position,
            plane_tilt_rad_about_y=float(plane_tilt_rad_about_y),
            tip_radius_m=float(tip_radius_m),
            tip_center_local_offset_m=tip_center_local_offset,
        )
        overlay_config = build_overlay_config(
            source_config=source_config,
            source_config_path=source_config_path,
            overlay_mjcf_path=overlay_mjcf_path,
            overlay_config_path=overlay_config_path,
            plane_point_world_m=tcp_position,
            normal_world=normal,
            plane_tilt_rad_about_y=float(plane_tilt_rad_about_y),
            tip_radius_m=float(tip_radius_m),
            tip_center_local_offset_m=tip_center_local_offset,
        )
        write_yaml(overlay_config_path, overlay_config)

    overlay_model = load_model(overlay_mjcf_path)
    overlay_data = make_data(overlay_model)
    set_qpos(overlay_model, overlay_data, q)
    overlay_tcp_position = site_position(overlay_model, overlay_data, tcp_site)
    plane_idx = geom_id(overlay_model, "diagnostic_contact_plane_unaccepted")
    tip_idx = geom_id(overlay_model, "diagnostic_contact_tip_unaccepted")
    plane_point = overlay_data.geom_xpos[plane_idx].copy()
    plane_normal = overlay_data.geom_xmat[plane_idx].reshape(3, 3)[:, 2].copy()
    if float(np.dot(plane_normal, normal)) < 0.0:
        plane_normal = -plane_normal
    tip_center = overlay_data.geom_xpos[tip_idx].copy()

    tcp_plane_signed_distance = float(np.dot(overlay_tcp_position - plane_point, plane_normal))
    tip_center_plane_signed_distance = float(np.dot(tip_center - plane_point, plane_normal))
    tip_surface_gap_m = float(tip_center_plane_signed_distance - tip_radius_m)
    normal_error = float(np.linalg.norm(plane_normal - normal))
    tcp_site_shift_m = float(np.linalg.norm(overlay_tcp_position - tcp_position))
    tip_center_expected = tcp_position + tip_radius_m * normal
    tip_center_error_m = float(np.linalg.norm(tip_center - tip_center_expected))
    target_contact_pair_count, non_target_contact_count = contact_pair_counts(
        overlay_data,
        plane_idx=plane_idx,
        tip_idx=tip_idx,
    )

    activation_model = load_model(overlay_mjcf_path)
    activation_data = make_data(activation_model)
    activation_plane_idx = geom_id(activation_model, "diagnostic_contact_plane_unaccepted")
    activation_tip_idx = geom_id(activation_model, "diagnostic_contact_tip_unaccepted")
    activation_model.geom_pos[activation_plane_idx] += float(activation_probe_penetration_m) * normal
    set_qpos(activation_model, activation_data, q)
    activation_target_count, activation_non_target_count = contact_pair_counts(
        activation_data,
        plane_idx=activation_plane_idx,
        tip_idx=activation_tip_idx,
    )
    activation_force_N, _ = positive_contact_normal_force_between(
        activation_model,
        activation_data,
        geom_a_name="diagnostic_contact_plane_unaccepted",
        geom_b_name="diagnostic_contact_tip_unaccepted",
    )

    current_tcp_on_plane = abs(tcp_plane_signed_distance) <= tolerance_m
    tip_tangent = abs(tip_surface_gap_m) <= tolerance_m
    normal_matches = normal_error <= tolerance_m
    tcp_unchanged = tcp_site_shift_m <= tolerance_m
    tip_center_matches = tip_center_error_m <= tolerance_m
    seed_has_no_non_target_contacts = non_target_contact_count == 0
    activation_probe_clean = activation_target_count > 0 and activation_non_target_count == 0
    overlay_consistent = all(
        [
            current_tcp_on_plane,
            tip_tangent,
            normal_matches,
            tcp_unchanged,
            tip_center_matches,
            seed_has_no_non_target_contacts,
            activation_probe_clean,
        ]
    )
    if not overlay_consistent:
        violations.append("diagnostic contact overlay geometry is inconsistent at the v147 seed pose")

    return {
        "run_source": "calibrated diagnostic contact overlay audit after v147",
        "audit_run_id": run_id,
        "source_files": {
            "source_config": rel(source_config_path),
            "previous_calibrated_mjcf_replay": rel(previous_metrics_path),
            "source_mjcf": rel(source_mjcf_path),
            "seed": rel(seed_path),
            "overlay_mjcf": rel(overlay_mjcf_path),
            "overlay_config": rel(overlay_config_path),
        },
        "summary": {
            "audit_passed": not violations,
            "violations": violations,
            "overlay_model_loads": True,
            "diagnostic_contact_overlay_generated": bool(write_overlay),
            "model_nq": int(overlay_model.nq),
            "model_nv": int(overlay_model.nv),
            "model_ngeom": int(overlay_model.ngeom),
            "model_nsite": int(overlay_model.nsite),
            "model_ncon_at_seed": int(overlay_data.ncon),
            "tcp_site": tcp_site,
            "plane_geom_name": "diagnostic_contact_plane_unaccepted",
            "tip_geom_name": "diagnostic_contact_tip_unaccepted",
            "current_tcp_site_on_diagnostic_plane": current_tcp_on_plane,
            "contact_tip_surface_tangent_to_plane": tip_tangent,
            "plane_normal_matches_expected": normal_matches,
            "tcp_site_shift_m": tcp_site_shift_m,
            "tip_center_error_m": tip_center_error_m,
            "tcp_plane_signed_distance_m": tcp_plane_signed_distance,
            "tip_surface_gap_m": tip_surface_gap_m,
            "plane_normal_error": normal_error,
            "contact_tip_radius_m": float(tip_radius_m),
            "target_contact_pair_count_at_seed": target_contact_pair_count,
            "non_target_contact_count_at_seed": non_target_contact_count,
            "seed_has_no_non_target_contacts": seed_has_no_non_target_contacts,
            "activation_probe_penetration_m": float(activation_probe_penetration_m),
            "activation_probe_target_contact_pair_count": activation_target_count,
            "activation_probe_non_target_contact_count": activation_non_target_count,
            "activation_probe_target_normal_force_N": float(activation_force_N),
            "activation_probe_clean_target_contact": activation_probe_clean,
            "simulation_can_start_from_diagnostic_overlay": overlay_consistent,
            "diagnostic_overlay_acceptance_status": "not_accepted",
            "approved_read_only_evidence_claim": False,
            "contact_setup_target_acceptance_claim": False,
            "orientation_gate_acceptance_claim": False,
            "hardware_readiness_claim": False,
            "completion_claim_allowed": False,
            "do_not_mark_goal_complete": True,
        },
        "geometry": {
            "actual_q_rad": [float(v) for v in q],
            "tcp_site_position_world_m": [float(v) for v in overlay_tcp_position],
            "plane_point_world_m": [float(v) for v in plane_point],
            "expected_plane_normal_world": [float(v) for v in normal],
            "actual_plane_normal_world": [float(v) for v in plane_normal],
            "tip_center_world_m": [float(v) for v in tip_center],
            "tip_center_expected_world_m": [float(v) for v in tip_center_expected],
            "tip_center_local_offset_m_from_tcp": [float(v) for v in tip_center_local_offset],
            "activation_probe_plane_shift_world_m": [
                float(v) for v in (float(activation_probe_penetration_m) * normal)
            ],
        },
        "claim_boundary": {
            "offline_diagnostic_contact_geometry_only": True,
            "live_hardware_accessed_by_this_audit": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "approved_read_only_evidence": False,
            "contact_calibration_claim": False,
            "contact_setup_target_acceptance": False,
            "setup_target_acceptance_claim": False,
            "orientation_gate_acceptance_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "robustness_claim": False,
            "hardware_readiness": False,
            "completion_claim_allowed": False,
            "do_not_mark_goal_complete": True,
        },
        "next_actions": [
            "Use the overlay only for offline diagnostic start-contact simulation experiments.",
            "Do not treat the overlay plane, tip radius, or local offset as accepted contact geometry.",
            "Run contact/setup-target acceptance review before any claim-closing use.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Calibrated Diagnostic Contact Overlay Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Overlay model loads: `{summary['overlay_model_loads']}`",
        f"- Current TCP site on diagnostic plane: `{summary['current_tcp_site_on_diagnostic_plane']}`",
        f"- Contact tip surface tangent to plane: `{summary['contact_tip_surface_tangent_to_plane']}`",
        f"- Seed non-target contact count: `{summary['non_target_contact_count_at_seed']}`",
        f"- Activation probe target contact count: `{summary['activation_probe_target_contact_pair_count']}`",
        f"- Activation probe non-target contact count: `{summary['activation_probe_non_target_contact_count']}`",
        f"- TCP site shift: `{summary['tcp_site_shift_m']}` m",
        f"- Tip surface gap: `{summary['tip_surface_gap_m']}` m",
        f"- Simulation can start from diagnostic overlay: `{summary['simulation_can_start_from_diagnostic_overlay']}`",
        f"- Diagnostic overlay acceptance status: `{summary['diagnostic_overlay_acceptance_status']}`",
        f"- Completion claim allowed: `{summary['completion_claim_allowed']}`",
        "",
        "Interpretation:",
        "",
        "- The generated overlay adds an unaccepted diagnostic plane and tip sphere to the v147 calibrated kinematic seed.",
        "- Existing visual/primitive geoms are collision-masked so the diagnostic plane is reserved for the named tip pair.",
        "- It is a start-contact geometry scaffold for offline simulation only, not contact calibration or setup-target acceptance.",
    ]
    if payload["summary"]["violations"]:
        lines.extend(["", "## Violations", ""])
        lines.extend(f"- {violation}" for violation in payload["summary"]["violations"])
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-config", default=DEFAULT_SOURCE_CONFIG)
    parser.add_argument("--previous-metrics", default=DEFAULT_PREVIOUS_METRICS)
    parser.add_argument("--overlay-mjcf", default=DEFAULT_OVERLAY_MJCF)
    parser.add_argument("--overlay-config", default=DEFAULT_OVERLAY_CONFIG)
    parser.add_argument("--tip-radius-m", type=float, default=DEFAULT_TIP_RADIUS_M)
    parser.add_argument("--plane-tilt-rad-about-y", type=float, default=DEFAULT_PLANE_TILT_RAD_ABOUT_Y)
    parser.add_argument("--normal-world", type=float, nargs=3, default=DEFAULT_NORMAL_WORLD)
    parser.add_argument("--tolerance-m", type=float, default=DEFAULT_TOLERANCE_M)
    parser.add_argument("--activation-probe-penetration-m", type=float, default=DEFAULT_ACTIVATION_PROBE_PENETRATION_M)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--no-write-overlay", action="store_true")
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "calibrated_contact_overlay_after_v147" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    command = ["python3", "scripts/audit_calibrated_contact_overlay_after_v147.py", "--run-id", run_id]
    payload = build_payload(
        source_config_path=resolve(args.source_config),
        previous_metrics_path=resolve(args.previous_metrics),
        overlay_mjcf_path=resolve(args.overlay_mjcf),
        overlay_config_path=resolve(args.overlay_config),
        run_id=run_id,
        tip_radius_m=float(args.tip_radius_m),
        plane_tilt_rad_about_y=float(args.plane_tilt_rad_about_y),
        normal_world=[float(v) for v in args.normal_world],
        tolerance_m=float(args.tolerance_m),
        activation_probe_penetration_m=float(args.activation_probe_penetration_m),
        write_overlay=not args.no_write_overlay,
    )
    payload["output_dir"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=command)
    print(json.dumps(payload["summary"], indent=2))
    return 0 if payload["summary"]["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
