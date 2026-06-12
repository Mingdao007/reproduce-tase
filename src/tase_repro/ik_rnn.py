from __future__ import annotations

from dataclasses import dataclass

import mujoco
import numpy as np

from tase_repro.controller import CartesianVelocityCommand, solve_site_linear_velocity_step
from tase_repro.finite_time import sigr
from tase_repro.kinematics import (
    joint_ranges,
    orientation_error_rotvec,
    set_qpos,
    site_position,
    site_rotation_matrix,
)


@dataclass(frozen=True)
class IkRnnStepRecord:
    time_s: float
    q: np.ndarray
    qdot: np.ndarray
    tcp_m: np.ndarray
    position_error_m: np.ndarray
    orientation_error_rotvec: np.ndarray
    desired_linear_velocity_m_s: np.ndarray
    actual_linear_velocity_m_s: np.ndarray
    desired_angular_velocity_rad_s: np.ndarray
    actual_angular_velocity_rad_s: np.ndarray
    solver_success: bool
    solver_message: str
    active_bound_count: int
    hidden_qdot_clip_detected: bool


@dataclass(frozen=True)
class IkRnnRunResult:
    records: list[IkRnnStepRecord]
    target_tcp_m: np.ndarray
    target_rotation: np.ndarray | None
    q_min: np.ndarray
    q_max: np.ndarray
    qdot_min: np.ndarray
    qdot_max: np.ndarray
    dt_s: float
    r: float
    linear_gain: float
    angular_gain: float
    max_linear_speed_m_s: float
    max_angular_speed_rad_s: float
    warnings: list[str]

    @property
    def final_record(self) -> IkRnnStepRecord:
        return self.records[-1]

    def metrics(self) -> dict:
        position_norm = np.asarray([np.linalg.norm(row.position_error_m) for row in self.records], dtype=float)
        orientation_norm = np.asarray(
            [np.linalg.norm(row.orientation_error_rotvec) for row in self.records], dtype=float
        )
        qdot_abs = np.asarray([np.max(np.abs(row.qdot)) for row in self.records], dtype=float)
        qdot_limits = np.maximum(np.abs(self.qdot_min), np.abs(self.qdot_max))
        qdot_limit = float(np.max(qdot_limits))
        qdot_utilization = qdot_abs / qdot_limit if qdot_limit > 0.0 else np.zeros_like(qdot_abs)
        solver_success = np.asarray([row.solver_success for row in self.records], dtype=bool)
        hidden_clip = np.asarray([row.hidden_qdot_clip_detected for row in self.records], dtype=bool)
        final_q = self.final_record.q
        joint_lower_violation = np.maximum(self.q_min - final_q, 0.0)
        joint_upper_violation = np.maximum(final_q - self.q_max, 0.0)
        return {
            "steps": int(len(self.records)),
            "duration_s": float((len(self.records) - 1) * self.dt_s),
            "dt_s": float(self.dt_s),
            "r": float(self.r),
            "linear_gain": float(self.linear_gain),
            "angular_gain": float(self.angular_gain),
            "max_linear_speed_m_s": float(self.max_linear_speed_m_s),
            "max_angular_speed_rad_s": float(self.max_angular_speed_rad_s),
            "initial_position_error_m": float(position_norm[0]),
            "final_position_error_m": float(position_norm[-1]),
            "min_position_error_m": float(np.min(position_norm)),
            "position_error_reduction_m": float(position_norm[0] - position_norm[-1]),
            "initial_orientation_error_rad": float(orientation_norm[0]),
            "final_orientation_error_rad": float(orientation_norm[-1]),
            "min_orientation_error_rad": float(np.min(orientation_norm)),
            "orientation_error_reduction_rad": float(orientation_norm[0] - orientation_norm[-1]),
            "solver_success_fraction": float(np.mean(solver_success)),
            "solver_failure_count": int(np.size(solver_success) - np.count_nonzero(solver_success)),
            "hidden_qdot_clip_count": int(np.count_nonzero(hidden_clip)),
            "qdot_limit_rad_s": qdot_limit,
            "max_abs_qdot_rad_s": float(np.max(qdot_abs)),
            "max_qdot_utilization": float(np.max(qdot_utilization)),
            "qdot_saturation_fraction_98pct": float(np.mean(qdot_utilization >= 0.98)),
            "max_joint_limit_violation_rad": float(
                max(float(np.max(joint_lower_violation)), float(np.max(joint_upper_violation)))
            ),
            "final_q": [float(x) for x in final_q],
            "target_tcp_m": [float(x) for x in self.target_tcp_m],
            "final_tcp_m": [float(x) for x in self.final_record.tcp_m],
            "warnings": list(self.warnings),
        }

    def arrays(self) -> dict[str, np.ndarray]:
        return {
            "time_s": np.asarray([row.time_s for row in self.records], dtype=float),
            "q": np.asarray([row.q for row in self.records], dtype=float),
            "qdot": np.asarray([row.qdot for row in self.records], dtype=float),
            "tcp_m": np.asarray([row.tcp_m for row in self.records], dtype=float),
            "position_error_m": np.asarray([row.position_error_m for row in self.records], dtype=float),
            "orientation_error_rotvec": np.asarray(
                [row.orientation_error_rotvec for row in self.records], dtype=float
            ),
            "desired_linear_velocity_m_s": np.asarray(
                [row.desired_linear_velocity_m_s for row in self.records], dtype=float
            ),
            "actual_linear_velocity_m_s": np.asarray(
                [row.actual_linear_velocity_m_s for row in self.records], dtype=float
            ),
            "desired_angular_velocity_rad_s": np.asarray(
                [row.desired_angular_velocity_rad_s for row in self.records], dtype=float
            ),
            "actual_angular_velocity_rad_s": np.asarray(
                [row.actual_angular_velocity_rad_s for row in self.records], dtype=float
            ),
            "solver_success": np.asarray([row.solver_success for row in self.records], dtype=bool),
            "active_bound_count": np.asarray([row.active_bound_count for row in self.records], dtype=int),
            "hidden_qdot_clip_detected": np.asarray(
                [row.hidden_qdot_clip_detected for row in self.records], dtype=bool
            ),
        }


