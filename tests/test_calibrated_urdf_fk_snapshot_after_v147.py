from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_calibrated_urdf_fk_snapshot_after_v147 import (
    ROOT,
    build_payload,
    compute_frames,
    parse_urdf_joints,
)


SEED = ROOT / "data" / "ur10e_real_snapshot_20260525T1641" / "current_ur10e_sim_seed.yaml"
URDF = ROOT / "assets" / "urdf" / "ur10e_calibrated_20260525T1641.urdf"
PREVIOUS = (
    ROOT
    / "runs"
    / "current_real_snapshot_sim_seed_after_v146"
    / "20260525T210000"
    / "metrics.yaml"
)


def test_parse_calibrated_urdf_contains_real_calibration_hash_and_frames() -> None:
    text = URDF.read_text()
    joints = parse_urdf_joints(URDF)
    joint_names = {joint.name for joint in joints}

    assert "calib_7367377276742883610" in text
    assert {"shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint"}.issubset(joint_names)
    assert {"wrist_1_joint", "wrist_2_joint", "wrist_3_joint"}.issubset(joint_names)


def test_compute_frames_reaches_base_flange_and_tool0() -> None:
    seed = yaml.safe_load(SEED.read_text())
    q = seed["current_rtde_state"]["actual_q_rad"]
    q_by_joint = dict(
        zip(
            [
                "shoulder_pan_joint",
                "shoulder_lift_joint",
                "elbow_joint",
                "wrist_1_joint",
                "wrist_2_joint",
                "wrist_3_joint",
            ],
            q,
        )
    )

    frames = compute_frames(parse_urdf_joints(URDF), q_by_joint)

    assert "base" in frames
    assert "flange" in frames
    assert "tool0" in frames


def test_calibrated_urdf_fk_matches_rtde_tcp_with_live_tcp_offset() -> None:
    payload = build_payload(
        seed_path=SEED,
        urdf_path=URDF,
        previous_metrics_path=PREVIOUS,
        run_id="test",
        position_tolerance_m=1.0e-4,
        orientation_tolerance_rad=1.0e-4,
    )
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["calibrated_urdf_fk_matches_rtde_tcp"] is True
    assert summary["best_frame_id"] == "tool0_plus_live_tcp_offset_z"
    assert summary["best_position_error_m"] < 1.0e-5
    assert summary["best_orientation_error_rad"] < 1.0e-5
    assert summary["nominal_mujoco_position_error_m"] > 1.0
    assert summary["simulation_geometry_progress"] is True
    assert summary["completion_claim_allowed"] is False
    assert payload["claim_boundary"]["approved_read_only_evidence"] is False
    assert payload["claim_boundary"]["hardware_readiness"] is False


def test_calibrated_urdf_fk_rejects_unrealistic_tolerance() -> None:
    payload = build_payload(
        seed_path=SEED,
        urdf_path=URDF,
        previous_metrics_path=PREVIOUS,
        run_id="test",
        position_tolerance_m=1.0e-9,
        orientation_tolerance_rad=1.0e-9,
    )

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["calibrated_urdf_fk_matches_rtde_tcp"] is False
    assert payload["summary"]["completion_claim_allowed"] is False


def test_calibrated_urdf_fk_cli_writes_no_alias_metrics(tmp_path: pathlib.Path) -> None:
    out_dir = tmp_path / "calibrated_fk"
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_calibrated_urdf_fk_snapshot_after_v147.py",
            "--run-id",
            "test",
            "--output-dir",
            str(out_dir),
        ],
        cwd=ROOT,
        check=True,
    )

    metrics_text = (out_dir / "metrics.yaml").read_text()
    metrics_json = json.loads((out_dir / "metrics.json").read_text())

    assert "&id" not in metrics_text
    assert "*id" not in metrics_text
    assert metrics_json["summary"]["audit_passed"] is True
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
