from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_strict_vs_diagnostic_margin_separation import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]
CALIBRATION_MARGIN = (
    ROOT / "runs" / "contact_orientation_calibration_margin" / "20260524T235723" / "metrics.yaml"
)
RELAXATION_BUDGET = (
    ROOT / "runs" / "strict_terminal_relaxation_budget" / "20260525T105000" / "metrics.yaml"
)
COMPLETION_GATE = ROOT / "runs" / "post_v135_completion_gate" / "20260525T123000" / "metrics.yaml"


def build_current_payload(**overrides):
    kwargs = {
        "calibration_margin_path": CALIBRATION_MARGIN,
        "relaxation_budget_path": RELAXATION_BUDGET,
        "completion_gate_path": COMPLETION_GATE,
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_strict_vs_diagnostic_margin_separation_is_nonfinal() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["strict_vs_diagnostic_margin_separation_complete"] is True
    assert summary["source_relaxation_budget_audit_passed"] is True
    assert summary["source_completion_gate_audit_passed"] is True
    assert summary["diagnostic_required_normal_rotation_rad"] == 0.0005664520369604714
    assert summary["strict_orientation_increase_rad"] == 0.0335984782867086
    assert summary["strict_to_diagnostic_orientation_margin_ratio"] > 50.0
    assert summary["minimum_uniform_multiplier"] == 2.11994927622362
    assert summary["minimum_uniform_case_id"] == "xy_force_orientation__best_candidate__slsqp"
    assert summary["minimum_uniform_requires_all_three_scalar_gates"] is True
    assert summary["v85_margin_can_close_strict_orientation"] is False
    assert summary["v85_margin_can_close_strict_uniform_relaxation"] is False
    assert summary["v85_margin_can_close_strict_paper_equivalent_goal"] is False
    assert summary["diagnostic_margin_is_strictly_smaller_than_strict_orientation_gap"] is True
    assert summary["accepted_measurement_noise_budget_exists"] is False
    assert summary["replacement_gate_accepted"] is False
    assert summary["read_only_evidence_required_for_calibration"] is True
    assert summary["approved_read_only_run_count"] == 0
    assert summary["approved_read_only_audit_passed_count"] == 0
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True

    comparison = payload["comparison"]
    assert comparison["scale_separation"]["strict_gap_exceeds_diagnostic_margin"] is True
    assert comparison["scale_separation"]["strict_gap_also_requires_force_and_tangential_relaxation"] is True
    assert comparison["strict_context"]["failed_scalar_criteria"] == [
        "force_error_N",
        "tangential_error_m",
        "orientation_error_rad",
    ]
    assert payload["claim_boundary"]["diagnostic_margin_only"] is True
    assert payload["claim_boundary"]["strict_paper_equivalent_feasibility"] is False
    assert payload["claim_boundary"]["contact_calibration_claim"] is False
    assert payload["claim_boundary"]["hardware_readiness"] is False


def test_margin_separation_rejects_if_diagnostic_margin_could_close_strict(tmp_path) -> None:
    relaxation = yaml.safe_load(RELAXATION_BUDGET.read_text(encoding="utf-8"))
    relaxation["summary"]["strict_orientation_increase_rad"] = 0.0001
    relaxation["summary"]["strict_to_diagnostic_orientation_margin_ratio"] = (
        0.0001 / 0.0005664520369604714
    )
    relaxation["best_uniform_relaxation_row"]["required_increases"]["orientation_error_rad"] = 0.0001
    drifted = tmp_path / "relaxation.yaml"
    drifted.write_text(yaml.safe_dump(relaxation, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(relaxation_budget_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["v85_margin_can_close_strict_orientation"] is True
    assert "v85 diagnostic margin is large enough to close strict orientation" in payload[
        "summary"
    ]["violations"]
    assert any("strict-to-diagnostic orientation ratio" in violation for violation in payload["summary"]["violations"])


def test_margin_separation_rejects_accepted_gate_drift(tmp_path) -> None:
    calibration = yaml.safe_load(CALIBRATION_MARGIN.read_text(encoding="utf-8"))
    calibration["gate_options"]["v83_min_passing_time0p01"]["accepted_as_replacement_gate"] = True
    drifted = tmp_path / "calibration.yaml"
    drifted.write_text(yaml.safe_dump(calibration, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(calibration_margin_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert summary_has(payload, "v85 gate option v83_min_passing_time0p01 is accepted as replacement")
    assert payload["summary"]["replacement_gate_accepted"] is True


def test_margin_separation_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "strict_vs_diagnostic_margin_separation"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_strict_vs_diagnostic_margin_separation.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_MARGIN_SEPARATION",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.strip() == str(out_dir)
    metrics_yaml_text = (out_dir / "metrics.yaml").read_text(encoding="utf-8")
    metrics = yaml.safe_load(metrics_yaml_text)
    metrics_json = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))

    assert metrics_json == metrics
    assert "&id" not in metrics_yaml_text
    assert "*id" not in metrics_yaml_text
    assert metrics["summary"]["audit_passed"] is True
    assert metrics["summary"]["strict_vs_diagnostic_margin_separation_complete"] is True
    assert metrics["summary"]["v85_margin_can_close_strict_paper_equivalent_goal"] is False
    assert metrics["summary"]["completion_claim_allowed"] is False
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()


def summary_has(payload: dict, expected: str) -> bool:
    return expected in payload["summary"]["violations"]
