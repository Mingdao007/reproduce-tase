from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import mujoco

from scripts.audit_calibrated_mjcf_replay_after_v147 import ROOT, build_payload


CONFIG = ROOT / "configs" / "mujoco_ur10e_calibrated_20260525T1641_tcp_offset.yaml"
MJCF = ROOT / "assets" / "mjcf" / "ur10e_calibrated_20260525T1641_tcp_offset.xml"
PREVIOUS = (
    ROOT
    / "runs"
    / "calibrated_urdf_fk_snapshot_after_v147"
    / "20260525T211000"
    / "metrics.yaml"
)


def test_calibrated_mjcf_loads_in_mujoco() -> None:
    model = mujoco.MjModel.from_xml_path(str(MJCF))

    assert model.nq == 6
    assert model.nv == 6
    assert model.nsite == 1


def test_calibrated_mjcf_replays_rtde_tcp_pose() -> None:
    payload = build_payload(
        config_path=CONFIG,
        previous_metrics_path=PREVIOUS,
        run_id="test",
        position_tolerance_m=1.0e-4,
        orientation_tolerance_rad=1.0e-4,
    )
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["mujoco_model_loads"] is True
    assert summary["calibrated_mjcf_replay_matches_rtde_tcp"] is True
    assert summary["simulation_can_use_calibrated_mjcf_seed"] is True
    assert summary["position_error_m"] < 1.0e-5
    assert summary["orientation_error_rad"] < 1.0e-5
    assert summary["joint_limit_violation_rad"] == 0.0
    assert summary["completion_claim_allowed"] is False
    assert payload["claim_boundary"]["contact_calibration_claim"] is False
    assert payload["claim_boundary"]["hardware_readiness"] is False


def test_calibrated_mjcf_replay_rejects_unrealistic_tolerance() -> None:
    payload = build_payload(
        config_path=CONFIG,
        previous_metrics_path=PREVIOUS,
        run_id="test",
        position_tolerance_m=1.0e-9,
        orientation_tolerance_rad=1.0e-9,
    )

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["calibrated_mjcf_replay_matches_rtde_tcp"] is False
    assert payload["summary"]["completion_claim_allowed"] is False


def test_calibrated_mjcf_replay_cli_writes_no_alias_metrics(tmp_path: pathlib.Path) -> None:
    out_dir = tmp_path / "calibrated_mjcf"
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_calibrated_mjcf_replay_after_v147.py",
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
