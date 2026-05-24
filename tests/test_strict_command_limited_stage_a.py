from __future__ import annotations

from tase_repro.feasibility import FeasibilityThresholds

from scripts.audit_strict_command_limited_stage_a import (
    command_limited_cases,
    strict_setup_chain_gate,
    summarize_rows,
)


STRICT_THRESHOLDS = {
    "max_final_tangential_error_m": 0.002,
    "max_final_orientation_error_rad": 0.03,
    "max_tail_mean_abs_force_error_N": 0.25,
    "qdot_saturation_fraction_max": 0.01,
}


def _phase(
    *,
    contact: float = 1.0,
    force_error: float = 0.01,
    qdot_saturation: float = 0.0,
    tail_qdot_utilization: float = 0.1,
) -> dict:
    return {
        "summary": {
            "contact_present_fraction": contact,
            "tail_mean_abs_force_error_N": force_error,
            "qdot_saturation_fraction": qdot_saturation,
            "tail_max_qdot_utilization": tail_qdot_utilization,
            "max_qdot_violation_rad_s": 0.0,
            "max_joint_limit_violation_rad": 0.0,
        }
    }


def test_command_limited_cases_change_command_generation_not_only_priority() -> None:
    cases = command_limited_cases()
    case_ids = [case.case_id for case in cases]

    assert "v113_reference_uncapped" in case_ids
    assert "angular_cap_0p02_low_force_longer" in case_ids
    assert "angular_cap_0p01_low_planar_slow" in case_ids
    assert len(case_ids) == len(set(case_ids))
    assert any(case.force_gain < 5e-4 for case in cases)
    assert any(case.approach_max_angular_command_rad_s is not None for case in cases)
    assert any(case.approach_duration_s > 4.0 for case in cases)


def test_strict_setup_chain_gate_uses_worst_setup_phase_qdot() -> None:
    gate = strict_setup_chain_gate(
        final_orientation_error_rad=0.01,
        final_tangential_error_m=0.001,
        setup_phases=[
            _phase(qdot_saturation=0.5, tail_qdot_utilization=1.0),
            _phase(qdot_saturation=0.0, tail_qdot_utilization=0.5),
        ],
        strict_thresholds=STRICT_THRESHOLDS,
        feasibility_thresholds=FeasibilityThresholds(),
    )

    assert gate["passed"] is False
    assert gate["failed_criteria"] == [
        "setup_max_qdot_saturation_fraction",
        "setup_max_tail_qdot_utilization",
    ]
    assert gate["criteria"]["setup_max_qdot_saturation_fraction"]["actual"] == 0.5
    assert gate["criteria"]["setup_max_tail_qdot_utilization"]["actual"] == 1.0


def test_summarize_rows_keeps_command_limited_probe_nonfinal() -> None:
    passing_gate = strict_setup_chain_gate(
        final_orientation_error_rad=0.01,
        final_tangential_error_m=0.001,
        setup_phases=[_phase()],
        strict_thresholds=STRICT_THRESHOLDS,
        feasibility_thresholds=FeasibilityThresholds(),
    )
    failing_gate = strict_setup_chain_gate(
        final_orientation_error_rad=0.04,
        final_tangential_error_m=0.005,
        setup_phases=[_phase(qdot_saturation=0.25, tail_qdot_utilization=1.0)],
        strict_thresholds=STRICT_THRESHOLDS,
        feasibility_thresholds=FeasibilityThresholds(),
    )
    rows = [
        {
            "case_id": "passing",
            "strict_setup_chain_gate": passing_gate,
            "strict_setup_violation_score": 0.0,
            "setup_final_tangential_position_error_m": 0.001,
            "setup_final_orientation_error_rad": 0.01,
            "trajectory_feasibility_gate": {"feasibility_pass": True},
            "planned_setup_then_trajectory_pass": True,
        },
        {
            "case_id": "failing",
            "strict_setup_chain_gate": failing_gate,
            "strict_setup_violation_score": 40.0,
            "setup_final_tangential_position_error_m": 0.005,
            "setup_final_orientation_error_rad": 0.04,
            "trajectory_feasibility_gate": {"feasibility_pass": False},
            "planned_setup_then_trajectory_pass": False,
        },
    ]

    summary = summarize_rows(rows)

    assert summary["case_count"] == 2
    assert summary["strict_setup_chain_pass_count"] == 1
    assert summary["trajectory_feasibility_pass_count"] == 1
    assert summary["planned_setup_then_trajectory_pass_count"] == 1
    assert summary["setup_failed_criteria_counts"] == {
        "final_orientation_error_rad": 1,
        "final_tangential_position_error_m": 1,
        "setup_max_qdot_saturation_fraction": 1,
        "setup_max_tail_qdot_utilization": 1,
    }
    assert summary["best_score_case_id"] == "passing"
    assert summary["strict_command_limited_stage_a_complete"] is False
    assert summary["strict_paper_equivalent_feasibility"] is False
