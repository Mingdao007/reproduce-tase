#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import pathlib
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any

import numpy as np
import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.kinematics import orientation_error_rotvec  # noqa: E402

from scripts.audit_current_real_snapshot_sim_seed_after_v146 import (  # noqa: E402
    rotvec_to_matrix,
)


DEFAULT_SEED = "data/ur10e_real_snapshot_20260525T1641/current_ur10e_sim_seed.yaml"
DEFAULT_URDF = "assets/urdf/ur10e_calibrated_20260525T1641.urdf"
DEFAULT_PREVIOUS = "runs/current_real_snapshot_sim_seed_after_v146/20260525T210000/metrics.yaml"
DEFAULT_POSITION_TOLERANCE_M = 1.0e-4
DEFAULT_ORIENTATION_TOLERANCE_RAD = 1.0e-4
JOINT_ORDER = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


@dataclass(frozen=True)
class JointSpec:
    name: str
    joint_type: str
    parent: str
    child: str
    origin: np.ndarray
    axis: np.ndarray


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


def transform(xyz: list[float] | np.ndarray | None = None, rotation: np.ndarray | None = None) -> np.ndarray:
    matrix = np.eye(4)
    if rotation is not None:
        matrix[:3, :3] = rotation
    if xyz is not None:
        matrix[:3, 3] = np.asarray(xyz, dtype=float)
    return matrix


def rpy_to_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    rz = np.array([[cy, -sy, 0.0], [sy, cy, 0.0], [0.0, 0.0, 1.0]])
    ry = np.array([[cp, 0.0, sp], [0.0, 1.0, 0.0], [-sp, 0.0, cp]])
    rx = np.array([[1.0, 0.0, 0.0], [0.0, cr, -sr], [0.0, sr, cr]])
    return rz @ ry @ rx


def axis_angle_to_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    unit = np.asarray(axis, dtype=float)
    norm = float(np.linalg.norm(unit))
    if norm == 0.0:
        raise ValueError("joint axis has zero norm")
    x, y, z = unit / norm
    c = math.cos(angle)
    s = math.sin(angle)
    one_minus_c = 1.0 - c
    return np.array(
        [
            [c + x * x * one_minus_c, x * y * one_minus_c - z * s, x * z * one_minus_c + y * s],
            [y * x * one_minus_c + z * s, c + y * y * one_minus_c, y * z * one_minus_c - x * s],
            [z * x * one_minus_c - y * s, z * y * one_minus_c + x * s, c + z * z * one_minus_c],
        ],
        dtype=float,
    )


def origin_transform(joint: ET.Element) -> np.ndarray:
    origin = joint.find("origin")
    if origin is None:
        return np.eye(4)
    xyz = [float(value) for value in origin.get("xyz", "0 0 0").split()]
    rpy = [float(value) for value in origin.get("rpy", "0 0 0").split()]
    return transform(xyz, rpy_to_matrix(*rpy))


def parse_urdf_joints(urdf_path: pathlib.Path) -> list[JointSpec]:
    root = ET.parse(urdf_path).getroot()
    joints: list[JointSpec] = []
    for joint in root.findall("joint"):
        parent = joint.find("parent")
        child = joint.find("child")
        if parent is None or child is None:
            continue
        axis_element = joint.find("axis")
        axis = (
            np.asarray([float(value) for value in axis_element.get("xyz", "0 0 1").split()])
            if axis_element is not None
            else np.asarray([0.0, 0.0, 1.0])
        )
        joints.append(
            JointSpec(
                name=str(joint.get("name")),
                joint_type=str(joint.get("type")),
                parent=str(parent.get("link")),
                child=str(child.get("link")),
                origin=origin_transform(joint),
                axis=axis,
            )
        )
    return joints


