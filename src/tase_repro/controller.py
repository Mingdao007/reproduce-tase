from __future__ import annotations

from dataclasses import dataclass

import mujoco
import numpy as np

from tase_repro.constraints import VelocitySolveResult, solve_constrained_velocity_least_squares
from tase_repro.kinematics import site_jacobian


@dataclass(frozen=True)
class CartesianVelocityCommand:
    linear_velocity_m_s: np.ndarray
    weight: float = 1.0
    axis_weights: np.ndarray | None = None


@dataclass(frozen=True)
class ControllerStepResult:
    qdot: np.ndarray
    actual_linear_velocity_m_s: np.ndarray
    desired_linear_velocity_m_s: np.ndarray
    residual_linear_velocity_m_s: np.ndarray
    planar_residual_norm_m_s: float
    normal_residual_m_s: float
    residual_norm: float
    active_bound_count: int
    solver_success: bool
    solver_message: str


def solve_site_linear_velocity_step(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    *,
    site_name: str,
    q: np.ndarray,
    command: CartesianVelocityCommand,
    dt: float,
    q_min: np.ndarray,
    q_max: np.ndarray,
    qdot_min: np.ndarray,
    qdot_max: np.ndarray,
    damping: float = 1e-6,
) -> ControllerStepResult:
    """Solve one velocity-level TCP task with hard joint/velocity bounds."""
    jacp, _ = site_jacobian(model, data, site_name)
    desired = np.asarray(command.linear_velocity_m_s, dtype=float)
    if desired.shape != (3,):
        raise ValueError("linear velocity command must have shape (3,)")

    weight = float(command.weight)
    if command.axis_weights is None:
        axis_weights = np.ones(3, dtype=float)
    else:
        axis_weights = np.asarray(command.axis_weights, dtype=float)
        if axis_weights.shape != (3,):
            raise ValueError("axis_weights must have shape (3,)")
        if np.any(axis_weights < 0.0):
            raise ValueError("axis_weights must be nonnegative")
    row_weights = weight * axis_weights
    solve: VelocitySolveResult = solve_constrained_velocity_least_squares(
        row_weights[:, None] * jacp,
        row_weights * desired,
        q=np.asarray(q, dtype=float),
        dt=dt,
        q_min=np.asarray(q_min, dtype=float),
        q_max=np.asarray(q_max, dtype=float),
        qdot_min=np.asarray(qdot_min, dtype=float),
        qdot_max=np.asarray(qdot_max, dtype=float),
        damping=damping,
    )
    if solve.success:
        qdot = solve.qdot
        actual = jacp @ qdot
    else:
        qdot = np.zeros(model.nv, dtype=float)
        actual = np.zeros(3, dtype=float)
    residual = actual - desired

    return ControllerStepResult(
        qdot=qdot,
        actual_linear_velocity_m_s=actual,
        desired_linear_velocity_m_s=desired,
        residual_linear_velocity_m_s=residual,
        planar_residual_norm_m_s=float(np.linalg.norm(residual[:2])),
        normal_residual_m_s=float(residual[2]),
        residual_norm=solve.residual_norm,
        active_bound_count=solve.active_bound_count,
        solver_success=solve.success,
        solver_message=solve.message,
    )
