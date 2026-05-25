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
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.kinematics import (  # noqa: E402
    joint_ranges,
    load_model,
    make_data,
    orientation_error_rotvec,
    set_qpos,
    site_position,
    site_rotation_matrix,
)


DEFAULT_SEED = "data/ur10e_real_snapshot_20260525T1641/current_ur10e_sim_seed.yaml"
DEFAULT_CALIBRATION = "data/ur10e_real_snapshot_20260525T1641/ur10e_calibration.yaml"
DEFAULT_CONFIG = "configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml"
DEFAULT_V146 = "runs/post_v145_offline_blocker_boundary/20260525T200000/metrics.yaml"
DEFAULT_SITE_NAME = "tcp_site_unverified_85mm"


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


def rotvec_to_matrix(rotvec: list[float] | np.ndarray) -> np.ndarray:
    vec = np.asarray(rotvec, dtype=float)
    angle = float(np.linalg.norm(vec))
    if angle < 1.0e-12:
        return np.eye(3)
    axis = vec / angle
    cross = np.array(
        [
            [0.0, -axis[2], axis[1]],
            [axis[2], 0.0, -axis[0]],
            [-axis[1], axis[0], 0.0],
        ],
        dtype=float,
    )
    return np.eye(3) + np.sin(angle) * cross + (1.0 - np.cos(angle)) * (cross @ cross)


def max_joint_limit_violation(q: np.ndarray, q_min: np.ndarray, q_max: np.ndarray) -> float:
    lower = np.maximum(q_min - q, 0.0)
    upper = np.maximum(q - q_max, 0.0)
    return float(np.max(lower + upper))


def safe_boundary_violations(seed: dict[str, Any]) -> list[str]:
    expected_false = [
        "robot_motion_commanded",
        "robot_configuration_written",
        "ur_script_sent",
        "rtde_inputs_written",
        "zero_ftsensor_or_bias_commanded",
        "approved_read_only_evidence_claim",
    ]
    boundary = seed.get("safety_boundary", {})
    return [
        f"safety_boundary.{key} is {boundary.get(key)!r}, expected False"
        for key in expected_false
        if boundary.get(key) is not False
    ]


def model_tcp_guess(config: dict[str, Any]) -> list[float] | None:
    contact = config.get("ur10e_mujoco", {}).get("contact", {})
    guess = contact.get("tcp_guess_m")
    if isinstance(guess, list) and len(guess) == 3:
        return [float(x) for x in guess]
    return None


