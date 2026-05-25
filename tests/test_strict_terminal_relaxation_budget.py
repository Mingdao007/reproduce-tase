from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_strict_terminal_relaxation_budget import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]


def build_current_payload(**overrides):
    kwargs = {
        "strict_terminal_path": ROOT
        / "runs"
        / "strict_terminal_constrained_optimization"
        / "20260525T085000"
        / "metrics.yaml",
        "tradeoff_boundary_path": ROOT
        / "runs"
        / "strict_terminal_tradeoff_boundary"
        / "20260525T104000"
        / "metrics.yaml",
        "calibration_margin_path": ROOT
        / "runs"
        / "contact_orientation_calibration_margin"
        / "20260524T235723"
        / "metrics.yaml",
        "remaining_blockers_path": ROOT
        / "runs"
        / "remaining_blocker_prioritization"
        / "20260525T072557"
        / "metrics.yaml",
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_current_strict_terminal_relaxation_budget_is_nonfinal() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["strict_terminal_pass_count"] == 0
    assert summary["optimization_case_count"] == 12
    assert summary["eligible_scalar_relaxation_row_count"] == 9
    assert summary["minimum_uniform_case_id"] == "xy_force_orientation__best_candidate__slsqp"
    assert summary["minimum_uniform_multiplier"] == 2.11994927622362
    assert summary["minimum_uniform_requires_all_three_scalar_gates"] is True
    assert summary["orientation_only_relaxation_case_id"] == "xy_force__best_candidate__l-bfgs-b"
    assert summary["orientation_only_multiplier"] == 4.899002392744376
    assert summary["contactless_xy_orientation_row_count"] == 2
    assert summary["strict_to_diagnostic_orientation_margin_ratio"] > 50.0
    assert summary["relaxation_budget_acceptance_allowed"] is False
    assert summary["new_optimization_run"] is False
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True

    uniform = payload["best_uniform_relaxation_row"]
    assert set(uniform["failed_scalar_criteria"]) == {
        "force_error_N",
        "tangential_error_m",
        "orientation_error_rad",
    }
    assert uniform["required_multipliers"]["force_error_N"] > 1.0
    assert uniform["required_multipliers"]["tangential_error_m"] > 1.0
    assert uniform["required_multipliers"]["orientation_error_rad"] > 2.0

    orientation = payload["orientation_only_relaxation_row"]
    assert orientation["failed_scalar_criteria"] == ["orientation_error_rad"]
    assert orientation["required_multipliers"]["force_error_N"] == 1.0
    assert orientation["required_multipliers"]["tangential_error_m"] == 1.0
    assert orientation["required_multipliers"]["orientation_error_rad"] > 4.0

    boundary = payload["claim_boundary"]
    assert boundary["strict_terminal_relaxation_accepted"] is False
    assert boundary["strict_paper_equivalent_feasibility"] is False
    assert boundary["hardware_readiness"] is False


def test_relaxation_budget_rejects_hidden_strict_pass(tmp_path) -> None:
    strict = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "strict_terminal_constrained_optimization"
            / "20260525T085000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    row = strict["optimization_rows"][0]
    for criterion in ["force_error_N", "tangential_error_m", "orientation_error_rad"]:
        row["terminal_ratios"][criterion] = 0.5
        row["strict_terminal_gate"]["criteria"][criterion]["passed"] = True
        row["strict_terminal_gate"]["criteria"][criterion]["ratio"] = 0.5
    row["strict_terminal_gate"]["passed"] = True
    row["strict_terminal_gate"]["failed_criteria"] = []
    row["strict_terminal_gate"]["max_gate_ratio"] = 0.5
    strict["summary"]["strict_terminal_pass_count"] = 1
    drifted = tmp_path / "strict.yaml"
    drifted.write_text(yaml.safe_dump(strict, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(strict_terminal_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["strict_terminal_pass_count"] == 1
    assert "strict terminal pass rows are present" in payload["summary"]["violations"]
    assert "minimum scalar relaxation budget does not preserve strict failure" in payload[
        "summary"
    ]["violations"]


def test_relaxation_budget_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "strict_terminal_relaxation_budget"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_strict_terminal_relaxation_budget.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_RELAXATION_BUDGET",
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
    assert metrics["summary"]["relaxation_budget_acceptance_allowed"] is False
    assert metrics["claim_boundary"]["strict_terminal_relaxation_accepted"] is False
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