def compute_frames(joints: list[JointSpec], q_by_joint: dict[str, float]) -> dict[str, np.ndarray]:
    children: dict[str, list[JointSpec]] = {}
    for joint in joints:
        children.setdefault(joint.parent, []).append(joint)
    frames = {"world": np.eye(4)}
    stack = ["world"]
    while stack:
        parent = stack.pop()
        for joint in children.get(parent, []):
            local = joint.origin.copy()
            if joint.joint_type in {"revolute", "continuous"}:
                local = local @ transform(rotation=axis_angle_to_matrix(joint.axis, q_by_joint[joint.name]))
            frames[joint.child] = frames[parent] @ local
            stack.append(joint.child)
    return frames


def pose_error_row(
    *,
    frame_id: str,
    transform_base_frame: np.ndarray,
    real_position: np.ndarray,
    real_rotation: np.ndarray,
) -> dict[str, Any]:
    position = transform_base_frame[:3, 3]
    orientation_error = orientation_error_rotvec(real_rotation, transform_base_frame[:3, :3])
    return {
        "frame_id": frame_id,
        "position_m": [float(value) for value in position],
        "position_error_vector_m": [float(value) for value in position - real_position],
        "position_error_norm_m": float(np.linalg.norm(position - real_position)),
        "orientation_error_rotvec": [float(value) for value in orientation_error],
        "orientation_error_norm_rad": float(np.linalg.norm(orientation_error)),
    }