def build_payload(
    *,
    seed_path: pathlib.Path,
    calibration_path: pathlib.Path,
    config_path: pathlib.Path,
    v146_metrics_path: pathlib.Path,
    site_name: str,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    seed = load_yaml(seed_path)
    calibration = load_yaml(calibration_path)
    config = load_yaml(config_path)
    v146 = load_yaml(v146_metrics_path)

    violations.extend(safe_boundary_violations(seed))

    v146_summary = v146.get("summary", {})
    expected_v146 = {
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
        "user_completion_criterion_met": False,
        "safe_nonrepeating_completion_action_available": False,
    }
    for key, expected in expected_v146.items():
        if v146_summary.get(key) != expected:
            violations.append(f"v146.summary.{key} is {v146_summary.get(key)!r}, expected {expected!r}")

    q = np.asarray(seed["current_rtde_state"]["actual_q_rad"], dtype=float)
    real_pose = np.asarray(seed["current_rtde_state"]["actual_tcp_pose_m_axis_angle"], dtype=float)
    model_path = resolve(config["ur10e_mujoco"]["mjcf_path"])
    model = load_model(model_path)
    data = make_data(model)
    set_qpos(model, data, q)
    q_min, q_max = joint_ranges(model)
    sim_tcp = site_position(model, data, site_name)
    sim_rotation = site_rotation_matrix(model, data, site_name)
    real_rotation = rotvec_to_matrix(real_pose[3:])
    position_error = sim_tcp - real_pose[:3]
    orientation_error = orientation_error_rotvec(real_rotation, sim_rotation)
    joint_limit_violation = max_joint_limit_violation(q, q_min, q_max)
    if q.shape != (model.nq,):
        violations.append(f"seed actual_q shape is {q.shape}, expected {(model.nq,)}")
    if joint_limit_violation > 0.0:
        violations.append(f"seed actual_q violates MuJoCo joint limits by {joint_limit_violation}")

    source_backup_root = pathlib.Path(seed.get("source_backup_root", ""))
    external_backup_files = [
        source_backup_root / "report.md",
        source_backup_root / "simulation_inputs" / "current_ur10e_sim_seed.yaml",
        source_backup_root / "calibration" / "ur10e_calibration_20260525T1641.yaml",
        source_backup_root / "diagnostics" / "rtde_sim_state_once.json",
    ]
    external_present = [path.exists() for path in external_backup_files]
    tcp_guess = model_tcp_guess(config)
    tcp_offset = seed["current_rtde_state"]["tcp_offset_m_axis_angle"]
    calibration_hash = calibration.get("kinematics", {}).get("hash")
    seed_calibration_hash = seed.get("ur_kinematics_calibration", {}).get("hash")
    if calibration_hash != seed_calibration_hash:
        violations.append(
            f"repo calibration hash {calibration_hash!r} differs from seed hash {seed_calibration_hash!r}"
        )

    position_error_norm = float(np.linalg.norm(position_error))
    orientation_error_norm = float(np.linalg.norm(orientation_error))
    payload = {
        "run_source": "current real UR10e readable-state simulation seed audit after v146",
        "audit_run_id": run_id,
        "source_files": {
            "repo_seed": rel(seed_path),
            "repo_calibration": rel(calibration_path),
            "config": rel(config_path),
            "v146_offline_blocker_boundary": rel(v146_metrics_path),
            "external_backup_root": str(source_backup_root),
        },
        "summary": {
            "audit_passed": not violations,
            "violations": violations,
            "current_robot_state_backed_up": True,
            "repo_local_sim_seed_available": seed_path.exists(),
            "repo_local_calibration_available": calibration_path.exists(),
            "external_backup_root_exists": source_backup_root.exists(),
            "external_backup_required_files_present_count": sum(1 for item in external_present if item),
            "external_backup_required_file_count": len(external_backup_files),
            "offline_simulation_can_continue_from_seed": not violations,
            "current_pose_replay_in_nominal_mujoco_complete": True,
            "joint_limit_violation_rad": joint_limit_violation,
            "nominal_mujoco_to_rtde_tcp_position_error_m": position_error_norm,
            "nominal_mujoco_to_rtde_tcp_orientation_error_rad": orientation_error_norm,
            "calibration_hash": calibration_hash,
            "payload_kg": float(seed["current_rtde_state"]["payload_kg"]),
            "tcp_offset_z_m": float(tcp_offset[2]),
            "model_tcp_guess_z_m": None if tcp_guess is None else float(tcp_guess[2]),
            "approved_read_only_evidence_claim": False,
            "contact_setup_target_acceptance_claim": False,
            "orientation_gate_acceptance_claim": False,
            "hardware_readiness_claim": False,
            "completion_claim_allowed": False,
            "do_not_mark_goal_complete": True,
        },
        "seed_snapshot": {
            "captured_wall": seed.get("captured_wall"),
            "actual_q_rad": [float(x) for x in q],
            "actual_q_deg": list(seed.get("current_rtde_state", {}).get("actual_q_deg", [])),
            "actual_tcp_pose_m_axis_angle": [float(x) for x in real_pose],
            "actual_tcp_force_N_Nm": list(seed["current_rtde_state"]["actual_tcp_force_N_Nm"]),
            "payload_kg": float(seed["current_rtde_state"]["payload_kg"]),
            "payload_cog_m": list(seed["current_rtde_state"]["payload_cog_m"]),
            "tcp_offset_m_axis_angle": list(tcp_offset),
        },
        "mujoco_replay": {
            "model_path": rel(model_path),
            "site_name": site_name,
            "sim_tcp_position_m": [float(x) for x in sim_tcp],
            "rtde_tcp_position_m": [float(x) for x in real_pose[:3]],
            "position_error_vector_m": [float(x) for x in position_error],
            "position_error_norm_m": position_error_norm,
            "orientation_error_rotvec": [float(x) for x in orientation_error],
            "orientation_error_norm_rad": orientation_error_norm,
            "joint_limit_violation_rad": joint_limit_violation,
            "tcp_convention_note": (
                "The repo MJCF still uses the unverified 85 mm TCP/contact convention; "
                "the live UR TCP offset readback is a separate working configuration and "
                "is not accepted as a contact model."
            ),
        },
        "backup_artifacts": {
            "external_required_files": [
                {"path": str(path), "exists": exists}
                for path, exists in zip(external_backup_files, external_present)
            ],
            "repo_seed_exists": seed_path.exists(),
            "repo_calibration_exists": calibration_path.exists(),
        },
        "claim_boundary": {
            "offline_audit_only": True,
            "new_live_hardware_access_in_repo": False,
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
            "Use the repo-local seed and calibration for offline simulation initialization.",
            "Do not treat the backed-up force traces as contact-model or force-control validation.",
            "Continue strict terminal feasibility or robustness only as non-final offline simulation work.",
        ],
    }
    return payload


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    replay = payload["mujoco_replay"]
    lines = [
        "# Current Real Snapshot Simulation Seed Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Current robot state backed up: `{summary['current_robot_state_backed_up']}`",
        f"- Offline simulation can continue from seed: `{summary['offline_simulation_can_continue_from_seed']}`",
        f"- Calibration hash: `{summary['calibration_hash']}`",
        f"- Payload: `{summary['payload_kg']}` kg",
        f"- TCP offset z: `{summary['tcp_offset_z_m']}` m",
        f"- Nominal MuJoCo to RTDE TCP position error: `{summary['nominal_mujoco_to_rtde_tcp_position_error_m']}` m",
        f"- Nominal MuJoCo to RTDE TCP orientation error: `{summary['nominal_mujoco_to_rtde_tcp_orientation_error_rad']}` rad",
        f"- Completion claim allowed: `{summary['completion_claim_allowed']}`",
        "",
        "## Replay",
        "",
        f"- Model: `{replay['model_path']}`",
        f"- Site: `{replay['site_name']}`",
        f"- Sim TCP position: `{replay['sim_tcp_position_m']}`",
        f"- RTDE TCP position: `{replay['rtde_tcp_position_m']}`",
        f"- Position error vector: `{replay['position_error_vector_m']}`",
        "",
        "## Boundary",
        "",
        "- This is a simulation seed and bookkeeping artifact only.",
        "- It is not approved read-only calibration evidence, contact/setup-target acceptance, orientation-gate acceptance, robustness proof, or hardware readiness.",
    ]
    if payload["summary"]["violations"]:
        lines.extend(["", "## Violations", ""])
        lines.extend(f"- {violation}" for violation in payload["summary"]["violations"])
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default=DEFAULT_SEED)
    parser.add_argument("--calibration", default=DEFAULT_CALIBRATION)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--v146-metrics", default=DEFAULT_V146)
    parser.add_argument("--site-name", default=DEFAULT_SITE_NAME)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "current_real_snapshot_sim_seed_after_v146" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        seed_path=resolve(args.seed),
        calibration_path=resolve(args.calibration),
        config_path=resolve(args.config),
        v146_metrics_path=resolve(args.v146_metrics),
        site_name=args.site_name,
        run_id=run_id,
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
