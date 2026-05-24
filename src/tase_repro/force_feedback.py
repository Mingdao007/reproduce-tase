from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import mujoco
import numpy as np

from tase_repro.contact import finite_time_normal_velocity_command, unit_vector
from tase_repro.contact_ladder import positive_contact_normal_force, positive_contact_normal_force_vector
from tase_repro.controller import CartesianVelocityCommand, solve_site_linear_velocity_step
from tase_repro.kinematics import (
    joint_ranges,
    load_model,
    make_data,
    orientation_error_rotvec,
    set_qpos,
    site_position,
    site_rotation_matrix,
)
from tase_repro.orientation import rotation_aligning_local_z_to_normal
from tase_repro.trajectories import PlanarTrajectoryState, linear_planar_state


@dataclass(frozen=True)
class ForceFeedbackResult:
    q: np.ndarray
    qdot: np.ndarray
    tcp: np.ndarray
    force: np.ndarray
    commanded_vz: np.ndarray
    actual_vz: np.ndarray
    solver_success: np.ndarray
    active_bounds: np.ndarray
    contact_count: np.ndarray


@dataclass(frozen=True)
class ForceMotionResult:
    q: np.ndarray
    qdot: np.ndarray
    tcp: np.ndarray
    tcp_rotation: np.ndarray
    desired_tcp: np.ndarray
    desired_tcp_rotation: np.ndarray
    orientation_error_rotvec: np.ndarray
    force: np.ndarray
    commanded_linear_velocity: np.ndarray
    commanded_angular_velocity: np.ndarray
    actual_linear_velocity: np.ndarray
    actual_angular_velocity: np.ndarray
    linear_velocity_residual: np.ndarray
    angular_velocity_residual: np.ndarray
    task_slack_linear_velocity: np.ndarray
    task_slack_angular_velocity: np.ndarray
    planar_scale: np.ndarray
    solver_success: np.ndarray
    active_bounds: np.ndarray
    contact_count: np.ndarray
    orientation_task_enabled: bool


def apply_base_z_offset(model: mujoco.MjModel, base_z_offset_m: float) -> None:
    base_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "base_link")
    if base_id < 0:
        raise ValueError("base_link body not found")
    model.body_pos[base_id, 2] += float(base_z_offset_m)


def simulate_stationary_force_feedback(
    model_path: str | Path,
    *,
    initial_q: np.ndarray,
    base_z_offset_m: float,
    target_force_N: float,
    duration_s: float,
    dt_s: float,
    qdot_min: np.ndarray,
    qdot_max: np.ndarray,
    gain: float,
    r: float,
    site_name: str = "tcp_site_unverified_85mm",
) -> ForceFeedbackResult:
    """Run a kinematic stationary normal-force feedback simulation.

    This uses MuJoCo contact force measurement and the bounded velocity solve.
    It is still simulation-only and does not model robot torque dynamics.
    """
    model = load_model(model_path)
    apply_base_z_offset(model, base_z_offset_m)
    data = make_data(model)
    q_min, q_max = joint_ranges(model)
    q = np.asarray(initial_q, dtype=float).copy()
    if q.shape != (model.nq,):
        raise ValueError(f"initial_q shape {q.shape} does not match model.nq={model.nq}")
    qdot_min = np.asarray(qdot_min, dtype=float)
    qdot_max = np.asarray(qdot_max, dtype=float)

    steps = int(round(float(duration_s) / float(dt_s)))
    q_hist = np.empty((steps, model.nq), dtype=float)
    qdot_hist = np.empty((steps, model.nv), dtype=float)
    tcp_hist = np.empty((steps, 3), dtype=float)
    force_hist = np.empty(steps, dtype=float)
    cmd_vz_hist = np.empty(steps, dtype=float)
    actual_vz_hist = np.empty(steps, dtype=float)
    solver_success = np.empty(steps, dtype=bool)
    active_bounds = np.empty(steps, dtype=int)
    contact_count = np.empty(steps, dtype=int)

    for idx in range(steps):
        set_qpos(model, data, q)
        mujoco.mj_forward(model, data)
        force = positive_contact_normal_force(model, data)
        command_vz = finite_time_normal_velocity_command(
            force,
            target_force_N,
            gain=gain,
            r=r,
        )
        step = solve_site_linear_velocity_step(
            model,
            data,
            site_name=site_name,
            q=q,
            command=CartesianVelocityCommand(np.array([0.0, 0.0, command_vz])),
            dt=dt_s,
            q_min=q_min,
            q_max=q_max,
            qdot_min=qdot_min,
            qdot_max=qdot_max,
        )
        q = q + dt_s * step.qdot
        set_qpos(model, data, q)

        q_hist[idx] = q
        qdot_hist[idx] = step.qdot
        tcp_hist[idx] = site_position(model, data, site_name)
        force_hist[idx] = force
        cmd_vz_hist[idx] = command_vz
        actual_vz_hist[idx] = step.actual_linear_velocity_m_s[2]
        solver_success[idx] = step.solver_success
        active_bounds[idx] = step.active_bound_count
        contact_count[idx] = data.ncon

    return ForceFeedbackResult(
        q=q_hist,
        qdot=qdot_hist,
        tcp=tcp_hist,
        force=force_hist,
        commanded_vz=cmd_vz_hist,
        actual_vz=actual_vz_hist,
        solver_success=solver_success,
        active_bounds=active_bounds,
        contact_count=contact_count,
    )


