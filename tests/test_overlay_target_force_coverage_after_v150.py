from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_overlay_target_force_coverage_after_v150 import ROOT, build_payload


CONFIG = ROOT / "configs" / "mujoco_ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.yaml"
PREVIOUS = ROOT / "runs" / "calibrated_overlay_force_response_after_v149" / "20260525T230000" / "metrics.yaml"


def test_overlay_target_force_coverage_identifies_5n_gap_without_completion_claim() -> None:
    payload = build_payload(
        config_path=CONFIG,
        previous_metrics_path=PREVIOUS,
        run_id="test",
        target_force_N=5.0,
        scan_m=[0.0, 1.0e-12, 1.0e-10, 1.0e-8, 1.0e-6, 1.0e-4],
        force_tolerance_N=0.25,
    )
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["clean_target_contact_all_rows"] is True
    assert summary["target_force_reachable_in_scan"] is False
    assert summary["coverage_gap_identified"] is True
    assert summary["minimum_positive_force_N"] > 7.0
    assert summary["best_force_N"] == 7.136494172695263
    assert summary["best_abs_error_N"] > 2.0
    assert summary["completion_claim_allowed"] is False
    assert payload["claim_boundary"]["contact_calibration_claim"] is False
    assert payload["claim_boundary"]["hardware_readiness"] is False


def test_overlay_target_force_coverage_rejects_previous_completion_drift(tmp_path: pathlib.Path) -> None:
    previous = yaml.safe_load(PREVIOUS.read_text())
    previous["summary"]["completion_claim_allowed"] = True
    drifted = tmp_path / "previous.yaml"
    drifted.write_text(yaml.safe_dump(previous, sort_keys=False), encoding="utf-8")

    payload = build_payload(
        config_path=CONFIG,
        previous_metrics_path=drifted,
        run_id="test",
        target_force_N=5.0,
        scan_m=[0.0, 1.0e-12],
        force_tolerance_N=0.25,
    )

    assert payload["summary"]["audit_passed"] is False
    assert any("completion claim" in violation for violation in payload["summary"]["violations"])
    assert payload["summary"]["completion_claim_allowed"] is False


def test_overlay_target_force_coverage_flags_unexpected_target_reach() -> None:
    payload = build_payload(
        config_path=CONFIG,
        previous_metrics_path=PREVIOUS,
        run_id="test",
        target_force_N=7.136494172695263,
        scan_m=[0.0, 1.0e-12],
        force_tolerance_N=0.25,
    )

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["target_force_reachable_in_scan"] is True
    assert payload["summary"]["completion_claim_allowed"] is False


def test_overlay_target_force_coverage_cli_writes_no_alias_metrics(tmp_path: pathlib.Path) -> None:
    out_dir = tmp_path / "coverage"
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_overlay_target_force_coverage_after_v150.py",
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