def build_payload(
    *,
    seed_path: pathlib.Path,
    urdf_path: pathlib.Path,
    previous_metrics_path: pathlib.Path,
    run_id: str,
    position_tolerance_m: float,
    orientation_tolerance_rad: float,
) -> dict[str, Any]:
    violations: list[str] = []
    seed = load_yaml(seed_path)
    previous = load_yaml(previous_metrics_path)
    q = np.asarray(seed["current_rtde_state"]["actual_q_rad"], dtype=float)
    real_pose = np.asarray(seed["current_rtde_state"]["actual_tcp_pose_m_axis_angle"], dtype=float)
    real_position = real_pose[:3]
    real_rotation = rotvec_to_matrix(real_pose[3:])
    tcp_offset = seed["current_rtde_state"]["tcp_offset_m_axis_angle"]
    tcp_offset_z = float(tcp_offset[2])
    q_by_joint = dict(zip(JOINT_ORDER, q))

    if previous.get("summary", {}).get("audit_passed") is not True:
        violations.append("previous v147 seed audit did not pass")
    if previous.get("summary", {}).get("completion_claim_allowed") is not False:
        violations.append("previous v147 seed audit drifted into completion claim")

    joints = parse_urdf_joints(urdf_path)
    frames = compute_frames(joints, q_by_joint)
    missing_frames = [frame for frame in ("base", "flange", "tool0") if frame not in frames]
    if missing_frames:
        violations.append(f"missing URDF frames: {missing_frames}")
    base_to_world = frames["base"]
    base_inv = np.linalg.inv(base_to_world)
    candidate_transforms = {
        "flange": base_inv @ frames["flange"],
        "tool0": base_inv @ frames["tool0"],
        "tool0_plus_live_tcp_offset_z": base_inv @ frames["tool0"] @ transform([0.0, 0.0, tcp_offset_z]),
        "tool0_minus_live_tcp_offset_z": base_inv @ frames["tool0"] @ transform([0.0, 0.0, -tcp_offset_z]),
    }
    rows = [
        pose_error_row(
            frame_id=frame_id,
            transform_base_frame=matrix,
            real_position=real_position,
            real_rotation=real_rotation,
        )
        for frame_id, matrix in candidate_transforms.items()
    ]
    best = min(rows, key=lambda row: row["position_error_norm_m"] + row["orientation_error_norm_rad"])
    calibrated_match = (
        best["frame_id"] == "tool0_plus_live_tcp_offset_z"
        and best["position_error_norm_m"] <= position_tolerance_m
        and best["orientation_error_norm_rad"] <= orientation_tolerance_rad
    )
    if not calibrated_match:
        violations.append("calibrated URDF + live TCP offset does not match RTDE TCP pose within tolerance")

    return {
        "run_source": "calibrated URDF FK snapshot audit after v147 readable-state backup",
        "audit_run_id": run_id,
        "source_files": {
            "repo_seed": rel(seed_path),
            "calibrated_urdf": rel(urdf_path),
            "previous_seed_audit": rel(previous_metrics_path),
        },
        "summary": {
            "audit_passed": not violations,
            "violations": violations,
            "calibrated_urdf_fk_matches_rtde_tcp": calibrated_match,
            "best_frame_id": best["frame_id"],
            "best_position_error_m": best["position_error_norm_m"],
            "best_orientation_error_rad": best["orientation_error_norm_rad"],
            "position_tolerance_m": float(position_tolerance_m),
            "orientation_tolerance_rad": float(orientation_tolerance_rad),
            "tcp_offset_z_m": tcp_offset_z,
            "actual_q_rad": [float(value) for value in q],
            "actual_q_deg": list(seed["current_rtde_state"]["actual_q_deg"]),
            "nominal_mujoco_position_error_m": previous["summary"][
                "nominal_mujoco_to_rtde_tcp_position_error_m"
            ],
            "nominal_mujoco_orientation_error_rad": previous["summary"][
                "nominal_mujoco_to_rtde_tcp_orientation_error_rad"
            ],
            "simulation_geometry_progress": calibrated_match,
            "approved_read_only_evidence_claim": False,
            "contact_setup_target_acceptance_claim": False,
            "orientation_gate_acceptance_claim": False,
            "hardware_readiness_claim": False,
            "completion_claim_allowed": False,
            "do_not_mark_goal_complete": True,
        },
        "candidate_rows": rows,
        "claim_boundary": {
            "offline_simulation_model_alignment_only": True,
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
            "Use the calibrated URDF + live TCP offset frame as the kinematic basis for subsequent offline simulation work.",
            "Do not use this FK match as contact geometry, force-frame, orientation-gate, or robustness acceptance.",
            "The remaining simulation blocker is now contact/setup-target and robustness closure, not raw UR10e kinematics readout.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Calibrated URDF FK Snapshot Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Calibrated URDF FK matches RTDE TCP: `{summary['calibrated_urdf_fk_matches_rtde_tcp']}`",
        f"- Best frame: `{summary['best_frame_id']}`",
        f"- Best position error: `{summary['best_position_error_m']}` m",
        f"- Best orientation error: `{summary['best_orientation_error_rad']}` rad",
        f"- Nominal MuJoCo position error before this: `{summary['nominal_mujoco_position_error_m']}` m",
        f"- Nominal MuJoCo orientation error before this: `{summary['nominal_mujoco_orientation_error_rad']}` rad",
        f"- Completion claim allowed: `{summary['completion_claim_allowed']}`",
        "",
        "| frame | position error m | orientation error rad |",
        "| --- | ---: | ---: |",
    ]
    for row in payload["candidate_rows"]:
        lines.append(
            f"| `{row['frame_id']}` | `{row['position_error_norm_m']}` | `{row['orientation_error_norm_rad']}` |"
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The generated calibrated URDF plus the live TCP offset reproduces the RTDE TCP pose at the backed-up joint state.",
            "- The older nominal MuJoCo primitive remains too approximate for real-state replay.",
            "- This is a kinematic alignment result only, not contact/setup-target acceptance or a hardware-readiness claim.",
        ]
    )
    if payload["summary"]["violations"]:
        lines.extend(["", "## Violations", ""])
        lines.extend(f"- {violation}" for violation in payload["summary"]["violations"])
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default=DEFAULT_SEED)
    parser.add_argument("--urdf", default=DEFAULT_URDF)
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
        else ROOT / "runs" / "calibrated_urdf_fk_snapshot_after_v147" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        seed_path=resolve(args.seed),
        urdf_path=resolve(args.urdf),
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
