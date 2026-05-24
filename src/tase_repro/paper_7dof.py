from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tase_repro.finite_time import sigr
from tase_repro.kinematics import orientation_error_rotvec
from tase_repro.orientation import rotation_aligning_local_z_to_normal
from tase_repro.panda_kinematics import panda_forward_kinematics, panda_geometric_jacobian


@dataclass(frozen=True)
class PaperSectionV7DofConfig:
    duration_s: float = 5.0
    dt_s: float = 0.002
    q0_rad: tuple[float, ...] = (
        0.0,
        -0.7853981633974483,
        0.0,
        -2.356194490192345,
        0.0,
        1.5707963267948966,
        0.7853981633974483,
    )
    radius_m: float = 0.2
    omega_rad_s: float = 0.2
    desired_force_N: float = 5.0
    epsilon: float = 0.022
    kp: float = 4.0
    ko: float = 5.0
    kf: float = 1.0
    md_kg: float = 12.0
    bd_N_s_m: float = 550.0
    finite_time_power: float = 2.0 / 3.0
    q_min_rad: float = -2.5
    q_max_rad: float = 2.5
    qdot_min_rad_s: float = -1.5
    qdot_max_rad_s: float = 1.5
    escape_velocity_alpha: float = 2.0
    communication_delay_s: float = 0.032
    max_angular_speed_rad_s: float = 1.0
    contact_stiffness_N_m: float = 4.0e4
    contact_damping_N_s_m: float = 220.0
    max_contact_force_N: float = 50.0
    force_integral_limit: float = float("inf")
    force_integral_leak: float = 0.0
    force_min_norm_N: float = 1.0e-6
    orientation_mode: str = "force_shortest_arc"
    solver_mode: str = "kkt_projection"
    force_loop_mode: str = "paper_literal"
    z0_convention: str = "q0_forward_kinematics_height"


@dataclass(frozen=True)
class PaperSectionV7DofResult:
    config: PaperSectionV7DofConfig
    t_s: np.ndarray
    q_rad: np.ndarray
    qdot_rad_s: np.ndarray
    qddot_rad_s2: np.ndarray
    lambda_1: np.ndarray
    position_m: np.ndarray
    desired_position_m: np.ndarray
    position_error_m: np.ndarray
    orientation_error_rad: np.ndarray
    task_residual_norm: np.ndarray
    force_error_N: np.ndarray
    measured_force_N: np.ndarray
    contact_active: np.ndarray
    penetration_m: np.ndarray
    commanded_task_velocity: np.ndarray
    projected_qdot_raw: np.ndarray
    projected_qdot: np.ndarray
    velocity_clamp_active: np.ndarray
    condition_number: np.ndarray
    desired_rotation_valid: np.ndarray
    z0_m: float
    plane_z_m: float


def paper_section_v_desired_position(
    t_s: float,
    *,
    z0_m: float,
    radius_m: float = 0.2,
    omega_rad_s: float = 0.2,
) -> np.ndarray:
    phase = float(omega_rad_s) * float(t_s)
    return np.array([radius_m * np.cos(phase), radius_m * np.sin(phase), z0_m], dtype=float)


def paper_section_v_desired_velocity(
    t_s: float,
    *,
    radius_m: float = 0.2,
    omega_rad_s: float = 0.2,
) -> np.ndarray:
    phase = float(omega_rad_s) * float(t_s)
    return np.array(
        [
            -radius_m * omega_rad_s * np.sin(phase),
            radius_m * omega_rad_s * np.cos(phase),
            0.0,
        ],
        dtype=float,
    )


def plane_contact(
    position_m: np.ndarray,
    linear_velocity_m_s: np.ndarray,
    *,
    plane_z_m: float,
    plane_normal: np.ndarray,
    stiffness_N_m: float,
    damping_N_s_m: float,
    max_force_N: float,
) -> tuple[float, float, bool, float, float]:
    normal = np.asarray(plane_normal, dtype=float)
    signed_distance = float(np.dot(position_m, normal) - plane_z_m)
    normal_velocity = float(np.dot(linear_velocity_m_s, normal))
    penetration = max(0.0, -signed_distance)
    if penetration <= 0.0:
        return penetration, 0.0, False, signed_distance, normal_velocity
    measured_force = max(0.0, float(stiffness_N_m) * penetration - float(damping_N_s_m) * normal_velocity)
    measured_force = min(measured_force, float(max_force_N))
    return penetration, measured_force, True, signed_distance, normal_velocity


