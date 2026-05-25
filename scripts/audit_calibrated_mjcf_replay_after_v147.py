#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Any

import mujoco
import numpy as np
import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.audit_current_real_snapshot_sim_seed_after_v146 import rotvec_to_matrix  # noqa: E402
from tase_repro.kinematics import (  # noqa: E402
    joint_ranges,
    load_model,
    make_data,
    orientation_error_rotvec,
    set_qpos,
    site_position,
    site_rotation_matrix,
)


DEFAULT_CONFIG = "configs/mujoco_ur10e_calibrated_20260525T1641_tcp_offset.yaml"
DEFAULT_PREVIOUS = "runs/calibrated_urdf_fk_snapshot_after_v147/20260525T211000/metrics.yaml"
DEFAULT_POSITION_TOLERANCE_M = 1.0e-4
DEFAULT_ORIENTATION_TOLERANCE_RAD = 1.0e-4


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


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
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


def max_joint_limit_violation(q: np.ndarray, q_min: np.ndarray, q_max: np.ndarray) -> float:
    lower = np.maximum(q_min - q, 0.0)
    upper = np.maximum(q - q_max, 0.0)
    return float(np.max(lower + upper))


def build_payload(
    *,
    config_path: pathlib.Path,
    previous_metrics_path: pathlib.Path,
    run_id: str,
    position_tolerance_m: float,
    orientation_tolerance_rad: float,
) -> dict[str, Any]:
    violations: list[str] = []
    config = load_yaml(config_path)
    previous = load_yaml(previous_metrics_path)
    seed_path = resolve(config["ur10e_mujoco"]["source_seed_path"])
    seed = load_yaml(seed_path)
    q = np.asarray(seed["current_rtde_state"]["actual_q_rad"], dtype=float)
    real_pose = np.asarray(seed["current_rtde_state"]["actual_tcp_pose_m_axis_angle"], dtype=float)
    model_path = resolve(config["ur10e_mujoco"]["mjcf_path"])
    site_name = str(config["ur10e_mujoco"]["tcp_site"])

    if previous.get("summary", {}).get("calibrated_urdf_fk_matches_rtde_tcp") is not True:
        violations.append("previous calibrated URDF FK audit did not pass")
    if previous.get("summary", {}).get("completion_claim_allowed") is not False:
        violations.append("previous calibrated URDF FK audit drifted into completion claim")

    model = load_model(model_path)
    data = make_data(model)
    q_min, q_max = joint_ranges(model)
    set_qpos(model, data, q)
    sim_position = site_position(model, data, site_name)
    sim_rotation = site_rotation_matrix(model, data, site_name)
    real_rotation = rotvec_to_matrix(real_pose[3:])
    position_error = sim_position - real_pose[:3]
    orientation_error = orientation_error_rotvec(real_rotation, sim_rotation)
    position_error_norm = float(np.linalg.norm(position_error))
    orientation_error_norm = float(np.linalg.norm(orientation_error))
    joint_limit_violation = max_joint_limit_violation(q, q_min, q_max)
    replay_matches = (
        position_error_norm <= position_tolerance_m
        and orientation_error_norm <= orientation_tolerance_rad
        and joint_limit_violation == 0.0
    )
    if not replay_matches:
        violations.append("calibrated MJCF TCP site does not replay RTDE TCP pose within tolerance")

    return {
        "run_source": "calibrated MuJoCo MJCF replay audit after v147",
        "audit_run_id": run_id,
        "source_files": {
            "config": rel(config_path),
            "mjcf": rel(model_path),
            "seed": rel(seed_path),
            "previous_calibrated_urdf_fk": rel(previous_metrics_path),
        },
        "summary": {
            "audit_passed": not violations,
            "violations": violations,
            "mujoco_model_loads": True,
            "model_nq": int(model.nq),
            "model_nv": int(model.nv),
            "model_nbody": int(model.nbody),
            "model_nsite": int(model.nsite),
            "calibrated_mjcf_replay_matches_rtde_tcp": replay_matches,
            "position_error_m": position_error_norm,
            "orientation_error_rad": orientation_error_norm,
            "joint_limit_violation_rad": joint_limit_violation,
            "position_tolerance_m": float(position_tolerance_m),
            "orientation_tolerance_rad": float(orientation_tolerance_rad),
            "site_name": site_name,
            "tcp_offset_z_m": float(config["ur10e_mujoco"]["tcp_offset_m_axis_angle"][2]),
            "payload_kg": float(config["ur10e_mujoco"]["payload_kg"]),
            "simulation_can_use_calibrated_mjcf_seed": replay_matches,
            "approved_read_only_evidence_claim": False,
            "contact_setup_target_acceptance_claim": False,
            "orientation_gate_acceptance_claim": False,
            "hardware_readiness_claim": False,
            "completion_claim_allowed": False,
            "do_not_mark_goal_complete": True,
        },
        "replay": {
            "actual_q_rad": [float(value) for value in q],
            "actual_q_deg": list(seed["current_rtde_state"]["actual_q_deg"]),
            "sim_tcp_position_m": [float(value) for value in sim_position],
            "rtde_tcp_position_m": [float(value) for value in real_pose[:3]],
            "position_error_vector_m": [float(value) for value in position_error],
            "orientation_error_rotvec": [float(value) for value in orientation_error],
        },
        "claim_boundary": {
            "offline_mujoco_kinematic_replay_only": True,
            "live_hardware_accessed_by_this_audit": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "approved_read_only_evidence": False,
            "contact_calibration_claim": False,
            "setup_target_acceptance_claim": False,
            "orientation_gate_acceptance_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "robustness_claim": False,
            "hardware_readiness": False,
            "completion_claim_allowed": False,
            "do_not_mark_goal_complete": True,
        },
        "next_actions": [
            "Use this calibrated MJCF for the next offline simulation seed instead of the old nominal primitive.",
            "Add contact plane/contact patch only after the contact/setup-target convention is accepted.",
            "Keep strict feasibility and robustness labels non-final until contact/gate dependencies are closed.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Calibrated MJCF Replay Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- MuJoCo model loads: `{summary['mujoco_model_loads']}`",
        f"- Calibrated MJCF replay matches RTDE TCP: `{summary['calibrated_mjcf_replay_matches_rtde_tcp']}`",
        f"- Position error: `{summary['position_error_m']}` m",
        f"- Orientation error: `{summary['orientation_error_rad']}` rad",
        f"- Simulation can use calibrated MJCF seed: `{summary['simulation_can_use_calibrated_mjcf_seed']}`",
        f"- Completion claim allowed: `{summary['completion_claim_allowed']}`",
        "",
        "Interpretation:",
        "",
        "- The simplified calibrated MJCF loads in MuJoCo and reproduces the backed-up RTDE TCP pose.",
        "- The model is kinematic seed infrastructure only; it intentionally does not define contact plane, contact patch, or force-source truth.",
    ]
    if payload["summary"]["violations"]:
        lines.extend(["", "## Violations", ""])
        lines.extend(f"- {violation}" for violation in payload["summary"]["violations"])
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--previous-metrics", default=DEFAULT_PREVIOUS)
    parser.add_argument("--position-tolerance-m", type=float, default=DEFAULT_POSITION_TOLERANCE_M)
    parser.add_argument("--orientation-tolerance-rad", type=float, default=DEFAULT_ORIENTATION_TOLERANCE_RAD)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "calibrated_mjcf_replay_after_v147" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        config_path=resolve(args.config),
        previous_metrics_path=resolve(args.previous_metrics),
        run_id=run_id,
        position_tolerance_m=float(args.position_tolerance_m),
        orientation_tolerance_rad=float(args.orientation_tolerance_rad),
    )
    payload["output_dir"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0 if payload["summary"]["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
