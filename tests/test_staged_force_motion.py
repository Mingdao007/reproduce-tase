from __future__ import annotations

from pathlib import Path

import numpy as np

from tase_repro.force_feedback import summarize_force_motion
from tase_repro.kinematics import joint_ranges, load_model
from tase_repro.staged_force_motion import (
    first_orientation_threshold_index,
    simulate_orientation_prealign_then_planar_force_motion,
)
from tase_repro.trajectories import paper_e1_cycloid_planar_state

ROOT = Path(__file__).resolve().parents[1]
TILTED_MODEL_PATH = ROOT / "assets" / "mjcf" / "ur10e_tilted_plane_10deg.xml"


def test_staged_prealignment_reduces_trajectory_orientation_error() -> None:
    model = load_model(TILTED_MODEL_PATH)
    q_min, q_max = joint_ranges(model)
    qdot_min = np.full(model.nv, -0.15)
    qdot_max = np.full(model.nv, 0.15)
    staged = simulate_orientation_prealign_then_planar_force_motion(
        TILTED_MODEL_PATH,
        initial_q=np.array([0.0, -0.1, 0.15, -0.05, 0.0, 0.0]),
        base_z_offset_m=-0.0011631221220595766,
        target_force_N=5.0,
        planar_trajectory=lambda t_s: paper_e1_cycloid_planar_state(t_s, time_scale=0.075),
        approach_duration_s=1.2,
        trajectory_duration_s=0.1,
        dt_s=0.002,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        force_gain=5e-4,
        r=0.5,
        planar_kp=0.5,
        slack_axis_weights=np.array([1.0, 1.0, 10000.0]),
        slack_constraint_weight=1000.0,
        normal_velocity_mode="contact_normal",
        approach_orientation_priority_mode="weighted",
        approach_orientation_kp=2.0,
        trajectory_orientation_priority_mode="linear_primary",
        trajectory_orientation_kp=0.1,
        angular_axis_weights=np.ones(3),
        angular_slack_axis_weights=np.ones(3),
        approach_orientation_threshold_rad=0.03,
    )
    trajectory_summary = summarize_force_motion(
        staged.trajectory,
        target_force_N=5.0,
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
    )
    assert staged.approach_reached_threshold
    assert staged.approach_first_threshold_time_s is not None
    assert staged.approach_final_orientation_error_rad < 0.03
    assert trajectory_summary["max_orientation_error_rad"] < 0.03
    assert trajectory_summary["max_qdot_violation_rad_s"] == 0.0


def test_first_orientation_threshold_index_rejects_negative_threshold() -> None:
    class Result:
        orientation_error_rotvec = np.zeros((1, 3), dtype=float)

    try:
        first_orientation_threshold_index(Result(), -1.0)
    except ValueError as exc:
        assert "threshold_rad" in str(exc)
    else:
        raise AssertionError("negative threshold should raise ValueError")


def test_staged_approach_angular_command_cap_limits_command_norm() -> None:
    model = load_model(TILTED_MODEL_PATH)
    qdot_min = np.full(model.nv, -0.15)
    qdot_max = np.full(model.nv, 0.15)
    cap_rad_s = 0.01
    staged = simulate_orientation_prealign_then_planar_force_motion(
        TILTED_MODEL_PATH,
        initial_q=np.array([0.0, -0.1, 0.15, -0.05, 0.0, 0.0]),
        base_z_offset_m=-0.0011631221220595766,
        target_force_N=5.0,
        planar_trajectory=lambda t_s: paper_e1_cycloid_planar_state(t_s, time_scale=0.075),
        approach_duration_s=0.02,
        trajectory_duration_s=0.02,
        dt_s=0.002,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        force_gain=5e-4,
        r=0.5,
        planar_kp=0.5,
        slack_axis_weights=np.array([1.0, 1.0, 10000.0]),
        slack_constraint_weight=1000.0,
        normal_velocity_mode="contact_normal",
        approach_orientation_priority_mode="weighted",
        approach_orientation_kp=2.0,
        approach_max_angular_command_rad_s=cap_rad_s,
        trajectory_orientation_priority_mode="linear_primary",
        trajectory_orientation_kp=0.1,
        angular_axis_weights=np.ones(3),
        angular_slack_axis_weights=np.ones(3),
    )
    commanded_norm = np.linalg.norm(staged.approach.commanded_angular_velocity, axis=1)
    assert np.max(commanded_norm) <= cap_rad_s + 1e-12