def summarize_force_feedback(
    result: ForceFeedbackResult,
    *,
    target_force_N: float,
    q_min: np.ndarray,
    q_max: np.ndarray,
    qdot_min: np.ndarray,
    qdot_max: np.ndarray,
    tail_fraction: float = 0.2,
) -> dict:
    tail = max(1, int(round(len(result.force) * tail_fraction)))
    force_error = result.force - float(target_force_N)
    q_violation = np.maximum(q_min - result.q, 0.0) + np.maximum(result.q - q_max, 0.0)
    qdot_violation = np.maximum(qdot_min - result.qdot, 0.0) + np.maximum(result.qdot - qdot_max, 0.0)
    return {
        "target_force_N": float(target_force_N),
        "initial_force_N": float(result.force[0]),
        "final_force_N": float(result.force[-1]),
        "tail_mean_force_N": float(np.mean(result.force[-tail:])),
        "tail_mean_abs_force_error_N": float(np.mean(np.abs(force_error[-tail:]))),
        "max_abs_force_error_N": float(np.max(np.abs(force_error))),
        "solver_success_fraction": float(np.mean(result.solver_success)),
        "contact_present_fraction": float(np.mean(result.contact_count > 0)),
        "max_active_bound_count": int(np.max(result.active_bounds)),
        "max_abs_qdot_rad_s": float(np.max(np.abs(result.qdot))),
        "max_qdot_violation_rad_s": float(np.max(qdot_violation)),
        "max_joint_limit_violation_rad": float(np.max(q_violation)),
        "max_abs_commanded_vz_m_s": float(np.max(np.abs(result.commanded_vz))),
        "max_abs_actual_vz_m_s": float(np.max(np.abs(result.actual_vz))),
    }


