from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest
import yaml

from scripts.audit_calibrated_overlay_force_response_after_v149 import ROOT, build_payload, validate_ladder


CONFIG = ROOT / "configs" / "mujoco_ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.yaml"
PREVIOUS = ROOT / "runs" / "calibrated_contact_overlay_after_v147" / "20260525T223000" / "metrics.yaml"


def test_overlay_force_response_ladder_passes_without_completion_claim() -> None:
    payload = build_payload(
        config_path=CONFIG,
        previous_metrics_path=PREVIOUS,
        run_id="test",
        ladder_m=[0.0, 0.0001, 0.00025, 0.0005, 0.001, 0.0015, 0.002],
        force_tolerance_N=1.0e-9,
        distance_tolerance_m=1.0e-9,
    )
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["force_response_ladder_passed"] is True
    assert summary["clean_target_contact_all_rows"] is True
    assert summary["zero_penetration_force_ok"] is True
    assert summary["positive_penetration_force_positive"] is True
    assert summary["target_force_monotonic_nondecreasing"] is True
    assert summary["positive_target_force_strictly_increasing"] is True
    assert summary["contact_distance_matches_penetration"] is True
    assert summary["force_at_1mm_N"] > 10.0
    assert summary["completion_claim_allowed"] is False
    assert payload["claim_boundary"]["contact_calibration_claim"] is False
    assert payload["claim_boundary"]["hardware_readiness"] is False


def test_overlay_force_response_rejects_previous_acceptance_drift(tmp_path: pathlib.Path) -> None:
    previous = yaml.safe_load(PREVIOUS.read_text())
    previous["summary"]["diagnostic_overlay_acceptance_status"] = "accepted"
    drifted = tmp_path / "previous.yaml"
    drifted.write_text(yaml.safe_dump(previous, sort_keys=False), encoding="utf-8")

    payload = build_payload(
        config_path=CONFIG,
        previous_metrics_path=drifted,
        run_id="test",
        ladder_m=[0.0, 0.001],
        force_tolerance_N=1.0e-9,
        distance_tolerance_m=1.0e-9,
    )

    assert payload["summary"]["audit_passed"] is False
    assert any("accepted contact status" in violation for violation in payload["summary"]["violations"])
    assert payload["summary"]["completion_claim_allowed"] is False


def test_validate_ladder_rejects_unsorted_or_duplicate_values() -> None:
    with pytest.raises(ValueError):
        validate_ladder([0.0, 0.001, 0.0005])
    with pytest.raises(ValueError):
        validate_ladder([0.0, 0.001, 0.001])
    with pytest.raises(ValueError):
        validate_ladder([-0.001])


def test_overlay_force_response_cli_writes_no_alias_metrics(tmp_path: pathlib.Path) -> None:
    out_dir = tmp_path / "force_response"
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_calibrated_overlay_force_response_after_v149.py",
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
