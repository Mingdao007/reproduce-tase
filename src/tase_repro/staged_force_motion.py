from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

from tase_repro.force_feedback import ForceMotionResult, simulate_planar_force_motion
from tase_repro.trajectories import PlanarTrajectoryState


@dataclass(frozen=True)
class StagedForceMotionResult:
    approach: ForceMotionResult
    trajectory: ForceMotionResult
    approach_reached_threshold: bool
    approach_first_threshold_index: int | None
    approach_first_threshold_time_s: float | None
    approach_final_orientation_error_rad: float
    trajectory_initial_q: np.ndarray


def stationary_planar_state(_: float) -> PlanarTrajectoryState:
    return PlanarTrajectoryState(
        displacement_m=np.zeros(2, dtype=float),
        velocity_m_s=np.zeros(2, dtype=float),
    )


def first_orientation_threshold_index(result: ForceMotionResult, threshold_rad: float) -> int | None:
    if threshold_rad < 0.0:
        raise ValueError("threshold_rad must be nonnegative")
    errors = np.linalg.norm(result.orientation_error_rotvec, axis=1)
    below = np.flatnonzero(errors <= float(threshold_rad))
    return None if len(below) == 0 else int(below[0])


def simulate_orientation_prealign_then_planar_force_motion(
    model_path: str | Path,
    *,
    initial_q: np.ndarray,
    base_z_offset_m: float,
    target_force_N: float,
    planar_trajectory: Callable[[float], PlanarTrajectoryState],
    approach_duration_s: float,
    trajectory_duration_s: float,
    dt_s: float,
    qdot_min: np.ndarray,
    qdot_max: np.ndarray,
    trajectory_qdot_min: np.ndarray | None = None,
    trajectory_qdot_max: np.ndarray | None = None,
    force_gain: float,
    r: float,
    planar_kp: float = 0.5,
    axis_weights: np.ndarray | None = None,
    slack_axis_weights: np.ndarray | None = None,
    slack_constraint_weight: float = 1e3,
    normal_velocity_mode: str = "contact_normal",
    approach_orientation_priority_mode: str = "weighted",
    approach_orientation_kp: float = 1.0,
    approach_max_angular_command_rad_s: float | None = None,
    trajectory_orientation_priority_mode: str = "linear_primary",
    trajectory_orientation_kp: float = 0.1,
    trajectory_max_angular_command_rad_s: float | None = None,
    angular_axis_weights: np.ndarray | None = None,
    angular_slack_axis_weights: np.ndarray | None = None,
    approach_joint_posture_target: np.ndarray | None = None,
    approach_joint_posture_kp: float = 0.0,
    approach_joint_posture_weight: float = 0.0,
    approach_max_joint_posture_velocity_rad_s: float | None = None,
    trajectory_joint_posture_target: np.ndarray | None = None,
    trajectory_joint_posture_kp: float = 0.0,
    trajectory_joint_posture_weight: float = 0.0,
    trajectory_max_joint_posture_velocity_rad_s: float | None = None,
    approach_orientation_threshold_rad: float = 0.03,
    site_name: str = "tcp_site_unverified_85mm",
) -> StagedForceMotionResult:
    """Run tilted-surface orientation prealignment before paper trajectory.

    Stage A holds the planar command at zero while regulating contact force and
    aligning TCP local z to the measured force normal. Stage B restarts the
    requested planar trajectory from the approach terminal q.
    """
    stage_b_qdot_min = qdot_min if trajectory_qdot_min is None else trajectory_qdot_min
    stage_b_qdot_max = qdot_max if trajectory_qdot_max is None else trajectory_qdot_max
    approach = simulate_planar_force_motion(
        model_path,
        initial_q=initial_q,
        base_z_offset_m=base_z_offset_m,
        target_force_N=target_force_N,
        planar_trajectory=stationary_planar_state,
        duration_s=approach_duration_s,
        dt_s=dt_s,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        force_gain=force_gain,
        r=r,
        planar_kp=planar_kp,
        axis_weights=axis_weights,
        slack_axis_weights=slack_axis_weights,
        slack_constraint_weight=slack_constraint_weight,
        normal_velocity_mode=normal_velocity_mode,
        orientation_mode="force_normal",
        orientation_priority_mode=approach_orientation_priority_mode,
        orientation_kp=approach_orientation_kp,
        max_angular_command_rad_s=approach_max_angular_command_rad_s,
        angular_axis_weights=angular_axis_weights,
        angular_slack_axis_weights=angular_slack_axis_weights,
        joint_posture_target=approach_joint_posture_target,
        joint_posture_kp=approach_joint_posture_kp,
        joint_posture_weight=approach_joint_posture_weight,
        max_joint_posture_velocity_rad_s=approach_max_joint_posture_velocity_rad_s,
        site_name=site_name,
    )
    threshold_index = first_orientation_threshold_index(approach, approach_orientation_threshold_rad)
    threshold_time = None if threshold_index is None else threshold_index * float(dt_s)
    final_q = approach.q[-1].copy()
    final_orientation_error = float(np.linalg.norm(approach.orientation_error_rotvec[-1]))

    trajectory = simulate_planar_force_motion(
        model_path,
        initial_q=final_q,
        base_z_offset_m=base_z_offset_m,
        target_force_N=target_force_N,
        planar_trajectory=planar_trajectory,
        duration_s=trajectory_duration_s,
        dt_s=dt_s,
        qdot_min=stage_b_qdot_min,
        qdot_max=stage_b_qdot_max,
        force_gain=force_gain,
        r=r,
        planar_kp=planar_kp,
        axis_weights=axis_weights,
        slack_axis_weights=slack_axis_weights,
        slack_constraint_weight=slack_constraint_weight,
        normal_velocity_mode=normal_velocity_mode,
        orientation_mode="force_normal",
        orientation_priority_mode=trajectory_orientation_priority_mode,
        orientation_kp=trajectory_orientation_kp,
        max_angular_command_rad_s=trajectory_max_angular_command_rad_s,
        angular_axis_weights=angular_axis_weights,
        angular_slack_axis_weights=angular_slack_axis_weights,
        joint_posture_target=trajectory_joint_posture_target,
        joint_posture_kp=trajectory_joint_posture_kp,
        joint_posture_weight=trajectory_joint_posture_weight,
        max_joint_posture_velocity_rad_s=trajectory_max_joint_posture_velocity_rad_s,
        site_name=site_name,
    )
    return StagedForceMotionResult(
        approach=approach,
        trajectory=trajectory,
        approach_reached_threshold=threshold_index is not None,
        approach_first_threshold_index=threshold_index,
        approach_first_threshold_time_s=threshold_time,
        approach_final_orientation_error_rad=final_orientation_error,
        trajectory_initial_q=final_q,
    )