def simulate_tangential_force_motion(
    model_path: str | Path,
    *,
    initial_q: np.ndarray,
    base_z_offset_m: float,
    target_force_N: float,
    tangential_velocity_m_s: np.ndarray,
    duration_s: float,
    dt_s: float,
    qdot_min: np.ndarray,
    qdot_max: np.ndarray,
    force_gain: float,
    r: float,
    tangential_kp: float = 0.5,
    axis_weights: np.ndarray | None = None,
    slack_axis_weights: np.ndarray | None = None,
    slack_constraint_weight: float = 1e3,
    normal_guard_force_fraction: float | None = None,
    normal_guard_min_planar_scale: float = 0.0,
    normal_velocity_mode: str = "world_z",
    site_name: str = "tcp_site_unverified_85mm",
) -> ForceMotionResult:
    """Run a low-speed tangential motion while regulating normal force."""
    tangent = np.asarray(tangential_velocity_m_s, dtype=float)
    if tangent.shape != (2,):
        raise ValueError("tangential_velocity_m_s must have shape (2,) for x/y")
    return simulate_planar_force_motion(
        model_path,
        initial_q=initial_q,
        base_z_offset_m=base_z_offset_m,
        target_force_N=target_force_N,
        planar_trajectory=lambda t_s: linear_planar_state(t_s, tangent),
        duration_s=duration_s,
        dt_s=dt_s,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        force_gain=force_gain,
        r=r,
        planar_kp=tangential_kp,
        axis_weights=axis_weights,
        slack_axis_weights=slack_axis_weights,
        slack_constraint_weight=slack_constraint_weight,
        normal_guard_force_fraction=normal_guard_force_fraction,
        normal_guard_min_planar_scale=normal_guard_min_planar_scale,
        normal_velocity_mode=normal_velocity_mode,
        site_name=site_name,
    )


