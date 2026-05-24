from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, lsq_linear, minimize


@dataclass(frozen=True)
class VelocitySolveResult:
    qdot: np.ndarray
    success: bool
    status: int
    message: str
    residual_norm: float
    active_bound_count: int


@dataclass(frozen=True)
class SlackVelocitySolveResult:
    qdot: np.ndarray
    slack: np.ndarray
    success: bool
    status: int
    message: str
    residual_norm: float
    active_bound_count: int


def step_velocity_bounds(
    q: np.ndarray,
    *,
    dt: float,
    q_min: np.ndarray,
    q_max: np.ndarray,
    qdot_min: np.ndarray,
    qdot_max: np.ndarray,
    margin: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    q = np.asarray(q, dtype=float)
    lower = np.maximum(np.asarray(qdot_min, dtype=float), (np.asarray(q_min, dtype=float) + margin - q) / dt)
    upper = np.minimum(np.asarray(qdot_max, dtype=float), (np.asarray(q_max, dtype=float) - margin - q) / dt)
    return lower, upper


def is_velocity_feasible(
    q: np.ndarray,
    qdot: np.ndarray,
    *,
    dt: float,
    q_min: np.ndarray,
    q_max: np.ndarray,
    qdot_min: np.ndarray,
    qdot_max: np.ndarray,
    margin: float = 0.0,
    atol: float = 1e-10,
) -> bool:
    lower, upper = step_velocity_bounds(
        q,
        dt=dt,
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        margin=margin,
    )
    qdot = np.asarray(qdot, dtype=float)
    return bool(np.all(qdot >= lower - atol) and np.all(qdot <= upper + atol))


def solve_constrained_velocity_least_squares(
    A: np.ndarray,
    b: np.ndarray,
    *,
    q: np.ndarray,
    dt: float,
    q_min: np.ndarray,
    q_max: np.ndarray,
    qdot_min: np.ndarray,
    qdot_max: np.ndarray,
    damping: float = 1e-8,
    damping_target: np.ndarray | None = None,
    margin: float = 0.0,
) -> VelocitySolveResult:
    """Solve a bounded least-squares velocity subproblem.

    This is the v1 testable contract for the later QP controller. It enforces
    velocity and one-step position bounds inside the optimizer, not by clipping
    after the solve.
    """
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    damping_value = float(damping)
    if damping_value < 0.0:
        raise ValueError("damping must be nonnegative")
    if damping_target is None:
        solve_damping_target = np.zeros(A.shape[1], dtype=float)
    else:
        solve_damping_target = np.asarray(damping_target, dtype=float)
        if solve_damping_target.shape != (A.shape[1],):
            raise ValueError("damping_target must have one entry per velocity variable")
    lower, upper = step_velocity_bounds(
        np.asarray(q, dtype=float),
        dt=dt,
        q_min=np.asarray(q_min, dtype=float),
        q_max=np.asarray(q_max, dtype=float),
        qdot_min=np.asarray(qdot_min, dtype=float),
        qdot_max=np.asarray(qdot_max, dtype=float),
        margin=margin,
    )
    if np.any(lower > upper):
        return VelocitySolveResult(
            qdot=np.full_like(lower, np.nan, dtype=float),
            success=False,
            status=-1,
            message="infeasible bounds",
            residual_norm=float("nan"),
            active_bound_count=0,
        )

    if damping_value > 0.0:
        A_aug = np.vstack([A, np.sqrt(damping_value) * np.eye(A.shape[1])])
        b_aug = np.concatenate([b, np.sqrt(damping_value) * solve_damping_target])
    else:
        A_aug = A
        b_aug = b

    result = lsq_linear(A_aug, b_aug, bounds=(lower, upper), method="trf", lsmr_tol="auto")
    qdot = np.asarray(result.x, dtype=float)
    active = int(np.sum(np.isclose(qdot, lower, atol=1e-8) | np.isclose(qdot, upper, atol=1e-8)))
    residual = float(np.linalg.norm(A @ qdot - b))
    return VelocitySolveResult(
        qdot=qdot,
        success=bool(result.success),
        status=int(result.status),
        message=str(result.message),
        residual_norm=residual,
        active_bound_count=active,
    )


def solve_constrained_velocity_least_squares_with_slack(
    A: np.ndarray,
    b: np.ndarray,
    *,
    q: np.ndarray,
    dt: float,
    q_min: np.ndarray,
    q_max: np.ndarray,
    qdot_min: np.ndarray,
    qdot_max: np.ndarray,
    slack_weights: np.ndarray,
    constraint_weight: float = 1e3,
    damping: float = 1e-8,
    damping_target: np.ndarray | None = None,
    margin: float = 0.0,
) -> SlackVelocitySolveResult:
    """Solve a bounded velocity task with explicit task slack variables.

    The model is `A qdot + slack = b`. Joint velocity and one-step position
    bounds remain hard on `qdot`; task mismatch is represented by slack.
    """
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    slack_weights = np.asarray(slack_weights, dtype=float)
    if A.ndim != 2:
        raise ValueError("A must be a matrix")
    if b.shape != (A.shape[0],):
        raise ValueError("b must have one entry per task row")
    if slack_weights.shape != (A.shape[0],):
        raise ValueError("slack_weights must have one entry per task row")
    if np.any(slack_weights < 0.0):
        raise ValueError("slack_weights must be nonnegative")
    if constraint_weight <= 0.0:
        raise ValueError("constraint_weight must be positive")
    damping_value = float(damping)
    if damping_value < 0.0:
        raise ValueError("damping must be nonnegative")
    if damping_target is None:
        solve_damping_target = np.zeros(A.shape[1], dtype=float)
    else:
        solve_damping_target = np.asarray(damping_target, dtype=float)
        if solve_damping_target.shape != (A.shape[1],):
            raise ValueError("damping_target must have one entry per velocity variable")

    lower_qdot, upper_qdot = step_velocity_bounds(
        np.asarray(q, dtype=float),
        dt=dt,
        q_min=np.asarray(q_min, dtype=float),
        q_max=np.asarray(q_max, dtype=float),
        qdot_min=np.asarray(qdot_min, dtype=float),
        qdot_max=np.asarray(qdot_max, dtype=float),
        margin=margin,
    )
    if np.any(lower_qdot > upper_qdot):
        return SlackVelocitySolveResult(
            qdot=np.full_like(lower_qdot, np.nan, dtype=float),
            slack=np.full(A.shape[0], np.nan, dtype=float),
            success=False,
            status=-1,
            message="infeasible bounds",
            residual_norm=float("nan"),
            active_bound_count=0,
        )

    task_rows = A.shape[0]
    dof = A.shape[1]
    equality_block = constraint_weight * np.hstack([A, np.eye(task_rows)])
    equality_target = constraint_weight * b
    slack_block = np.hstack([np.zeros((task_rows, dof)), np.diag(np.sqrt(slack_weights))])
    blocks = [equality_block, slack_block]
    targets = [equality_target, np.zeros(task_rows)]
    if damping_value > 0.0:
        damping_block = np.hstack([np.sqrt(damping_value) * np.eye(dof), np.zeros((dof, task_rows))])
        blocks.append(damping_block)
        targets.append(np.sqrt(damping_value) * solve_damping_target)

    A_aug = np.vstack(blocks)
    b_aug = np.concatenate(targets)
    lower = np.concatenate([lower_qdot, np.full(task_rows, -np.inf)])
    upper = np.concatenate([upper_qdot, np.full(task_rows, np.inf)])
    result = lsq_linear(A_aug, b_aug, bounds=(lower, upper), method="trf", lsmr_tol="auto")
    z = np.asarray(result.x, dtype=float)
    qdot = z[:dof]
    slack = z[dof:]
    active = int(np.sum(np.isclose(qdot, lower_qdot, atol=1e-8) | np.isclose(qdot, upper_qdot, atol=1e-8)))
    residual = float(np.linalg.norm(A @ qdot + slack - b))
    return SlackVelocitySolveResult(
        qdot=qdot,
        slack=slack,
        success=bool(result.success),
        status=int(result.status),
        message=str(result.message),
        residual_norm=residual,
        active_bound_count=active,
    )


def solve_linear_primary_angular_secondary_with_slack(
    linear_A: np.ndarray,
    linear_b: np.ndarray,
    angular_A: np.ndarray,
    angular_b: np.ndarray,
    *,
    q: np.ndarray,
    dt: float,
    q_min: np.ndarray,
    q_max: np.ndarray,
    qdot_min: np.ndarray,
    qdot_max: np.ndarray,
    linear_slack_weights: np.ndarray,
    angular_axis_weights: np.ndarray,
    primary_constraint_weight: float = 1e3,
    damping: float = 1e-8,
    damping_target: np.ndarray | None = None,
    secondary_damping: float | None = None,
    margin: float = 0.0,
) -> SlackVelocitySolveResult:
    """Preserve a primary linear task while optimizing a secondary angular task.

    Stage 1 solves the existing bounded linear task with explicit linear slack.
    Stage 2 minimizes angular residual subject to hard velocity/joint bounds and
    an equality constraint that preserves the stage-1 TCP linear velocity.
    The returned slack vector is `[linear_slack, angular_slack]`, where angular
    slack is reported as the remaining desired-minus-actual angular velocity.
    """
    linear_A = np.asarray(linear_A, dtype=float)
    linear_b = np.asarray(linear_b, dtype=float)
    angular_A = np.asarray(angular_A, dtype=float)
    angular_b = np.asarray(angular_b, dtype=float)
    linear_slack_weights = np.asarray(linear_slack_weights, dtype=float)
    angular_axis_weights = np.asarray(angular_axis_weights, dtype=float)
    if linear_A.ndim != 2 or angular_A.ndim != 2:
        raise ValueError("linear_A and angular_A must be matrices")
    if linear_b.shape != (linear_A.shape[0],):
        raise ValueError("linear_b must have one entry per linear task row")
    if angular_b.shape != (angular_A.shape[0],):
        raise ValueError("angular_b must have one entry per angular task row")
    if linear_A.shape[1] != angular_A.shape[1]:
        raise ValueError("linear_A and angular_A must have the same number of columns")
    if linear_slack_weights.shape != (linear_A.shape[0],):
        raise ValueError("linear_slack_weights must have one entry per linear task row")
    if angular_axis_weights.shape != (angular_A.shape[0],):
        raise ValueError("angular_axis_weights must have one entry per angular task row")
    if np.any(angular_axis_weights < 0.0):
        raise ValueError("angular_axis_weights must be nonnegative")
    damping_value = float(damping)
    if damping_value < 0.0:
        raise ValueError("damping must be nonnegative")
    secondary_damping_value = damping_value if secondary_damping is None else float(secondary_damping)
    if secondary_damping_value < 0.0:
        raise ValueError("secondary_damping must be nonnegative")
    if damping_target is None:
        solve_damping_target = None
    else:
        solve_damping_target = np.asarray(damping_target, dtype=float)
        if solve_damping_target.shape != (linear_A.shape[1],):
            raise ValueError("damping_target must have one entry per velocity variable")

    primary = solve_constrained_velocity_least_squares_with_slack(
        linear_A,
        linear_b,
        q=q,
        dt=dt,
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        slack_weights=linear_slack_weights,
        constraint_weight=primary_constraint_weight,
        damping=damping_value,
        margin=margin,
    )
    if not primary.success:
        slack = np.concatenate([primary.slack, np.full(angular_A.shape[0], np.nan)])
        return SlackVelocitySolveResult(
            qdot=primary.qdot,
            slack=slack,
            success=False,
            status=primary.status,
            message=f"primary failed: {primary.message}",
            residual_norm=primary.residual_norm,
            active_bound_count=primary.active_bound_count,
        )

    lower, upper = step_velocity_bounds(
        np.asarray(q, dtype=float),
        dt=dt,
        q_min=np.asarray(q_min, dtype=float),
        q_max=np.asarray(q_max, dtype=float),
        qdot_min=np.asarray(qdot_min, dtype=float),
        qdot_max=np.asarray(qdot_max, dtype=float),
        margin=margin,
    )
    if np.any(lower > upper):
        slack = np.concatenate([primary.slack, np.full(angular_A.shape[0], np.nan)])
        return SlackVelocitySolveResult(
            qdot=primary.qdot,
            slack=slack,
            success=False,
            status=-1,
            message="secondary infeasible bounds",
            residual_norm=float("nan"),
            active_bound_count=primary.active_bound_count,
        )

    target_linear_velocity = linear_A @ primary.qdot
    angular_weight_sq = angular_axis_weights * angular_axis_weights
    secondary_damping_target = primary.qdot if solve_damping_target is None else solve_damping_target

    def objective(x: np.ndarray) -> float:
        angular_error = angular_A @ x - angular_b
        damping_error = x - secondary_damping_target
        return float(
            np.sum(angular_weight_sq * angular_error * angular_error)
            + secondary_damping_value * np.dot(damping_error, damping_error)
        )

    def jacobian(x: np.ndarray) -> np.ndarray:
        angular_error = angular_A @ x - angular_b
        return 2.0 * (angular_A.T @ (angular_weight_sq * angular_error)) + 2.0 * secondary_damping_value * (
            x - secondary_damping_target
        )

    result = minimize(
        objective,
        primary.qdot,
        jac=jacobian,
        method="SLSQP",
        bounds=Bounds(lower, upper),
        constraints=[
            LinearConstraint(linear_A, target_linear_velocity, target_linear_velocity),
        ],
        options={"ftol": 1e-12, "maxiter": 200},
    )
    qdot = np.asarray(
        result.x if np.all(np.isfinite(result.x)) else primary.qdot,
        dtype=float,
    )
    linear_slack = linear_b - linear_A @ qdot
    angular_slack = angular_b - angular_A @ qdot
    slack = np.concatenate([linear_slack, angular_slack])
    active = int(
        np.sum(
            np.isclose(qdot, lower, atol=1e-8)
            | np.isclose(qdot, upper, atol=1e-8)
        )
    )
    residual = float(
        np.linalg.norm(
            np.concatenate(
                [
                    linear_A @ qdot + linear_slack - linear_b,
                    angular_A @ qdot + angular_slack - angular_b,
                ]
            )
        )
    )
    return SlackVelocitySolveResult(
        qdot=qdot,
        slack=slack,
        success=bool(result.success),
        status=int(result.status),
        message=f"primary: {primary.message}; secondary: {result.message}",
        residual_norm=residual,
        active_bound_count=active,
    )
