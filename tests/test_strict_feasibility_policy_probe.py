from __future__ import annotations

from tase_repro.feasibility import FeasibilityThresholds

from scripts.audit_strict_feasibility_policy_probe import (
    setup_terminal_gate,
    strict_policy_cases,
    summarize_rows,
)


STRICT_THRESHOLDS = {
    "max_final_tangential_error_m": 0.002,
    "max_final_orientation_error_rad": 0.03,
    "max_tail_mean_abs_force_error_N": 0.25,
    "qdot_saturation_fraction_max": 0.01,
}


def _phase_summary(
    *,
    force_error: float = 0.01,
    qdot_saturation: float = 0.0,
    tail_qdot_utilization: float = 0.1,
) -> dict:
    return {
        "summary": {
            "contact_present_fraction": 1.0,
            "tail_mean_abs_force_error_N": force_error,
            "qdot_saturation_fraction": qdot_saturation,
            "tail_max_qdot_utilization": tail_qdot_utilization,
            "max_qdot_violation_rad_s": 0.0,
            "max_joint_limit_violation_rad": 0.0,
        }
    }


def test_strict_policy_cases_include_reference_and_new_blended_rows() -> None:
    case_ids = [case.case_id for case in strict_policy_cases()]

    assert case_ids[0] == "baseline_no_recenter"
    assert "linear_recenter_4_linear_settle_4" in case_ids
    assert "weighted_recenter_4_weighted_settle_2" in case_ids
    assert "weighted_recenter_high_planar_kp_4_2" in case_ids
    assert "linear_recenter_weighted_settle_high_planar_kp" in case_ids
    assert len(case_ids) == len(set(case_ids))


def test_setup_terminal_gate_requires_orientation_tangential_force_and_qdot() -> None:
    gate = setup_terminal_gate(
        final_orientation_error_rad=0.031,
        final_tangential_error_m=0.003,
        setup_phase_summary=_phase_summary(force_error=0.3, qdot_saturation=0.2),
        strict_thresholds=STRICT_THRESHOLDS,
        feasibility_thresholds=FeasibilityThresholds(),
    )

    assert gate["passed"] is False
    assert gate["failed_criteria"] == [
        "final_orientation_error_rad",
        "final_tangential_position_error_m",
        "tail_mean_abs_force_error_N",
        "qdot_saturation_fraction",
    ]
    assert gate["criteria"]["final_orientation_error_rad"]["ratio"] > 1.0
    assert gate["criteria"]["final_tangential_position_error_m"]["ratio"] > 1.0


def test_summarize_rows_keeps_probe_nonfinal() -> None:
    passing_gate = setup_terminal_gate(
        final_orientation_error_rad=0.01,
        final_tangential_error_m=0.001,
        setup_phase_summary=_phase_summary(),
        strict_thresholds=STRICT_THRESHOLDS,
        feasibility_thresholds=FeasibilityThresholds(),
    )
    failing_gate = setup_terminal_gate(
        final_orientation_error_rad=0.02,
        final_tangential_error_m=0.004,
        setup_phase_summary=_phase_summary(qdot_saturation=0.2),
        strict_thresholds=STRICT_THRESHOLDS,
        feasibility_thresholds=FeasibilityThresholds(),
    )
    rows = [
        {
            "case_id": "passing_setup",
            "setup_terminal_state_gate": passing_gate,
            "trajectory_feasibility_gate": {"feasibility_pass": True},
            "planned_setup_then_trajectory_pass": True,
            "full_staged_feasibility_pass": False,
            "setup_violation_score": 0.0,
        },
        {
            "case_id": "failing_setup",
            "setup_terminal_state_gate": failing_gate,
            "trajectory_feasibility_gate": {"feasibility_pass": True},
            "planned_setup_then_trajectory_pass": False,
            "full_staged_feasibility_pass": False,
            "setup_violation_score": 20.0,
        },
    ]

    summary = summarize_rows(rows)

    assert summary["case_count"] == 2
    assert summary["setup_terminal_state_pass_count"] == 1
    assert summary["trajectory_feasibility_pass_count"] == 2
    assert summary["planned_setup_then_trajectory_pass_count"] == 1
    assert summary["full_staged_feasibility_pass_count"] == 0
    assert summary["setup_failed_criteria_counts"] == {
        "final_tangential_position_error_m": 1,
        "qdot_saturation_fraction": 1,
    }
    assert summary["best_setup_score_case_id"] == "passing_setup"
    assert summary["strict_policy_probe_complete"] is False
    assert summary["strict_paper_equivalent_feasibility"] is False
