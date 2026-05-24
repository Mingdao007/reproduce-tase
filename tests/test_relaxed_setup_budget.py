from __future__ import annotations

from tase_repro.relaxed_setup_budget import RelaxedSetupBudget, evaluate_relaxed_setup_budget


def test_relaxed_setup_budget_records_qdot_saturation_without_failing() -> None:
    budget = RelaxedSetupBudget(
        max_setup_tangential_drift_m=0.010,
        max_final_orientation_error_rad=0.03,
        max_tail_mean_abs_force_error_N=0.25,
        contact_present_fraction_min=1.0,
        max_qdot_violation_rad_s=1e-9,
        max_joint_limit_violation_rad=1e-9,
    )
    gate = evaluate_relaxed_setup_budget(
        {
            "max_tangential_position_error_m": 0.0084,
            "final_orientation_error_rad": 0.002,
            "tail_mean_abs_force_error_N": 0.004,
            "contact_present_fraction": 1.0,
            "max_qdot_violation_rad_s": 0.0,
            "max_joint_limit_violation_rad": 0.0,
            "qdot_saturation_fraction": 1.0,
            "tail_max_qdot_utilization": 1.0,
        },
        budget,
    )

    assert gate["passed"] is True
    assert gate["recorded_qdot_saturation_fraction"] == 1.0
    assert gate["qdot_saturation_policy"] == "record_only"


def test_relaxed_setup_budget_fails_drift_over_budget() -> None:
    budget = RelaxedSetupBudget(
        max_setup_tangential_drift_m=0.010,
        max_final_orientation_error_rad=0.03,
        max_tail_mean_abs_force_error_N=0.25,
        contact_present_fraction_min=1.0,
        max_qdot_violation_rad_s=1e-9,
        max_joint_limit_violation_rad=1e-9,
    )
    gate = evaluate_relaxed_setup_budget(
        {
            "max_tangential_position_error_m": 0.011,
            "final_orientation_error_rad": 0.002,
            "tail_mean_abs_force_error_N": 0.004,
            "contact_present_fraction": 1.0,
            "max_qdot_violation_rad_s": 0.0,
            "max_joint_limit_violation_rad": 0.0,
            "qdot_saturation_fraction": 0.0,
            "tail_max_qdot_utilization": 0.1,
        },
        budget,
    )

    assert gate["passed"] is False
    assert gate["failed_criteria"] == ["setup_tangential_drift_m"]