def escape_velocity_bounds(
    q_rad: np.ndarray,
    *,
    q_min_rad: np.ndarray,
    q_max_rad: np.ndarray,
    qdot_min_rad_s: np.ndarray,
    qdot_max_rad_s: np.ndarray,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    q_array = np.asarray(q_rad, dtype=float)
    lower = np.maximum(float(alpha) * (np.asarray(q_min_rad, dtype=float) - q_array), qdot_min_rad_s)
    upper = np.minimum(float(alpha) * (np.asarray(q_max_rad, dtype=float) - q_array), qdot_max_rad_s)
    return lower, upper


def _saturate_norm(vector: np.ndarray, limit: float) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm <= float(limit):
        return vector
    return (float(limit) / max(norm, np.finfo(float).eps)) * vector


def _saturate_scalar(value: float, limit: float) -> float:
    if np.isinf(limit):
        return float(value)
    return float(np.clip(value, -float(limit), float(limit)))


def _safe_condition_number(matrix: np.ndarray) -> float:
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    if singular_values.size == 0 or singular_values[-1] <= np.finfo(float).eps:
        return float("inf")
    return float(singular_values[0] / singular_values[-1])


def _projection_target(
    jacobian: np.ndarray,
    command: np.ndarray,
    lambda_1: np.ndarray,
    *,
    solver_mode: str,
) -> np.ndarray:
    if solver_mode == "pinv_bounded":
        return np.linalg.pinv(jacobian) @ command
    if solver_mode == "kkt_projection":
        return -jacobian.T @ lambda_1
    raise ValueError("solver_mode must be 'pinv_bounded' or 'kkt_projection'")


def _desired_rotation(
    force_world_N: np.ndarray,
    previous_rotation: np.ndarray,
    *,
    press_normal: np.ndarray,
    force_min_norm_N: float,
    orientation_mode: str,
) -> tuple[np.ndarray, bool]:
    if orientation_mode == "normal_only":
        return rotation_aligning_local_z_to_normal(press_normal, reference_rotation=previous_rotation), True
    if orientation_mode != "force_shortest_arc":
        raise ValueError("orientation_mode must be 'normal_only' or 'force_shortest_arc'")
    force_norm = float(np.linalg.norm(force_world_N))
    if force_norm < float(force_min_norm_N):
        return previous_rotation, False
    desired_z_axis = -force_world_N / force_norm
    return rotation_aligning_local_z_to_normal(desired_z_axis, reference_rotation=previous_rotation), True


def simulate_paper_section_v_7dof(config: PaperSectionV7DofConfig) -> PaperSectionV7DofResult:
    if config.duration_s < 0.0:
        raise ValueError("duration_s must be nonnegative")
    if config.dt_s <= 0.0:
        raise ValueError("dt_s must be positive")
    if config.force_loop_mode != "paper_literal":
        raise ValueError("only paper_literal force_loop_mode is implemented")

    q_min = np.full(7, config.q_min_rad, dtype=float)
    q_max = np.full(7, config.q_max_rad, dtype=float)
    qdot_min = np.full(7, config.qdot_min_rad_s, dtype=float)
    qdot_max = np.full(7, config.qdot_max_rad_s, dtype=float)
    plane_normal = np.array([0.0, 0.0, 1.0], dtype=float)
    press_normal = -plane_normal
    phi_o = np.diag([1.0, 1.0, 0.0])
    phi_bar_o = np.eye(3) - phi_o

    q = np.asarray(config.q0_rad, dtype=float).copy()
    if q.shape != (7,):
        raise ValueError("q0_rad must contain seven joints")
    dq = np.zeros(7, dtype=float)
    lambda_1 = np.zeros(6, dtype=float)
    initial_pose = panda_forward_kinematics(q)
    z0 = float(initial_pose.position_m[2])
    plane_z = z0 + config.desired_force_N / config.contact_stiffness_N_m
    desired_signed_distance = float(np.dot(initial_pose.position_m, plane_normal) - plane_z)
    desired_rotation = rotation_aligning_local_z_to_normal(press_normal, reference_rotation=initial_pose.rotation)

    steps = int(np.floor(config.duration_s / config.dt_s)) + 1
    t_values = np.arange(steps, dtype=float) * config.dt_s
    arrays = {
        "q": np.zeros((steps, 7), dtype=float),
        "dq": np.zeros((steps, 7), dtype=float),
        "ddq": np.zeros((steps, 7), dtype=float),
        "lambda_1": np.zeros((steps, 6), dtype=float),
        "position": np.zeros((steps, 3), dtype=float),
        "desired_position": np.zeros((steps, 3), dtype=float),
        "position_error": np.zeros((steps, 3), dtype=float),
        "orientation_error": np.zeros((steps, 3), dtype=float),
        "task_residual": np.zeros(steps, dtype=float),
        "force_error": np.zeros(steps, dtype=float),
        "measured_force": np.zeros(steps, dtype=float),
        "contact_active": np.zeros(steps, dtype=bool),
        "penetration": np.zeros(steps, dtype=float),
        "commanded_task_velocity": np.zeros((steps, 6), dtype=float),
        "qdot_proj_raw": np.zeros((steps, 7), dtype=float),
        "qdot_proj": np.zeros((steps, 7), dtype=float),
        "velocity_clamp_active": np.zeros((steps, 7), dtype=bool),
        "condition_number": np.zeros(steps, dtype=float),
        "desired_rotation_valid": np.zeros(steps, dtype=bool),
    }

    force_integral = 0.0
    xdot_p_delay = np.zeros(3, dtype=float)
    for idx, t_s in enumerate(t_values):
        desired_position = paper_section_v_desired_position(
            t_s,
            z0_m=z0,
            radius_m=config.radius_m,
            omega_rad_s=config.omega_rad_s,
        )
        desired_velocity = paper_section_v_desired_velocity(
            t_s,
            radius_m=config.radius_m,
            omega_rad_s=config.omega_rad_s,
        )
        pose = panda_forward_kinematics(q)
        jacobian = panda_geometric_jacobian(q)
        actual_task_velocity = jacobian @ dq
        xdot_p_actual = actual_task_velocity[:3]
        penetration, measured_force, contact_active, _signed_distance, _normal_velocity = plane_contact(
            pose.position_m,
            xdot_p_actual,
            plane_z_m=plane_z,
            plane_normal=plane_normal,
            stiffness_N_m=config.contact_stiffness_N_m,
            damping_N_s_m=config.contact_damping_N_s_m,
            max_force_N=config.max_contact_force_N,
        )
        force_world = measured_force * plane_normal
        desired_rotation, rotation_valid = _desired_rotation(
            force_world,
            desired_rotation,
            press_normal=press_normal,
            force_min_norm_N=config.force_min_norm_N,
            orientation_mode=config.orientation_mode,
        )
        position_error = desired_position - pose.position_m
        if config.orientation_mode == "normal_only":
            tool_z_axis = pose.rotation[:, 2]
            orientation_error = np.cross(tool_z_axis, press_normal)
        else:
            orientation_error = orientation_error_rotvec(desired_rotation, pose.rotation)

        force_error = config.desired_force_N - measured_force
        force_integral = _saturate_scalar(
            (1.0 - config.dt_s * config.force_integral_leak) * force_integral + config.dt_s * force_error,
            config.force_integral_limit,
        )
        xdot_motion = phi_o @ (desired_velocity + config.kp * position_error)
        xdd_p = (
            -((force_error + config.kf * force_integral) / config.md_kg) * plane_normal
            - (config.bd_N_s_m / config.md_kg) * (phi_bar_o @ xdot_p_delay)
        )
        xdot_force = phi_bar_o @ (xdot_p_delay + xdd_p * config.communication_delay_s)
        xdot_p_cmd = xdot_motion + xdot_force
        xdot_o_cmd = _saturate_norm(config.ko * orientation_error, config.max_angular_speed_rad_s)
        xdot_c = np.concatenate([xdot_p_cmd, xdot_o_cmd])

        lambda_dot = (actual_task_velocity - xdot_c) / config.epsilon
        qdot_lower, qdot_upper = escape_velocity_bounds(
            q,
            q_min_rad=q_min,
            q_max_rad=q_max,
            qdot_min_rad_s=qdot_min,
            qdot_max_rad_s=qdot_max,
            alpha=config.escape_velocity_alpha,
        )
        qdot_proj_raw = _projection_target(
            jacobian,
            xdot_c,
            lambda_1,
            solver_mode=config.solver_mode,
        )
        qdot_proj = np.minimum(np.maximum(qdot_proj_raw, qdot_lower), qdot_upper)
        qddot = -(1.0 / config.epsilon) * np.asarray(sigr(dq - qdot_proj, config.finite_time_power), dtype=float)

        arrays["q"][idx, :] = q
        arrays["dq"][idx, :] = dq
        arrays["ddq"][idx, :] = qddot
        arrays["lambda_1"][idx, :] = lambda_1
        arrays["position"][idx, :] = pose.position_m
        arrays["desired_position"][idx, :] = desired_position
        arrays["position_error"][idx, :] = position_error
        arrays["orientation_error"][idx, :] = orientation_error
        arrays["task_residual"][idx] = float(np.linalg.norm(actual_task_velocity - xdot_c))
        arrays["force_error"][idx] = force_error
        arrays["measured_force"][idx] = measured_force
        arrays["contact_active"][idx] = contact_active
        arrays["penetration"][idx] = penetration
        arrays["commanded_task_velocity"][idx, :] = xdot_c
        arrays["qdot_proj_raw"][idx, :] = qdot_proj_raw
        arrays["qdot_proj"][idx, :] = qdot_proj
        arrays["velocity_clamp_active"][idx, :] = np.abs(qdot_proj - qdot_proj_raw) > 1.0e-9
        arrays["condition_number"][idx] = _safe_condition_number(jacobian)
        arrays["desired_rotation_valid"][idx] = rotation_valid

        q = np.minimum(np.maximum(q + dq * config.dt_s, q_min), q_max)
        dq = np.minimum(np.maximum(dq + qddot * config.dt_s, qdot_lower), qdot_upper)
        lambda_1 = lambda_1 + lambda_dot * config.dt_s
        xdot_p_delay = xdot_p_actual

    return PaperSectionV7DofResult(
        config=config,
        t_s=t_values,
        q_rad=arrays["q"],
        qdot_rad_s=arrays["dq"],
        qddot_rad_s2=arrays["ddq"],
        lambda_1=arrays["lambda_1"],
        position_m=arrays["position"],
        desired_position_m=arrays["desired_position"],
        position_error_m=arrays["position_error"],
        orientation_error_rad=arrays["orientation_error"],
        task_residual_norm=arrays["task_residual"],
        force_error_N=arrays["force_error"],
        measured_force_N=arrays["measured_force"],
        contact_active=arrays["contact_active"],
        penetration_m=arrays["penetration"],
        commanded_task_velocity=arrays["commanded_task_velocity"],
        projected_qdot_raw=arrays["qdot_proj_raw"],
        projected_qdot=arrays["qdot_proj"],
        velocity_clamp_active=arrays["velocity_clamp_active"],
        condition_number=arrays["condition_number"],
        desired_rotation_valid=arrays["desired_rotation_valid"],
        z0_m=z0,
        plane_z_m=plane_z,
    )


def summarize_paper_section_v_7dof(result: PaperSectionV7DofResult) -> dict[str, float | int | bool | str]:
    q_min = result.config.q_min_rad
    q_max = result.config.q_max_rad
    qdot_min = result.config.qdot_min_rad_s
    qdot_max = result.config.qdot_max_rad_s
    tail_count = max(1, int(np.ceil(0.1 * result.t_s.size)))
    tail = slice(result.t_s.size - tail_count, result.t_s.size)
    finite_arrays = [
        result.q_rad,
        result.qdot_rad_s,
        result.qddot_rad_s2,
        result.position_m,
        result.position_error_m,
        result.task_residual_norm,
        result.force_error_N,
    ]
    all_finite = all(bool(np.all(np.isfinite(array))) for array in finite_arrays)
    q_bound_violation_count = int(np.count_nonzero((result.q_rad < q_min - 1e-9) | (result.q_rad > q_max + 1e-9)))
    qdot_bound_violation_count = int(
        np.count_nonzero((result.qdot_rad_s < qdot_min - 1e-9) | (result.qdot_rad_s > qdot_max + 1e-9))
    )
    tail_contact_fraction = float(np.mean(result.contact_active[tail]))
    tail_force_error_mean_N = float(np.mean(np.abs(result.force_error_N[tail])))
    contact_force_tail_success = bool(tail_contact_fraction >= 0.99 and tail_force_error_mean_N <= 1.0)
    metrics: dict[str, float | int | bool | str] = {
        "execution_success": bool(all_finite and q_bound_violation_count == 0 and qdot_bound_violation_count == 0),
        "contact_force_tail_success": contact_force_tail_success,
        "claim_level": "paper_platform_7dof_executable_diagnostic",
        "duration_s": float(result.t_s[-1]) if result.t_s.size else 0.0,
        "dt_s": float(result.config.dt_s),
        "sample_count": int(result.t_s.size),
        "solver_mode": result.config.solver_mode,
        "orientation_mode": result.config.orientation_mode,
        "force_loop_mode": result.config.force_loop_mode,
        "z0_convention": result.config.z0_convention,
        "z0_m": float(result.z0_m),
        "plane_z_m": float(result.plane_z_m),
        "max_abs_q_rad": float(np.max(np.abs(result.q_rad))),
        "max_abs_qdot_rad_s": float(np.max(np.abs(result.qdot_rad_s))),
        "q_bound_violation_count": q_bound_violation_count,
        "qdot_bound_violation_count": qdot_bound_violation_count,
        "velocity_clamp_fraction": float(np.mean(np.any(result.velocity_clamp_active, axis=1))),
        "contact_fraction": float(np.mean(result.contact_active)),
        "tail_contact_fraction": tail_contact_fraction,
        "desired_rotation_valid_fraction": float(np.mean(result.desired_rotation_valid)),
        "task_residual_rms": float(np.sqrt(np.mean(result.task_residual_norm * result.task_residual_norm))),
        "tail_position_error_mean_m": float(np.mean(np.linalg.norm(result.position_error_m[tail, :], axis=1))),
        "tail_orientation_error_mean_rad": float(np.mean(np.linalg.norm(result.orientation_error_rad[tail, :], axis=1))),
        "tail_force_error_mean_N": tail_force_error_mean_N,
        "final_position_error_norm_m": float(np.linalg.norm(result.position_error_m[-1, :])),
        "final_orientation_error_norm_rad": float(np.linalg.norm(result.orientation_error_rad[-1, :])),
        "final_force_error_N": float(result.force_error_N[-1]),
        "max_condition_number": float(np.max(result.condition_number)),
    }
    fig6_q7_sample_time_s = 22.0
    if result.t_s.size and float(result.t_s[-1]) + 0.5 * float(result.config.dt_s) >= fig6_q7_sample_time_s:
        q7_index = int(np.argmin(np.abs(result.t_s - fig6_q7_sample_time_s)))
        q7_at_sample_rad = float(result.q_rad[q7_index, 6])
        metrics.update(
            {
                "fig6_q7_sample_time_s": float(result.t_s[q7_index]),
                "fig6_q7_at_22s_rad": q7_at_sample_rad,
                "fig6_q7_abs_error_to_2p5_rad": abs(q7_at_sample_rad - 2.5),
            }
        )
    return metrics