def simulate_planar_force_motion(
    model_path: str | Path,
    *,
    initial_q: np.ndarray,
    base_z_offset_m: float,
    target_force_N: float,
    planar_trajectory: Callable[[float], PlanarTrajectoryState],
    duration_s: float,
    dt_s: float,
    qdot_min: np.ndarray,
    qdot_max: np.ndarray,
    force_gain: float,
    r: float,
    planar_kp: float = 0.5,
    axis_weights: np.ndarray | None = None,
    slack_axis_weights: np.ndarray | None = None,
    slack_constraint_weight: float = 1e3,
    normal_guard_force_fraction: float | None = None,
    normal_guard_min_planar_scale: float = 0.0,
    normal_velocity_mode: str = "world_z",
    orientation_mode: str = "none",
    orientation_priority_mode: str = "weighted",
    orientation_kp: float = 1.0,
    angular_axis_weights: np.ndarray | None = None,
    angular_slack_axis_weights: np.ndarray | None = None,
    site_name: str = "tcp_site_unverified_85mm",
) -> ForceMotionResult:
    """Run an x/y trajectory while regulating normal force."""
    if orientation_mode not in {"none", "hold", "force_normal"}:
        raise ValueError("orientation_mode must be 'none', 'hold', or 'force_normal'")
    if orientation_priority_mode not in {"weighted", "linear_primary"}:
        raise ValueError("orientation_priority_mode must be 'weighted' or 'linear_primary'")
    if normal_velocity_mode not in {"world_z", "contact_normal"}:
        raise ValueError("normal_velocity_mode must be 'world_z' or 'contact_normal'")
    orientation_task_enabled = orientation_mode != "none"
    model = load_model(model_path)
    apply_base_z_offset(model, base_z_offset_m)
    data = make_data(model)
    q_min, q_max = joint_ranges(model)
    q = np.asarray(initial_q, dtype=float).copy()
    if q.shape != (model.nq,):
        raise ValueError(f"initial_q shape {q.shape} does not match model.nq={model.nq}")
    qdot_min = np.asarray(qdot_min, dtype=float)
    qdot_max = np.asarray(qdot_max, dtype=float)
    if axis_weights is None:
        solve_axis_weights = np.ones(3, dtype=float)
    else:
        solve_axis_weights = np.asarray(axis_weights, dtype=float)
        if solve_axis_weights.shape != (3,):
            raise ValueError("axis_weights must have shape (3,)")
    if slack_axis_weights is None:
        solve_slack_axis_weights = None
    else:
        solve_slack_axis_weights = np.asarray(slack_axis_weights, dtype=float)
        if solve_slack_axis_weights.shape != (3,):
            raise ValueError("slack_axis_weights must have shape (3,)")
    if angular_axis_weights is None:
        solve_angular_axis_weights = np.ones(3, dtype=float)
    else:
        solve_angular_axis_weights = np.asarray(angular_axis_weights, dtype=float)
        if solve_angular_axis_weights.shape != (3,):
            raise ValueError("angular_axis_weights must have shape (3,)")
    if angular_slack_axis_weights is None:
        solve_angular_slack_axis_weights = None
    else:
        solve_angular_slack_axis_weights = np.asarray(angular_slack_axis_weights, dtype=float)
        if solve_angular_slack_axis_weights.shape != (3,):
            raise ValueError("angular_slack_axis_weights must have shape (3,)")
    if (
        orientation_task_enabled
        and orientation_priority_mode == "weighted"
        and solve_slack_axis_weights is not None
        and solve_angular_slack_axis_weights is None
    ):
        raise ValueError("angular_slack_axis_weights are required when orientation task uses slack solve")
    guard_fraction = None if normal_guard_force_fraction is None else float(normal_guard_force_fraction)
    if guard_fraction is not None and guard_fraction <= 0.0:
        raise ValueError("normal_guard_force_fraction must be positive when set")
    guard_min_scale = float(normal_guard_min_planar_scale)
    if not 0.0 <= guard_min_scale <= 1.0:
        raise ValueError("normal_guard_min_planar_scale must be in [0, 1]")

    set_qpos(model, data, q)
    start_tcp = site_position(model, data, site_name)
    start_rotation = site_rotation_matrix(model, data, site_name)
    last_desired_rotation = start_rotation.copy()
    steps = int(round(float(duration_s) / float(dt_s)))
    q_hist = np.empty((steps, model.nq), dtype=float)
    qdot_hist = np.empty((steps, model.nv), dtype=float)
    tcp_hist = np.empty((steps, 3), dtype=float)
    tcp_rotation_hist = np.empty((steps, 3, 3), dtype=float)
    desired_tcp_hist = np.empty((steps, 3), dtype=float)
    desired_tcp_rotation_hist = np.empty((steps, 3, 3), dtype=float)
    orientation_error_hist = np.empty((steps, 3), dtype=float)
    force_hist = np.empty(steps, dtype=float)
    commanded_linear_hist = np.empty((steps, 3), dtype=float)
    commanded_angular_hist = np.empty((steps, 3), dtype=float)
    actual_linear_hist = np.empty((steps, 3), dtype=float)
    actual_angular_hist = np.empty((steps, 3), dtype=float)
    linear_residual_hist = np.empty((steps, 3), dtype=float)
    angular_residual_hist = np.empty((steps, 3), dtype=float)
    task_slack_hist = np.empty((steps, 3), dtype=float)
    task_slack_angular_hist = np.empty((steps, 3), dtype=float)
    planar_scale_hist = np.empty(steps, dtype=float)
    solver_success = np.empty(steps, dtype=bool)
    active_bounds = np.empty(steps, dtype=int)
    contact_count = np.empty(steps, dtype=int)

    for idx in range(steps):
        t = idx * float(dt_s)
        set_qpos(model, data, q)
        mujoco.mj_forward(model, data)
        tcp = site_position(model, data, site_name)
        current_rotation = site_rotation_matrix(model, data, site_name)
        trajectory_state = planar_trajectory(t)
        planar_displacement = np.asarray(trajectory_state.displacement_m, dtype=float)
        planar_velocity = np.asarray(trajectory_state.velocity_m_s, dtype=float)
        if planar_displacement.shape != (2,) or planar_velocity.shape != (2,):
            raise ValueError("planar trajectory must return x/y displacement and velocity")
        desired_tcp = start_tcp.copy()
        desired_tcp[:2] += planar_displacement

        tangential_error = desired_tcp[:2] - tcp[:2]
        tangential_cmd = planar_velocity + float(planar_kp) * tangential_error
        force = positive_contact_normal_force(model, data)
        force_vector = positive_contact_normal_force_vector(model, data)
        planar_scale = 1.0
        if guard_fraction is not None:
            threshold = abs(float(target_force_N)) * guard_fraction
            planar_scale = float(np.clip(force / threshold, guard_min_scale, 1.0))
            tangential_cmd = planar_scale * tangential_cmd
        command_vz = finite_time_normal_velocity_command(
            force,
            target_force_N,
            gain=force_gain,
            r=r,
        )
        if normal_velocity_mode == "contact_normal" and np.linalg.norm(force_vector) > 1e-9:
            normal_direction = unit_vector(force_vector)
            normal_command = command_vz * normal_direction
        else:
            normal_command = np.array([0.0, 0.0, command_vz], dtype=float)
        command = np.array([tangential_cmd[0], tangential_cmd[1], 0.0]) + normal_command
        if orientation_mode == "hold":
            desired_rotation = start_rotation
            pre_step_orientation_error = orientation_error_rotvec(desired_rotation, current_rotation)
            angular_command = float(orientation_kp) * pre_step_orientation_error
        elif orientation_mode == "force_normal":
            if np.linalg.norm(force_vector) > 1e-9:
                desired_rotation = rotation_aligning_local_z_to_normal(
                    force_vector,
                    reference_rotation=start_rotation,
                )
                last_desired_rotation = desired_rotation
            else:
                desired_rotation = last_desired_rotation
            pre_step_orientation_error = orientation_error_rotvec(desired_rotation, current_rotation)
            angular_command = float(orientation_kp) * pre_step_orientation_error
        else:
            desired_rotation = current_rotation
            angular_command = None
        step = solve_site_linear_velocity_step(
            model,
            data,
            site_name=site_name,
            q=q,
            command=CartesianVelocityCommand(
                command,
                axis_weights=solve_axis_weights,
                slack_axis_weights=solve_slack_axis_weights,
                slack_constraint_weight=slack_constraint_weight,
                angular_velocity_rad_s=angular_command,
                angular_axis_weights=solve_angular_axis_weights,
                angular_slack_axis_weights=solve_angular_slack_axis_weights,
                angular_priority_mode=orientation_priority_mode,
            ),
            dt=dt_s,
            q_min=q_min,
            q_max=q_max,
            qdot_min=qdot_min,
            qdot_max=qdot_max,
        )
        q = q + dt_s * step.qdot
        set_qpos(model, data, q)
        post_step_rotation = site_rotation_matrix(model, data, site_name)

        q_hist[idx] = q
        qdot_hist[idx] = step.qdot
        tcp_hist[idx] = site_position(model, data, site_name)
        tcp_rotation_hist[idx] = post_step_rotation
        desired_tcp_hist[idx] = desired_tcp
        desired_tcp_rotation_hist[idx] = desired_rotation
        orientation_error_hist[idx] = (
            orientation_error_rotvec(desired_rotation, post_step_rotation)
            if orientation_task_enabled
            else np.zeros(3, dtype=float)
        )
        force_hist[idx] = force
        commanded_linear_hist[idx] = command
        commanded_angular_hist[idx] = np.zeros(3, dtype=float) if angular_command is None else angular_command
        actual_linear_hist[idx] = step.actual_linear_velocity_m_s
        actual_angular_hist[idx] = step.actual_angular_velocity_rad_s
        linear_residual_hist[idx] = step.residual_linear_velocity_m_s
        angular_residual_hist[idx] = step.residual_angular_velocity_rad_s
        task_slack_hist[idx] = step.task_slack_linear_velocity_m_s
        task_slack_angular_hist[idx] = step.task_slack_angular_velocity_rad_s
        planar_scale_hist[idx] = planar_scale
        solver_success[idx] = step.solver_success
        active_bounds[idx] = step.active_bound_count
        contact_count[idx] = data.ncon

    return ForceMotionResult(
        q=q_hist,
        qdot=qdot_hist,
        tcp=tcp_hist,
        tcp_rotation=tcp_rotation_hist,
        desired_tcp=desired_tcp_hist,
        desired_tcp_rotation=desired_tcp_rotation_hist,
        orientation_error_rotvec=orientation_error_hist,
        force=force_hist,
        commanded_linear_velocity=commanded_linear_hist,
        commanded_angular_velocity=commanded_angular_hist,
        actual_linear_velocity=actual_linear_hist,
        actual_angular_velocity=actual_angular_hist,
        linear_velocity_residual=linear_residual_hist,
        angular_velocity_residual=angular_residual_hist,
        task_slack_linear_velocity=task_slack_hist,
        task_slack_angular_velocity=task_slack_angular_hist,
        planar_scale=planar_scale_hist,
        solver_success=solver_success,
        active_bounds=active_bounds,
        contact_count=contact_count,
        orientation_task_enabled=orientation_task_enabled,
    )


