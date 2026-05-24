from __future__ import annotations

from dataclasses import dataclass

import mujoco
import numpy as np

from tase_repro.constraints import (
    SlackVelocitySolveResult,
    VelocitySolveResult,
    solve_constrained_velocity_least_squares,
    solve_constrained_velocity_least_squares_with_slack,
    solve_linear_primary_angular_secondary_with_slack,
)
from tase_repro.kinematics import site_jacobian


@dataclass(frozen=True)
class CartesianVelocityCommand:
    linear_velocity_m_s: np.ndarray
    weight: float = 1.0
    axis_weights: np.ndarray | None = None
    slack_axis_weights: np.ndarray | None = None
    slack_constraint_weight: float = 1e3
    angular_velocity_rad_s: np.ndarray | None = None
    angular_axis_weights: np.ndarray | None = None
    angular_slack_axis_weights: np.ndarray | None = None
    angular_priority_mode: str = "weighted"
    joint_velocity_target_rad_s: np.ndarray | None = None
    joint_velocity_weight: float = 0.0


@dataclass(frozen=True)
class ControllerStepResult:
    qdot: np.ndarray
    actual_linear_velocity_m_s: np.ndarray
    desired_linear_velocity_m_s: np.ndarray
    residual_linear_velocity_m_s: np.ndarray
    task_slack_linear_velocity_m_s: np.ndarray
    actual_angular_velocity_rad_s: np.ndarray
    desired_angular_velocity_rad_s: np.ndarray
    residual_angular_velocity_rad_s: np.ndarray
    task_slack_angular_velocity_rad_s: np.ndarray
    angular_residual_norm_rad_s: float
    angular_slack_norm_rad_s: float
    angular_task_enabled: bool
    planar_residual_norm_m_s: float
    normal_residual_m_s: float
    planar_slack_norm_m_s: float
    normal_slack_m_s: float
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
    jacp, jacr = site_jacobian(model, data, site_name)
    q_array = np.asarray(q, dtype=float)
    damping_value = float(damping)
    if damping_value < 0.0:
        raise ValueError("damping must be nonnegative")
    joint_velocity_weight = float(command.joint_velocity_weight)
    if joint_velocity_weight < 0.0:
        raise ValueError("joint_velocity_weight must be nonnegative")
    if command.joint_velocity_target_rad_s is None:
        if joint_velocity_weight > 0.0:
            raise ValueError("joint_velocity_target_rad_s is required when joint_velocity_weight is positive")
        joint_velocity_target = None
    else:
        joint_velocity_target = np.asarray(command.joint_velocity_target_rad_s, dtype=float)
        if joint_velocity_target.shape != (jacp.shape[1],):
            raise ValueError("joint_velocity_target_rad_s must have one entry per velocity variable")
    if joint_velocity_target is not None and joint_velocity_weight > 0.0:
        solve_damping = damping_value + joint_velocity_weight
        solve_damping_target = (joint_velocity_weight / solve_damping) * joint_velocity_target
    else:
        solve_damping = damping_value
        solve_damping_target = None
    desired = np.asarray(command.linear_velocity_m_s, dtype=float)
    if desired.shape != (3,):
        raise ValueError("linear velocity command must have shape (3,)")
    angular_task_enabled = command.angular_velocity_rad_s is not None
    if angular_task_enabled:
        desired_angular = np.asarray(command.angular_velocity_rad_s, dtype=float)
        if desired_angular.shape != (3,):
            raise ValueError("angular velocity command must have shape (3,)")
    else:
        desired_angular = np.zeros(3, dtype=float)
    if command.angular_priority_mode not in {"weighted", "linear_primary"}:
        raise ValueError("angular_priority_mode must be 'weighted' or 'linear_primary'")

    weight = float(command.weight)
    if command.axis_weights is None:
        axis_weights = np.ones(3, dtype=float)
    else:
        axis_weights = np.asarray(command.axis_weights, dtype=float)
        if axis_weights.shape != (3,):
            raise ValueError("axis_weights must have shape (3,)")
        if np.any(axis_weights < 0.0):
            raise ValueError("axis_weights must be nonnegative")
    if command.angular_axis_weights is None:
        angular_axis_weights = np.ones(3, dtype=float)
    else:
        angular_axis_weights = np.asarray(command.angular_axis_weights, dtype=float)
        if angular_axis_weights.shape != (3,):
            raise ValueError("angular_axis_weights must have shape (3,)")
        if np.any(angular_axis_weights < 0.0):
            raise ValueError("angular_axis_weights must be nonnegative")

    if angular_task_enabled:
        task_jacobian = np.vstack([jacp, jacr])
        task_desired = np.concatenate([desired, desired_angular])
        task_axis_weights = np.concatenate([axis_weights, angular_axis_weights])
    else:
        task_jacobian = jacp
        task_desired = desired
        task_axis_weights = axis_weights

    use_slack = command.slack_axis_weights is not None or (
        angular_task_enabled and command.angular_slack_axis_weights is not None
    )
    if (
        angular_task_enabled
        and command.angular_priority_mode == "linear_primary"
        and command.slack_axis_weights is None
    ):
        raise ValueError("slack_axis_weights are required for linear_primary angular priority")
    if not use_slack:
        row_weights = weight * task_axis_weights
        solve: VelocitySolveResult | SlackVelocitySolveResult = solve_constrained_velocity_least_squares(
            row_weights[:, None] * task_jacobian,
            row_weights * task_desired,
            q=q_array,
            dt=dt,
            q_min=np.asarray(q_min, dtype=float),
            q_max=np.asarray(q_max, dtype=float),
            qdot_min=np.asarray(qdot_min, dtype=float),
            qdot_max=np.asarray(qdot_max, dtype=float),
            damping=solve_damping,
            damping_target=solve_damping_target,
        )
        slack = np.zeros(task_jacobian.shape[0], dtype=float)
    else:
        if command.slack_axis_weights is None:
            raise ValueError("slack_axis_weights are required when using slack solve")
        slack_weights = np.asarray(command.slack_axis_weights, dtype=float)
        if slack_weights.shape != (3,):
            raise ValueError("slack_axis_weights must have shape (3,)")
        if np.any(slack_weights < 0.0):
            raise ValueError("slack_axis_weights must be nonnegative")
        if angular_task_enabled and command.angular_priority_mode == "linear_primary":
            solve = solve_linear_primary_angular_secondary_with_slack(
                jacp,
                desired,
                jacr,
                desired_angular,
                q=q_array,
                dt=dt,
                q_min=np.asarray(q_min, dtype=float),
                q_max=np.asarray(q_max, dtype=float),
                qdot_min=np.asarray(qdot_min, dtype=float),
                qdot_max=np.asarray(qdot_max, dtype=float),
                linear_slack_weights=slack_weights,
                angular_axis_weights=angular_axis_weights,
                primary_constraint_weight=float(command.slack_constraint_weight),
                damping=damping_value,
                damping_target=solve_damping_target,
                secondary_damping=solve_damping,
            )
        elif angular_task_enabled:
            if command.angular_slack_axis_weights is None:
                raise ValueError("angular_slack_axis_weights are required for angular slack solve")
            angular_slack_weights = np.asarray(command.angular_slack_axis_weights, dtype=float)
            if angular_slack_weights.shape != (3,):
                raise ValueError("angular_slack_axis_weights must have shape (3,)")
            if np.any(angular_slack_weights < 0.0):
                raise ValueError("angular_slack_axis_weights must be nonnegative")
            solve_slack_weights = np.concatenate([slack_weights, angular_slack_weights])
            solve = solve_constrained_velocity_least_squares_with_slack(
                task_jacobian,
                task_desired,
                q=q_array,
                dt=dt,
                q_min=np.asarray(q_min, dtype=float),
                q_max=np.asarray(q_max, dtype=float),
                qdot_min=np.asarray(qdot_min, dtype=float),
                qdot_max=np.asarray(qdot_max, dtype=float),
                slack_weights=solve_slack_weights,
                constraint_weight=float(command.slack_constraint_weight),
                damping=solve_damping,
                damping_target=solve_damping_target,
            )
        else:
            solve_slack_weights = slack_weights
            solve = solve_constrained_velocity_least_squares_with_slack(
                task_jacobian,
                task_desired,
                q=q_array,
                dt=dt,
                q_min=np.asarray(q_min, dtype=float),
                q_max=np.asarray(q_max, dtype=float),
                qdot_min=np.asarray(qdot_min, dtype=float),
                qdot_max=np.asarray(qdot_max, dtype=float),
                slack_weights=solve_slack_weights,
                constraint_weight=float(command.slack_constraint_weight),
                damping=solve_damping,
                damping_target=solve_damping_target,
            )
        slack = solve.slack
    if solve.success:
        qdot = solve.qdot
        actual = jacp @ qdot
        actual_angular = jacr @ qdot
    else:
        qdot = np.zeros(model.nv, dtype=float)
        actual = np.zeros(3, dtype=float)
        actual_angular = np.zeros(3, dtype=float)
        slack = task_desired.copy()
    residual = actual - desired
    angular_residual = actual_angular - desired_angular if angular_task_enabled else np.zeros(3, dtype=float)
    linear_slack = slack[:3]
    angular_slack = slack[3:] if angular_task_enabled else np.zeros(3, dtype=float)

    return ControllerStepResult(
        qdot=qdot,
        actual_linear_velocity_m_s=actual,
        desired_linear_velocity_m_s=desired,
        residual_linear_velocity_m_s=residual,
        task_slack_linear_velocity_m_s=linear_slack,
        actual_angular_velocity_rad_s=actual_angular,
        desired_angular_velocity_rad_s=desired_angular,
        residual_angular_velocity_rad_s=angular_residual,
        task_slack_angular_velocity_rad_s=angular_slack,
        angular_residual_norm_rad_s=float(np.linalg.norm(angular_residual)),
        angular_slack_norm_rad_s=float(np.linalg.norm(angular_slack)),
        angular_task_enabled=angular_task_enabled,
        planar_residual_norm_m_s=float(np.linalg.norm(residual[:2])),
        normal_residual_m_s=float(residual[2]),
        planar_slack_norm_m_s=float(np.linalg.norm(linear_slack[:2])),
        normal_slack_m_s=float(linear_slack[2]),
        residual_norm=solve.residual_norm,
        active_bound_count=solve.active_bound_count,
        solver_success=solve.success,
        solver_message=solve.message,
    )