def bounded_finite_time_velocity(
    error: np.ndarray,
    *,
    gain: float,
    r: float,
    max_norm: float,
) -> np.ndarray:
    if not 0.0 < r <= 1.0:
        raise ValueError("r must be in (0, 1]")
    if gain < 0.0:
        raise ValueError("gain must be nonnegative")
    if max_norm <= 0.0:
        raise ValueError("max_norm must be positive")
    velocity = float(gain) * np.asarray(sigr(np.asarray(error, dtype=float), float(r)), dtype=float)
    norm = float(np.linalg.norm(velocity))
    if norm > max_norm:
        velocity = velocity * (float(max_norm) / norm)
    return velocity


def run_ik_rnn_frontier(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    *,
    site_name: str,
    initial_q: np.ndarray,
    target_tcp_m: np.ndarray,
    target_rotation: np.ndarray | None,
    duration_s: float,
    dt_s: float,
    r: float,
    linear_gain: float,
    angular_gain: float,
    max_linear_speed_m_s: float,
    max_angular_speed_rad_s: float,
    qdot_limit_rad_s: float,
    linear_slack_axis_weights: np.ndarray | None = None,
    angular_slack_axis_weights: np.ndarray | None = None,
    angular_priority_mode: str = "weighted",
    slack_constraint_weight: float = 1e3,
    damping: float = 1e-6,
) -> IkRnnRunResult:
    if duration_s <= 0.0:
        raise ValueError("duration_s must be positive")
    if dt_s <= 0.0:
        raise ValueError("dt_s must be positive")
    if qdot_limit_rad_s <= 0.0:
        raise ValueError("qdot_limit_rad_s must be positive")
    q0 = np.asarray(initial_q, dtype=float)
    if q0.shape != (model.nq,):
        raise ValueError(f"initial_q shape {q0.shape} does not match model.nq={model.nq}")
    target_tcp = np.asarray(target_tcp_m, dtype=float)
    if target_tcp.shape != (3,):
        raise ValueError("target_tcp_m must have shape (3,)")
    target_rot = None if target_rotation is None else np.asarray(target_rotation, dtype=float)
    if target_rot is not None and target_rot.shape != (3, 3):
        raise ValueError("target_rotation must have shape (3, 3)")

    q_min, q_max = joint_ranges(model)
    qdot_min = np.full(model.nv, -float(qdot_limit_rad_s), dtype=float)
    qdot_max = np.full(model.nv, float(qdot_limit_rad_s), dtype=float)
    q = np.clip(q0.copy(), q_min, q_max)
    steps = int(round(float(duration_s) / float(dt_s))) + 1
    records: list[IkRnnStepRecord] = []
    linear_slack = np.ones(3, dtype=float) if linear_slack_axis_weights is None else linear_slack_axis_weights
    angular_slack = (
        np.ones(3, dtype=float) if angular_slack_axis_weights is None else angular_slack_axis_weights
    )

    for step in range(steps):
        set_qpos(model, data, q)
        tcp = site_position(model, data, site_name)
        rotation = site_rotation_matrix(model, data, site_name)
        position_error = target_tcp - tcp
        desired_linear = bounded_finite_time_velocity(
            position_error,
            gain=linear_gain,
            r=r,
            max_norm=max_linear_speed_m_s,
        )
        if target_rot is None:
            orientation_error = np.zeros(3, dtype=float)
            desired_angular = np.zeros(3, dtype=float)
            angular_velocity = None
        else:
            orientation_error = orientation_error_rotvec(target_rot, rotation)
            desired_angular = bounded_finite_time_velocity(
                orientation_error,
                gain=angular_gain,
                r=r,
                max_norm=max_angular_speed_rad_s,
            )
            angular_velocity = desired_angular
        command = CartesianVelocityCommand(
            desired_linear,
            slack_axis_weights=np.asarray(linear_slack, dtype=float),
            slack_constraint_weight=float(slack_constraint_weight),
            angular_velocity_rad_s=angular_velocity,
            angular_slack_axis_weights=np.asarray(angular_slack, dtype=float) if angular_velocity is not None else None,
            angular_priority_mode=angular_priority_mode,
        )
        solve = solve_site_linear_velocity_step(
            model,
            data,
            site_name=site_name,
            q=q,
            command=command,
            dt=dt_s,
            q_min=q_min,
            q_max=q_max,
            qdot_min=qdot_min,
            qdot_max=qdot_max,
            damping=damping,
        )
        hidden_clip = bool(np.any(solve.qdot < qdot_min - 1e-10) or np.any(solve.qdot > qdot_max + 1e-10))
        records.append(
            IkRnnStepRecord(
                time_s=float(step * dt_s),
                q=q.copy(),
                qdot=solve.qdot.copy(),
                tcp_m=tcp.copy(),
                position_error_m=position_error.copy(),
                orientation_error_rotvec=orientation_error.copy(),
                desired_linear_velocity_m_s=desired_linear.copy(),
                actual_linear_velocity_m_s=solve.actual_linear_velocity_m_s.copy(),
                desired_angular_velocity_rad_s=desired_angular.copy(),
                actual_angular_velocity_rad_s=solve.actual_angular_velocity_rad_s.copy(),
                solver_success=bool(solve.solver_success),
                solver_message=solve.solver_message,
                active_bound_count=int(solve.active_bound_count),
                hidden_qdot_clip_detected=hidden_clip,
            )
        )
        q = np.clip(q + solve.qdot * dt_s, q_min, q_max)

    warnings = [
        "offline IK/RNN frontier only",
        "uses velocity-level constrained IK, not live UR control",
        "does not close strict paper-equivalent, robustness, contact-model, or hardware gates",
    ]
    return IkRnnRunResult(
        records=records,
        target_tcp_m=target_tcp.copy(),
        target_rotation=None if target_rot is None else target_rot.copy(),
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        dt_s=float(dt_s),
        r=float(r),
        linear_gain=float(linear_gain),
        angular_gain=float(angular_gain),
        max_linear_speed_m_s=float(max_linear_speed_m_s),
        max_angular_speed_rad_s=float(max_angular_speed_rad_s),
        warnings=warnings,
    )
