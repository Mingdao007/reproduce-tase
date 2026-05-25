from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_current_real_snapshot_sim_seed_after_v146 import (
    ROOT,
    build_payload,
    rotvec_to_matrix,
)


SEED = ROOT / "data" / "ur10e_real_snapshot_20260525T1641" / "current_ur10e_sim_seed.yaml"
CALIBRATION = ROOT / "data" / "ur10e_real_snapshot_20260525T1641" / "ur10e_calibration.yaml"
CONFIG = ROOT / "configs" / "mujoco_ur10e_tilted_plane_tcp_contact_point.yaml"
V146 = ROOT / "runs" / "post_v145_offline_blocker_boundary" / "20260525T200000" / "metrics.yaml"


def test_rotvec_to_matrix_handles_identity_and_pi_z() -> None:
    identity = rotvec_to_matrix([0.0, 0.0, 0.0])
    pi_z = rotvec_to_matrix([0.0, 0.0, 3.141592653589793])

    assert identity.tolist() == [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    assert pi_z[0, 0] < -0.999999
    assert pi_z[1, 1] < -0.999999
    assert pi_z[2, 2] == 1.0


def test_current_real_snapshot_seed_replays_current_q_without_completion_claim() -> None:
    payload = build_payload(
        seed_path=SEED,
        calibration_path=CALIBRATION,
        config_path=CONFIG,
        v146_metrics_path=V146,
        site_name="tcp_site_unverified_85mm",
        run_id="test",
    )
    summary = payload["summary"]
    boundary = payload["claim_boundary"]

    assert summary["audit_passed"] is True
    assert summary["repo_local_sim_seed_available"] is True
    assert summary["repo_local_calibration_available"] is True
    assert summary["offline_simulation_can_continue_from_seed"] is True
    assert summary["current_pose_replay_in_nominal_mujoco_complete"] is True
    assert summary["joint_limit_violation_rad"] == 0.0
    assert summary["calibration_hash"] == "calib_7367377276742883610"
    assert summary["payload_kg"] == 0.44
    assert summary["tcp_offset_z_m"] == 0.12254000000000001
    assert summary["nominal_mujoco_to_rtde_tcp_position_error_m"] > 0.0
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True
    assert boundary["approved_read_only_evidence"] is False
    assert boundary["hardware_readiness"] is False
    assert boundary["strict_paper_equivalent_feasibility"] is False
    assert boundary["robustness_claim"] is False


def test_current_real_snapshot_seed_rejects_evidence_claim_drift(tmp_path: pathlib.Path) -> None:
    seed = yaml.safe_load(SEED.read_text())
    seed["safety_boundary"]["approved_read_only_evidence_claim"] = True
    drifted_seed = tmp_path / "seed.yaml"
    with drifted_seed.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(seed, handle, sort_keys=False)

    payload = build_payload(
        seed_path=drifted_seed,
        calibration_path=CALIBRATION,
        config_path=CONFIG,
        v146_metrics_path=V146,
        site_name="tcp_site_unverified_85mm",
        run_id="test",
    )

    assert payload["summary"]["audit_passed"] is False
    assert any(
        "safety_boundary.approved_read_only_evidence_claim" in violation
        for violation in payload["summary"]["violations"]
    )
    assert payload["summary"]["completion_claim_allowed"] is False


def test_current_real_snapshot_seed_cli_writes_no_alias_metrics(tmp_path: pathlib.Path) -> None:
    out_dir = tmp_path / "snapshot_audit"
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_current_real_snapshot_sim_seed_after_v146.py",
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
