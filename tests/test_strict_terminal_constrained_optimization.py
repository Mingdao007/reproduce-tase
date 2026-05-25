from __future__ import annotations

import numpy as np

from scripts.audit_strict_terminal_constrained_optimization import (
    smooth_minimax_objective,
    strict_terminal_thresholds,
    summarize_rows,
    terminal_gate,
)


ACCEPTANCE = {
    "strict_setup_terminal_gate": {
        "max_final_tangential_error_m": 0.002,
        "max_final_orientation_error_rad": 0.03,
        "max_tail_mean_abs_force_error_N": 0.25,
        "max_joint_limit_violation_rad": 1.0e-9,
    }
}


def _metrics(
    *,
    force: float = 0.1,
    xy: float = 0.001,
    orient: float = 0.01,
    contact: int = 1,
) -> dict:
    return {
        "force_error_N": force,
        "tangential_error_m": xy,
        "orientation_error_rad": orient,
        "target_contact_count": contact,
        "joint_limit_violation_rad": 0.0,
    }


def _row(case_id: str, gate: dict, metrics: dict, *, success: bool = True) -> dict:
    return {
        "case_id": case_id,
        "optimizer": {"success": success},
        "terminal_metrics": metrics,
        "strict_terminal_gate": gate,
    }


def test_strict_terminal_thresholds_maps_acceptance_gate_names() -> None:
    thresholds = strict_terminal_thresholds(ACCEPTANCE)

    assert thresholds == {
        "max_force_error_N": 0.25,
        "max_tangential_error_m": 0.002,
        "max_orientation_error_rad": 0.03,
        "min_target_contact_count": 1.0,
        "max_joint_limit_violation_rad": 1.0e-9,
    }


def test_terminal_gate_reports_ratios_and_contact_failure() -> None:
    thresholds = strict_terminal_thresholds(ACCEPTANCE)

    gate = terminal_gate(_metrics(xy=0.003, contact=0), thresholds)

    assert gate["passed"] is False
    assert gate["failed_criteria"] == ["tangential_error_m", "target_contact_count"]
    assert gate["criteria"]["tangential_error_m"]["ratio"] == 1.5
    assert gate["max_gate_ratio"] == float("inf")


def test_smooth_minimax_objective_adds_no_contact_penalty() -> None:
    ratios = np.array([1.0, 2.0, 3.0])

    contact_score = smooth_minimax_objective(
        ratios,
        target_contact_count=1,
        power=4.0,
        no_contact_penalty=20.0,
    )
    no_contact_score = smooth_minimax_objective(
        ratios,
        target_contact_count=0,
        power=4.0,
        no_contact_penalty=20.0,
    )

    assert no_contact_score == contact_score + 20.0


def test_summarize_rows_keeps_nonfinal_flags_and_best_ratio() -> None:
    thresholds = strict_terminal_thresholds(ACCEPTANCE)
    pass_metrics = _metrics()
    fail_metrics = _metrics(force=0.3, xy=0.004, orient=0.06)
    pass_gate = terminal_gate(pass_metrics, thresholds)
    fail_gate = terminal_gate(fail_metrics, thresholds)
    rows = [
        _row("pass", pass_gate, pass_metrics),
        _row("fail", fail_gate, fail_metrics, success=False),
    ]

    summary = summarize_rows(rows, v56_strict_best_ratio=2.5)

    assert summary["optimization_case_count"] == 2
    assert summary["strict_terminal_pass_count"] == 1
    assert summary["optimizer_success_count"] == 1
    assert summary["setup_failed_criteria_counts"] == {
        "force_error_N": 1,
        "orientation_error_rad": 1,
        "tangential_error_m": 1,
    }
    assert summary["best_case_id"] == "pass"
    assert summary["best_ratio_improvement"] == 2.0
    assert summary["strict_terminal_constrained_optimization_complete"] is False
    assert summary["strict_paper_equivalent_feasibility"] is False
