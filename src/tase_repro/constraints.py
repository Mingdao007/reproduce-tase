from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import lsq_linear


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
    margin: float = 0.0,
) -> VelocitySolveResult:
    """Solve a bounded least-squares velocity subproblem.

    This is the v1 testable contract for the later QP controller. It enforces
    velocity and one-step position bounds inside the optimizer, not by clipping
    after the solve.
    """
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
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

    if damping > 0.0:
        A_aug = np.vstack([A, np.sqrt(damping) * np.eye(A.shape[1])])
        b_aug = np.concatenate([b, np.zeros(A.shape[1])])
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
    if damping > 0.0:
        damping_block = np.hstack([np.sqrt(damping) * np.eye(dof), np.zeros((dof, task_rows))])
        blocks.append(damping_block)
        targets.append(np.zeros(dof))

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