def test_staged_approach_angular_command_cap_rejects_negative_value() -> None:
    model = load_model(TILTED_MODEL_PATH)
    qdot_min = np.full(model.nv, -0.15)
    qdot_max = np.full(model.nv, 0.15)
    try:
        simulate_orientation_prealign_then_planar_force_motion(
            TILTED_MODEL_PATH,
            initial_q=np.array([0.0, -0.1, 0.15, -0.05, 0.0, 0.0]),
            base_z_offset_m=-0.0011631221220595766,
            target_force_N=5.0,
            planar_trajectory=lambda t_s: paper_e1_cycloid_planar_state(t_s, time_scale=0.075),
            approach_duration_s=0.02,
            trajectory_duration_s=0.02,
            dt_s=0.002,
            qdot_min=qdot_min,
            qdot_max=qdot_max,
            force_gain=5e-4,
            r=0.5,
            planar_kp=0.5,
            slack_axis_weights=np.array([1.0, 1.0, 10000.0]),
            slack_constraint_weight=1000.0,
            normal_velocity_mode="contact_normal",
            approach_orientation_priority_mode="weighted",
            approach_orientation_kp=2.0,
            approach_max_angular_command_rad_s=-0.01,
            trajectory_orientation_priority_mode="linear_primary",
            trajectory_orientation_kp=0.1,
            angular_axis_weights=np.ones(3),
            angular_slack_axis_weights=np.ones(3),
        )
    except ValueError as exc:
        assert "max_angular_command_rad_s" in str(exc)
    else:
        raise AssertionError("negative angular command cap should raise ValueError")


def test_staged_supports_separate_trajectory_qdot_limits() -> None:
    model = load_model(TILTED_MODEL_PATH)
    approach_qdot_min = np.full(model.nv, -0.3)
    approach_qdot_max = np.full(model.nv, 0.3)
    trajectory_qdot_min = np.full(model.nv, -0.05)
    trajectory_qdot_max = np.full(model.nv, 0.05)
    staged = simulate_orientation_prealign_then_planar_force_motion(
        TILTED_MODEL_PATH,
        initial_q=np.array([0.0, -0.1, 0.15, -0.05, 0.0, 0.0]),
        base_z_offset_m=-0.0011631221220595766,
        target_force_N=5.0,
        planar_trajectory=lambda t_s: paper_e1_cycloid_planar_state(t_s, time_scale=0.075),
        approach_duration_s=0.02,
        trajectory_duration_s=0.02,
        dt_s=0.002,
        qdot_min=approach_qdot_min,
        qdot_max=approach_qdot_max,
        trajectory_qdot_min=trajectory_qdot_min,
        trajectory_qdot_max=trajectory_qdot_max,
        force_gain=5e-4,
        r=0.5,
        planar_kp=0.5,
        slack_axis_weights=np.array([1.0, 1.0, 10000.0]),
        slack_constraint_weight=1000.0,
        normal_velocity_mode="contact_normal",
        approach_orientation_priority_mode="weighted",
        approach_orientation_kp=2.0,
        trajectory_orientation_priority_mode="linear_primary",
        trajectory_orientation_kp=0.1,
        angular_axis_weights=np.ones(3),
        angular_slack_axis_weights=np.ones(3),
    )
    assert np.max(np.abs(staged.approach.qdot)) <= 0.3 + 1e-12
    assert np.max(np.abs(staged.trajectory.qdot)) <= 0.05 + 1e-12