def summarize_force_motion(
    result: ForceMotionResult,
    *,
    target_force_N: float,
    q_min: np.ndarray,
    q_max: np.ndarray,
    qdot_min: np.ndarray,
    qdot_max: np.ndarray,
    tail_fraction: float = 0.2,
) -> dict:
    tail = max(1, int(round(len(result.force) * tail_fraction)))
    force_error = result.force - float(target_force_N)
    tangential_error = result.tcp[:, :2] - result.desired_tcp[:, :2]
    planar_velocity_residual = np.linalg.norm(result.linear_velocity_residual[:, :2], axis=1)
    normal_velocity_residual = result.linear_velocity_residual[:, 2]
    planar_velocity_slack = np.linalg.norm(result.task_slack_linear_velocity[:, :2], axis=1)
    normal_velocity_slack = result.task_slack_linear_velocity[:, 2]
    orientation_error = np.linalg.norm(result.orientation_error_rotvec, axis=1)
    angular_velocity_residual = np.linalg.norm(result.angular_velocity_residual, axis=1)
    angular_velocity_slack = np.linalg.norm(result.task_slack_angular_velocity, axis=1)
    q_violation = np.maximum(q_min - result.q, 0.0) + np.maximum(result.q - q_max, 0.0)
    qdot_violation = np.maximum(qdot_min - result.qdot, 0.0) + np.maximum(result.qdot - qdot_max, 0.0)
    qdot_abs_limits = np.minimum(np.abs(qdot_min), np.abs(qdot_max))
    valid_qdot_limits = np.isfinite(qdot_abs_limits) & (qdot_abs_limits > 0.0)
    if np.any(valid_qdot_limits):
        qdot_utilization = np.max(
            np.abs(result.qdot[:, valid_qdot_limits]) / qdot_abs_limits[valid_qdot_limits],
            axis=1,
        )
    else:
        qdot_utilization = np.zeros(len(result.force), dtype=float)
    qdot_saturation_threshold = 0.98
    displacement = result.tcp[-1, :2] - result.tcp[0, :2]
    desired_displacement = result.desired_tcp[-1, :2] - result.desired_tcp[0, :2]
    return {
        "target_force_N": float(target_force_N),
        "initial_force_N": float(result.force[0]),
        "final_force_N": float(result.force[-1]),
        "tail_mean_force_N": float(np.mean(result.force[-tail:])),
        "tail_mean_abs_force_error_N": float(np.mean(np.abs(force_error[-tail:]))),
        "max_abs_force_error_N": float(np.max(np.abs(force_error))),
        "mean_tangential_position_error_m": float(np.mean(np.linalg.norm(tangential_error, axis=1))),
        "max_tangential_position_error_m": float(np.max(np.linalg.norm(tangential_error, axis=1))),
        "final_tangential_displacement_m": [float(x) for x in displacement],
        "desired_tangential_displacement_m": [float(x) for x in desired_displacement],
        "solver_success_fraction": float(np.mean(result.solver_success)),
        "contact_present_fraction": float(np.mean(result.contact_count > 0)),
        "max_active_bound_count": int(np.max(result.active_bounds)),
        "min_planar_scale": float(np.min(result.planar_scale)),
        "tail_mean_planar_scale": float(np.mean(result.planar_scale[-tail:])),
        "mean_planar_velocity_residual_m_s": float(np.mean(planar_velocity_residual)),
        "max_planar_velocity_residual_m_s": float(np.max(planar_velocity_residual)),
        "tail_mean_planar_velocity_residual_m_s": float(np.mean(planar_velocity_residual[-tail:])),
        "mean_abs_normal_velocity_residual_m_s": float(np.mean(np.abs(normal_velocity_residual))),
        "max_abs_normal_velocity_residual_m_s": float(np.max(np.abs(normal_velocity_residual))),
        "tail_mean_abs_normal_velocity_residual_m_s": float(np.mean(np.abs(normal_velocity_residual[-tail:]))),
        "mean_planar_velocity_slack_m_s": float(np.mean(planar_velocity_slack)),
        "max_planar_velocity_slack_m_s": float(np.max(planar_velocity_slack)),
        "tail_mean_planar_velocity_slack_m_s": float(np.mean(planar_velocity_slack[-tail:])),
        "mean_abs_normal_velocity_slack_m_s": float(np.mean(np.abs(normal_velocity_slack))),
        "max_abs_normal_velocity_slack_m_s": float(np.max(np.abs(normal_velocity_slack))),
        "tail_mean_abs_normal_velocity_slack_m_s": float(np.mean(np.abs(normal_velocity_slack[-tail:]))),
        "orientation_task_enabled": bool(result.orientation_task_enabled),
        "mean_orientation_error_rad": float(np.mean(orientation_error)),
        "max_orientation_error_rad": float(np.max(orientation_error)),
        "tail_mean_orientation_error_rad": float(np.mean(orientation_error[-tail:])),
        "mean_angular_velocity_residual_rad_s": float(np.mean(angular_velocity_residual)),
        "max_angular_velocity_residual_rad_s": float(np.max(angular_velocity_residual)),
        "tail_mean_angular_velocity_residual_rad_s": float(np.mean(angular_velocity_residual[-tail:])),
        "mean_angular_velocity_slack_rad_s": float(np.mean(angular_velocity_slack)),
        "max_angular_velocity_slack_rad_s": float(np.max(angular_velocity_slack)),
        "tail_mean_angular_velocity_slack_rad_s": float(np.mean(angular_velocity_slack[-tail:])),
        "max_qdot_utilization": float(np.max(qdot_utilization)),
        "tail_max_qdot_utilization": float(np.max(qdot_utilization[-tail:])),
        "qdot_saturation_threshold": qdot_saturation_threshold,
        "qdot_saturation_fraction": float(np.mean(qdot_utilization >= qdot_saturation_threshold)),
        "tail_qdot_saturation_fraction": float(np.mean(qdot_utilization[-tail:] >= qdot_saturation_threshold)),
        "max_abs_qdot_rad_s": float(np.max(np.abs(result.qdot))),
        "max_qdot_violation_rad_s": float(np.max(qdot_violation)),
        "max_joint_limit_violation_rad": float(np.max(q_violation)),
        "max_abs_commanded_linear_velocity_m_s": float(np.max(np.linalg.norm(result.commanded_linear_velocity, axis=1))),
        "max_abs_actual_linear_velocity_m_s": float(np.max(np.linalg.norm(result.actual_linear_velocity, axis=1))),
        "max_abs_commanded_angular_velocity_rad_s": float(
            np.max(np.linalg.norm(result.commanded_angular_velocity, axis=1))
        ),
        "max_abs_actual_angular_velocity_rad_s": float(np.max(np.linalg.norm(result.actual_angular_velocity, axis=1))),
    }
