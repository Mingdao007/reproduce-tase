from __future__ import annotations

from tase_repro.feasibility import FeasibilityThresholds, evaluate_force_motion_feasibility


def passing_metrics() -> dict[str, float]:
    return {
        "solver_success_fraction": 1.0,
        "contact_present_fraction": 1.0,
        "tail_mean_abs_force_error_N": 0.1,
        "max_tangential_position_error_m": 0.001,
        "max_planar_velocity_slack_m_s": 0.0005,
        "max_abs_normal_velocity_slack_m_s": 0.0001,
        "max_qdot_violation_rad_s": 0.0,
        "max_joint_limit_violation_rad": 0.0,
        "max_abs_qdot_rad_s": 0.1,
        "max_qdot_utilization": 0.67,
        "tail_max_qdot_utilization": 0.5,
        "qdot_saturation_fraction": 0.0,
        "tail_qdot_saturation_fraction": 0.0,
        "max_orientation_error_rad": 0.005,
        "max_angular_velocity_slack_rad_s": 0.01,
    }


def test_force_motion_feasibility_passes_when_all_gates_pass() -> None:
    result = evaluate_force_motion_feasibility(
        passing_metrics(),
        thresholds=FeasibilityThresholds(),
        qdot_abs_limit_rad_s=0.15,
    )
    assert result["feasibility_pass"]
    assert result["failed_criteria"] == []


def test_force_motion_feasibility_reports_failed_criteria() -> None:
    metrics = passing_metrics()
    metrics["contact_present_fraction"] = 0.95
    metrics["max_planar_velocity_slack_m_s"] = 0.003
    metrics["qdot_saturation_fraction"] = 0.25
    metrics["tail_max_qdot_utilization"] = 1.0
    result = evaluate_force_motion_feasibility(
        metrics,
        thresholds=FeasibilityThresholds(),
        qdot_abs_limit_rad_s=0.15,
    )
    assert not result["feasibility_pass"]
    assert result["failed_criteria"] == [
        "contact_present_fraction",
        "max_planar_velocity_slack_m_s",
        "qdot_saturation_fraction",
        "tail_max_qdot_utilization",
    ]


def test_force_motion_feasibility_fails_missing_required_metric() -> None:
    metrics = passing_metrics()
    del metrics["max_abs_normal_velocity_slack_m_s"]
    result = evaluate_force_motion_feasibility(metrics, thresholds=FeasibilityThresholds())
    assert not result["feasibility_pass"]
    assert "max_abs_normal_velocity_slack_m_s" in result["failed_criteria"]


def test_force_motion_feasibility_uses_optional_orientation_gates() -> None:
    metrics = passing_metrics()
    metrics["max_orientation_error_rad"] = 0.02
    result = evaluate_force_motion_feasibility(
        metrics,
        thresholds=FeasibilityThresholds(
            max_orientation_error_rad_max=0.01,
            max_angular_velocity_slack_rad_s_max=0.02,
        ),
    )
    assert not result["feasibility_pass"]
    assert result["failed_criteria"] == ["max_orientation_error_rad"]


def test_force_motion_feasibility_requires_orientation_metrics_when_gated() -> None:
    metrics = passing_metrics()
    del metrics["max_orientation_error_rad"]
    result = evaluate_force_motion_feasibility(
        metrics,
        thresholds=FeasibilityThresholds(max_orientation_error_rad_max=0.01),
    )
    assert not result["feasibility_pass"]
    assert result["failed_criteria"] == ["max_orientation_error_rad"]
