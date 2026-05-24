#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from audit_stage_a_base_z_recovery import write_git_state


DEFAULT_HARDWARE_STATE = pathlib.Path(
    "/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/current_hardware_state.md"
)
DEFAULT_EOAT_NOTE = pathlib.Path(
    "/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/eoat_design/EOAT_TCP_NOTE.md"
)
DEFAULT_EOAT_DIR = pathlib.Path(
    "/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/eoat_design/"
    "v13_ksm8n_receiver_5p3mm_side_window_85mm"
)


def sha256_file(path: pathlib.Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: pathlib.Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        "sha256": sha256_file(path),
    }


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def bool_contains(text: str, needle: str) -> bool:
    return needle.lower() in text.lower()


def regex_float(text: str, pattern: str) -> float | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    return float(match.group(1))


def regex_vector(text: str, pattern: str) -> list[float] | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    return [float(value.strip()) for value in match.group(1).split(",")]


def mjcf_extract(path: pathlib.Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    plane = root.find(".//geom[@name='contact_plane']")
    contact_tip = root.find(".//geom[@name='contact_tip']")
    site = root.find(".//site[@name='tcp_site_unverified_85mm']")
    return {
        "model_name": root.attrib.get("model"),
        "contact_plane_euler": plane.attrib.get("euler") if plane is not None else None,
        "contact_plane_type": plane.attrib.get("type") if plane is not None else None,
        "contact_tip_type": contact_tip.attrib.get("type") if contact_tip is not None else None,
        "contact_tip_pos": [
            float(value) for value in contact_tip.attrib.get("pos", "").split()
        ]
        if contact_tip is not None and contact_tip.attrib.get("pos")
        else None,
        "contact_tip_radius_m": float(contact_tip.attrib["size"])
        if contact_tip is not None and contact_tip.attrib.get("size")
        else None,
        "tcp_site_pos": [float(value) for value in site.attrib.get("pos", "").split()]
        if site is not None and site.attrib.get("pos")
        else None,
    }


def readiness_row(
    *,
    name: str,
    status: str,
    measured: bool,
    constrains_v85_margin: bool,
    evidence: list[str],
    blockers: list[str],
    required_next: list[str],
) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "has_measured_record": bool(measured),
        "constrains_v85_margin": bool(constrains_v85_margin),
        "evidence": evidence,
        "blockers": blockers,
        "required_next": required_next,
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Measured Geometry Readiness Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        "## V85 Margin",
        "",
        f"- Required normal rotation: `{payload['v85_margin']['required_normal_rotation_rad']}` rad",
        f"- Required normal rotation: `{payload['v85_margin']['required_normal_rotation_deg']}` deg",
        f"- Equivalent geometry correction: `{payload['v85_margin']['equivalent_base_z_or_contact_point_um']}` um",
        "",
        "## Readiness Checks",
        "",
        "| check | status | measured record | constrains v85 margin |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in payload["readiness_checks"]:
        lines.append(
            "| `{name}` | `{status}` | `{measured}` | `{constrains}` |".format(
                name=row["name"],
                status=row["status"],
                measured=row["has_measured_record"],
                constrains=row["constrains_v85_margin"],
            )
        )

    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"- Supports accepting v85 margin: `{payload['verdict']['supports_accepting_v85_margin']}`",
            f"- Supports gate relaxation: `{payload['verdict']['supports_gate_relaxation']}`",
            f"- Supports hardware claim: `{payload['verdict']['supports_hardware_claim']}`",
            f"- Supports more Stage B qdot tuning: `{payload['verdict']['supports_more_stage_b_qdot_tuning']}`",
            "",
            "## Required Measurement Checklist",
            "",
        ]
    )
    for item in payload["measurement_checklist"]:
        lines.append(f"- {item}")
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    hardware_path = pathlib.Path(args.hardware_state).resolve()
    eoat_note_path = pathlib.Path(args.eoat_note).resolve()
    eoat_dir = pathlib.Path(args.eoat_dir).resolve()
    verification_path = eoat_dir / "verification.json"
    eoat_readme_path = eoat_dir / "README.md"
    v85_path = (ROOT / args.v85_metrics).resolve()
    config_path = (ROOT / args.contact_config).resolve()

    v85 = load_yaml(v85_path)
    config = load_yaml(config_path)
    mjcf_path = (ROOT / config["ur10e_mujoco"]["mjcf_path"]).resolve()

    hardware_text = read_text(hardware_path)
    eoat_note_text = read_text(eoat_note_path)
    eoat_readme_text = read_text(eoat_readme_path)
    verification = load_json(verification_path)
    mjcf = mjcf_extract(mjcf_path)

    current_tcp_offset = regex_vector(hardware_text, r"TCP offset:\s*`\[([^\]]+)\]`")
    payload_kg = regex_float(hardware_text, r"Payload:\s*`?([0-9.]+)\s*kg")
    direct_tcp_fz_stopped = regex_float(hardware_text, r"Fz mean =\s*(-?[0-9.]+)\s*N")
    direct_tcp_fz_running = regex_float(
        hardware_text, r"program_running`\s*\n\s*still returned `Fz mean =\s*(-?[0-9.]+)\s*N"
    )
    rtde_fz_observed = regex_float(hardware_text, r"`Fz` observed around `?(-?[0-9.]+)\s*N")

    design_contact_point_mm = float(
        verification["derived"]["contact_point_from_flange_face_mm"]
    )
    v85_corrections = v85["equivalent_corrections"]

    source_records = {
        "current_hardware_state": file_record(hardware_path),
        "eoat_tcp_note": file_record(eoat_note_path),
        "eoat_readme": file_record(eoat_readme_path),
        "eoat_verification_json": file_record(verification_path),
        "contact_config": file_record(config_path),
        "contact_mjcf": file_record(mjcf_path),
        "v85_metrics": file_record(v85_path),
    }

    cad_files = [
        {
            "path": str(path),
            "size_bytes": path.stat().st_size,
            "suffix": path.suffix,
        }
        for path in sorted(eoat_dir.iterdir())
        if path.is_file() and path.suffix.lower() in {".step", ".stl"}
    ]

    extracted_facts = {
        "hardware": {
            "current_ur_tcp_offset_m_rad": current_tcp_offset,
            "current_payload_kg": payload_kg,
            "use_ur_default_tcp_configuration_selected": bool_contains(
                hardware_text, "Use UR default TCP Configuration"
            ),
            "set_from_sensor_flange_not_selected": bool_contains(
                hardware_text, "Set from sensor flange` is not selected"
            ),
            "temporary_tcp_not_validated_for_contact": bool_contains(
                hardware_text, "not yet validated for contact experiments"
            ),
            "direct_tcp_daq_fz_mean_stopped_N": direct_tcp_fz_stopped,
            "direct_tcp_daq_fz_mean_program_running_N": direct_tcp_fz_running,
            "rtde_actual_tcp_force_fz_observed_N": rtde_fz_observed,
            "force_source_discrepancy_recorded": direct_tcp_fz_stopped is not None
            and direct_tcp_fz_running is not None
            and rtde_fz_observed is not None,
        },
        "eoat_design": {
            "design_contact_point_from_flange_face_mm": design_contact_point_mm,
            "tcp_on_centerline": bool(verification["derived"]["tcp_on_centerline"]),
            "ksm_placeholder_excluded_from_printable_outputs": bool(
                verification["derived"]["purchased_ksm_placeholder_excluded_from_printable_outputs"]
            ),
            "ksm_assumptions_to_confirm": list(verification["assumptions_to_confirm"]),
            "note_says_design_candidate_not_verified": bool_contains(
                eoat_note_text, "design candidate, not a verified UR10e TCP setting"
            ),
            "note_says_not_mounted_when_prepared": bool_contains(
                eoat_note_text, "had not yet been mounted"
            ),
            "readme_contact_module_purchased_ksm": bool_contains(
                eoat_readme_text, "Contact module: purchased KSM-8N"
            ),
            "readme_contact_point_from_flange_face_mm": regex_float(
                eoat_readme_text, r"Contact point from flange face:\s*([0-9.]+)\s*mm"
            ),
        },
        "simulation": {
            "model_status": config["v1"]["model_status"],
            "tcp_status": config["v1"]["tcp_status"],
            "surface": config["ur10e_mujoco"]["contact"]["surface"],
            "plane_tilt_rad_about_y": float(
                config["ur10e_mujoco"]["contact"]["plane_tilt_rad_about_y"]
            ),
            "expected_normal_world": config["ur10e_mujoco"]["contact"][
                "expected_normal_world"
            ],
            "tcp_guess_m": config["ur10e_mujoco"]["contact"]["tcp_guess_m"],
            "contact_model_convention": config["ur10e_mujoco"]["contact"][
                "contact_model_convention"
            ],
            "contact_tip_sphere_radius_m": float(
                config["ur10e_mujoco"]["contact"]["contact_tip_sphere_radius_m"]
            ),
            "contact_tip_sphere_center_local_m": config["ur10e_mujoco"]["contact"][
                "contact_tip_sphere_center_local_m"
            ],
            "mjcf_extract": mjcf,
        },
    }

    readiness_checks = [
        readiness_row(
            name="mounted_stack_tcp_contact_point",
            status="insufficient_design_only",
            measured=False,
            constrains_v85_margin=False,
            evidence=[
                f"EOAT design candidate contact point = {design_contact_point_mm} mm from design flange face.",
                f"Current UR TCP readback = {current_tcp_offset}; hardware note says this is temporary and not validated for contact.",
                "OnRobot FT setup photo evidence has UR default TCP selected, not sensor flange TCP.",
            ],
            blockers=[
                "No measured flange-to-contact point for the assembled UR10e + OnRobot + EOAT stack.",
                "No measured uncertainty budget comparable to the v85 14.96 um equivalent margin.",
            ],
            required_next=[
                "Measure mounted flange/sensor/tool stack contact point in the robot TCP convention.",
                "Record measurement method, repeatability, datum, sign, and uncertainty.",
            ],
        ),
        readiness_row(
            name="contact_patch_convention",
            status="insufficient_design_assumption",
            measured=False,
            constrains_v85_margin=False,
            evidence=[
                "EOAT verification treats the KSM-8N dimensions as assumptions to confirm.",
                "Printable assembly excludes the purchased KSM placeholder.",
                "Simulation uses a 45 mm sphere behind the TCP site as a contact-point convention variant.",
            ],
            blockers=[
                "No mounted KSM-8N seating verification tied to the actual contact patch.",
                "No measurement of whether the physical contact datum is ball top, sphere center, or another loaded patch.",
            ],
            required_next=[
                "Verify KSM seating, protrusion, loaded contact patch, and centerline alignment after assembly.",
                "Decide and document whether the gate uses contact point, ball center, or another physical datum.",
            ],
        ),
        readiness_row(
            name="plane_contact_normal",
            status="insufficient_analytic_simulation_only",
            measured=False,
            constrains_v85_margin=False,
            evidence=[
                "MuJoCo config uses a single analytic plane tilted 10 deg about y.",
                "Expected normal is taken from config, not a measured robot-base-frame plane normal.",
            ],
            blockers=[
                "No measured plane normal in the robot base frame.",
                "No normal-angle uncertainty budget comparable to the v85 0.03246 deg required correction.",
            ],
            required_next=[
                "Measure plane pose/normal in robot base frame with a repeatable read-only or fixture-based method.",
                "Record normal uncertainty and compare directly to 0.03246 deg.",
            ],
        ),
        readiness_row(
            name="force_source_frame",
            status="unresolved_conflict",
            measured=True,
            constrains_v85_margin=False,
            evidence=[
                f"Direct TCP DAQ stopped-state Fz mean = {direct_tcp_fz_stopped} N.",
                f"Program-running direct TCP DAQ Fz mean = {direct_tcp_fz_running} N.",
                f"RTDE actual_TCP_force Fz was observed around {rtde_fz_observed} N.",
                "Hardware note says direct TCP DAQ and PolyScope/RTDE force values use different zero/reference/compensation until proven otherwise.",
            ],
            blockers=[
                "Force source and frame are not reconciled.",
                "Direct TCP DAQ READFT cannot be used as control truth from the current evidence.",
            ],
            required_next=[
                "Map PolyScope OnRobot variables to RTDE output registers in a no-motion program.",
                "Compare URCap variables, RTDE, and direct TCP DAQ under the same zero/frame state.",
            ],
        ),
        readiness_row(
            name="orientation_gate_semantics",
            status="not_accepted",
            measured=False,
            constrains_v85_margin=False,
            evidence=[
                "V85 shows scoped recovery at larger gates but marks accepted_replacement_gate false.",
                "V69 found full-rotation and force-normal-only errors numerically equal for the audited terminal cases.",
            ],
            blockers=[
                "No accepted definition replacing the current 0.119 rad diagnostic gate.",
                "No calibrated normal/contact geometry supporting a relaxed gate.",
            ],
            required_next=[
                "Define whether the diagnostic gate is force-normal-only or full-frame rotation.",
                "Tie any replacement gate to measured geometry and normal uncertainty.",
            ],
        ),
    ]

    measurement_checklist = [
        "Measure mounted stack TCP/contact point from a named flange/sensor/tool datum.",
        "Measure or verify the physical KSM-8N contact datum and loaded contact patch convention.",
        "Measure the contact plane normal in the robot base frame and record angle uncertainty.",
        "Reconcile OnRobot URCap variables, UR RTDE, and direct TCP DAQ force frames/zeroing without motion.",
        "Define the diagnostic orientation gate semantics and uncertainty budget before relaxing any gate.",
        "Only after the read-only evidence is accepted, update simulation geometry or gate definitions in a separate branch.",
    ]

    answers = [
        {
            "question": "1. Is there a measured mounted-stack TCP/contact point?",
            "answer": "No. Existing records provide a design 85.0 mm candidate and a temporary UR TCP readback, not a measured mounted-stack contact point.",
        },
        {
            "question": "2. Is the 85.0 mm EOAT datum a surface, sphere center, or design-reference point?",
            "answer": "It is a design contact-point candidate from CAD metadata. The actual mounted KSM contact patch/ball datum is not verified.",
        },
        {
            "question": "3. Is the plane/contact normal measured in robot base frame?",
            "answer": "No. The current normal is an analytic MuJoCo 10 deg tilted-plane assumption.",
        },
        {
            "question": "4. Is the force source/frame reconciled?",
            "answer": "No. Existing records show a persistent direct TCP DAQ versus RTDE/PolyScope force-value disagreement around 32 N.",
        },
        {
            "question": "5. Is any existing uncertainty small enough for the v85 correction?",
            "answer": "No accepted measurement uncertainty exists for the 0.03246 deg or 14.96 um v85 correction.",
        },
        {
            "question": "6. What measurement/SOP is required before a gate relaxation or hardware claim?",
            "answer": "Mounted TCP/contact measurement, contact patch convention verification, plane-normal measurement, force-source reconciliation, and accepted orientation-gate semantics.",
        },
        {
            "question": "7. Does this support more Stage B qdot tuning?",
            "answer": "No. The missing evidence is geometry/normal/force-frame readiness, and v85 already showed the hard row has 0.0 qdot saturation.",
        },
    ]

    return {
        "run_source": "v86 measured geometry contact-normal readiness",
        "source_records": source_records,
        "source_cad_files": cad_files,
        "v85_margin": {
            "required_normal_rotation_rad": float(
                v85_corrections["required_normal_rotation_rad"]
            ),
            "required_normal_rotation_deg": float(
                v85_corrections["required_normal_rotation_deg"]
            ),
            "equivalent_base_z_or_contact_point_mm": float(
                v85_corrections["equivalent_base_z_or_contact_point_mm"]
            ),
            "equivalent_base_z_or_contact_point_um": float(
                v85_corrections["equivalent_base_z_or_contact_point_um"]
            ),
            "accepted_replacement_gate": bool(v85["claim_boundary"]["accepted_replacement_gate"]),
            "support_more_stage_b_qdot_tuning": bool(
                v85["support_more_stage_b_qdot_tuning"]
            ),
        },
        "extracted_facts": extracted_facts,
        "readiness_checks": readiness_checks,
        "measurement_checklist": measurement_checklist,
        "v86_objective_answers": answers,
        "verdict": {
            "records_sufficient_for_v85_margin": False,
            "supports_accepting_v85_margin": False,
            "supports_gate_relaxation": False,
            "supports_hardware_claim": False,
            "supports_more_stage_b_qdot_tuning": False,
            "next_step": "read-only measurement/SOP definition before model or gate changes",
        },
        "claim_boundary": {
            "recovery_claim": False,
            "contact_calibration_claim": False,
            "gate_relaxation_claim": False,
            "paper_equivalent_feasibility": False,
            "hardware_readiness": False,
            "real_robot_motion_or_configuration": False,
        },
        "safety": {
            "robot_motion_commanded": False,
            "tcp_payload_urcap_or_onrobot_write": False,
            "hardware_access_mode": "read-only local record inspection",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--v85-metrics",
        default="runs/contact_orientation_calibration_margin/20260524T235723/metrics.yaml",
    )
    parser.add_argument(
        "--hardware-state",
        default=str(DEFAULT_HARDWARE_STATE),
    )
    parser.add_argument(
        "--eoat-note",
        default=str(DEFAULT_EOAT_NOTE),
    )
    parser.add_argument(
        "--eoat-dir",
        default=str(DEFAULT_EOAT_DIR),
    )
    parser.add_argument(
        "--contact-config",
        default="configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml",
    )
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    payload = build_payload(args)
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "measured_geometry_readiness" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
