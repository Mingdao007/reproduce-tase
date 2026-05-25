from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_strict_terminal_tradeoff_boundary import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]


def build_current_payload(**overrides):
    kwargs = {
        "strict_terminal_path": ROOT
        / "runs"
        / "strict_terminal_constrained_optimization"
        / "20260525T085000"
        / "metrics.yaml",
        "remaining_blockers_path": ROOT
        / "runs"
        / "remaining_blocker_prioritization"
        / "20260525T072557"
        / "metrics.yaml",
        "claim_boundary_path": ROOT
        / "runs"
        / "paper_platform_claim_boundary"
        / "20260525T103000"
        / "metrics.yaml",
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_current_strict_terminal_tradeoff_boundary_is_preserved() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["strict_terminal_pass_count"] == 0
    assert summary["optimization_case_count"] == 12
    assert summary["best_combined_case_id"] == "xy_force_orientation__best_candidate__slsqp"
    assert summary["best_combined_failed_all_three_scalar_gates"] is True
    assert summary["force_xy_without_orientation_count"] > 0
    assert summary["xy_orientation_without_force_or_contact_count"] > 0
    assert summary["tradeoff_boundary_preserved"] is True
    assert summary["new_optimization_run"] is False
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True

    best = payload["best_combined_row"]
    assert best["failed_criteria"] == [
        "force_error_N",
        "tangential_error_m",
        "orientation_error_rad",
    ]
    assert best["ratios"]["orientation_error_rad"] > 2.0

    force_xy = payload["tradeoff_rows"]["force_xy_without_orientation_best"]
    assert force_xy["target_contact_passed"] is True
    assert force_xy["ratios"]["force_error_N"] <= 1.0
    assert force_xy["ratios"]["tangential_error_m"] <= 1.0
    assert force_xy["ratios"]["orientation_error_rad"] > 1.0

    xy_orientation = payload["tradeoff_rows"]["xy_orientation_without_force_or_contact_best"]
    assert xy_orientation["ratios"]["tangential_error_m"] <= 1.0
    assert xy_orientation["ratios"]["orientation_error_rad"] <= 1.0
    assert (
        xy_orientation["ratios"]["force_error_N"] > 1.0
        or xy_orientation["target_contact_passed"] is False
    )

    boundary = payload["claim_boundary"]
    assert boundary["new_optimization_run"] is False
    assert boundary["strict_paper_equivalent_feasibility"] is False
    assert boundary["hardware_readiness"] is False


def test_tradeoff_boundary_rejects_hidden_strict_terminal_pass(tmp_path) -> None:
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
    assert payload["summary"]["tradeoff_boundary_preserved"] is False
    assert "strict terminal pass rows are present" in payload["summary"]["violations"]
    assert "best combined row no longer fails all three scalar strict gates" in payload[
        "summary"
    ]["violations"]


def test_tradeoff_boundary_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "strict_terminal_tradeoff_boundary"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_strict_terminal_tradeoff_boundary.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_TRADEOFF_BOUNDARY",
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
    assert metrics["summary"]["strict_terminal_pass_count"] == 0
    assert metrics["summary"]["tradeoff_boundary_preserved"] is True
    assert metrics["claim_boundary"]["strict_paper_equivalent_feasibility"] is False
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
