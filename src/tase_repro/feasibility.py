from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class FeasibilityThresholds:
    solver_success_fraction_min: float = 1.0
    contact_present_fraction_min: float = 1.0
    tail_mean_abs_force_error_N_max: float = 0.25
    max_tangential_position_error_m_max: float = 0.002
    max_planar_velocity_slack_m_s_max: float = 0.001
    max_abs_normal_velocity_slack_m_s_max: float = 0.0002
    max_qdot_violation_rad_s_max: float = 1e-9
    max_joint_limit_violation_rad_max: float = 1e-9
    qdot_saturation_fraction_max: float = 0.01
    tail_max_qdot_utilization_max: float = 0.98

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def _metric(metrics: dict[str, Any], name: str) -> float | None:
    value = metrics.get(name)
    if value is None:
        return None
    return float(value)


def _add_min_criterion(
    criteria: dict[str, dict[str, Any]],
    metrics: dict[str, Any],
    *,
    name: str,
    threshold: float,
) -> None:
    actual = _metric(metrics, name)
    criteria[name] = {
        "actual": actual,
        "operator": ">=",
        "threshold": float(threshold),
        "passed": actual is not None and actual >= float(threshold),
    }


def _add_max_criterion(
    criteria: dict[str, dict[str, Any]],
    metrics: dict[str, Any],
    *,
    name: str,
    threshold: float,
) -> None:
    actual = _metric(metrics, name)
    criteria[name] = {
        "actual": actual,
        "operator": "<=",
        "threshold": float(threshold),
        "passed": actual is not None and actual <= float(threshold),
    }


def evaluate_force_motion_feasibility(
    metrics: dict[str, Any],
    *,
    thresholds: FeasibilityThresholds | None = None,
    qdot_abs_limit_rad_s: float | None = None,
) -> dict[str, Any]:
    """Evaluate simulation force-motion metrics against explicit gates."""
    limits = thresholds or FeasibilityThresholds()
    criteria: dict[str, dict[str, Any]] = {}
    _add_min_criterion(
        criteria,
        metrics,
        name="solver_success_fraction",
        threshold=limits.solver_success_fraction_min,
    )
    _add_min_criterion(
        criteria,
        metrics,
        name="contact_present_fraction",
        threshold=limits.contact_present_fraction_min,
    )
    _add_max_criterion(
        criteria,
        metrics,
        name="tail_mean_abs_force_error_N",
        threshold=limits.tail_mean_abs_force_error_N_max,
    )
    _add_max_criterion(
        criteria,
        metrics,
        name="max_tangential_position_error_m",
        threshold=limits.max_tangential_position_error_m_max,
    )
    _add_max_criterion(
        criteria,
        metrics,
        name="max_planar_velocity_slack_m_s",
        threshold=limits.max_planar_velocity_slack_m_s_max,
    )
    _add_max_criterion(
        criteria,
        metrics,
        name="max_abs_normal_velocity_slack_m_s",
        threshold=limits.max_abs_normal_velocity_slack_m_s_max,
    )
    _add_max_criterion(
        criteria,
        metrics,
        name="max_qdot_violation_rad_s",
        threshold=limits.max_qdot_violation_rad_s_max,
    )
    _add_max_criterion(
        criteria,
        metrics,
        name="max_joint_limit_violation_rad",
        threshold=limits.max_joint_limit_violation_rad_max,
    )
    if qdot_abs_limit_rad_s is not None:
        qdot_limit = abs(float(qdot_abs_limit_rad_s))
        if _metric(metrics, "max_qdot_utilization") is None:
            actual_qdot = _metric(metrics, "max_abs_qdot_rad_s")
            utilization = None if actual_qdot is None or qdot_limit <= 0.0 else actual_qdot / qdot_limit
            metrics = {**metrics, "max_qdot_utilization": utilization}
    _add_max_criterion(
        criteria,
        metrics,
        name="qdot_saturation_fraction",
        threshold=limits.qdot_saturation_fraction_max,
    )
    _add_max_criterion(
        criteria,
        metrics,
        name="tail_max_qdot_utilization",
        threshold=limits.tail_max_qdot_utilization_max,
    )

    failed = [name for name, criterion in criteria.items() if not bool(criterion["passed"])]
    return {
        "feasibility_pass": not failed,
        "failed_criteria": failed,
        "criteria": criteria,
    }
