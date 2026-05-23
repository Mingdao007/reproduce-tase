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


@dataclass(frozen=True)
class ControllerStepResult:
    qdot: np.ndarray
    actual_linear_velocity_m_s: np.ndarray
    desired_linear_velocity_m_s: np.ndarray
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
    solve: VelocitySolveResult = solve_constrained_velocity_least_squares(
        weight * jacp,
        weight * desired,
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

    return ControllerStepResult(
        qdot=qdot,
        actual_linear_velocity_m_s=actual,
        desired_linear_velocity_m_s=desired,
        residual_norm=solve.residual_norm,
        active_bound_count=solve.active_bound_count,
        solver_success=solve.success,
        solver_message=solve.message,
    )

