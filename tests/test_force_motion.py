from __future__ import annotations

from pathlib import Path

import numpy as np

from tase_repro.force_feedback import (
    simulate_planar_force_motion,
    simulate_tangential_force_motion,
    summarize_force_motion,
)
from tase_repro.kinematics import joint_ranges, load_model
from tase_repro.trajectories import paper_e1_cycloid_planar_state

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "assets" / "mjcf" / "ur10e_nominal.xml"


def test_tangential_force_motion_holds_contact_and_moves_x() -> None:
    model = load_model(MODEL_PATH)
    q_min, q_max = joint_ranges(model)
    qdot_min = np.full(model.nv, -0.05)
    qdot_max = np.full(model.nv, 0.05)
    result = simulate_tangential_force_motion(
        MODEL_PATH,
        initial_q=np.array([0.0, -0.02, 0.03, -0.01, 0.0, 0.0]),
        base_z_offset_m=-4e-5,
        target_force_N=5.0,
        tangential_velocity_m_s=np.array([0.0005, 0.0]),
        duration_s=1.0,
        dt_s=0.002,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        force_gain=5e-5,
        r=0.5,
        tangential_kp=0.5,
    )
    summary = summarize_force_motion(
        result,
        target_force_N=5.0,
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
    )
    assert summary["solver_success_fraction"] == 1.0
    assert summary["contact_present_fraction"] == 1.0
    assert summary["final_tangential_displacement_m"][0] > 0.0
    assert summary["max_planar_velocity_residual_m_s"] >= 0.0
    assert summary["max_abs_normal_velocity_residual_m_s"] >= 0.0
    assert summary["max_planar_velocity_slack_m_s"] >= 0.0
    assert summary["max_abs_normal_velocity_slack_m_s"] >= 0.0
    assert summary["tail_mean_abs_force_error_N"] < abs(summary["initial_force_N"] - 5.0)
    assert summary["max_qdot_violation_rad_s"] == 0.0
    assert summary["max_joint_limit_violation_rad"] == 0.0


def test_paper_e1_cycloid_force_motion_holds_contact_and_tracks_y() -> None:
    model = load_model(MODEL_PATH)
    q_min, q_max = joint_ranges(model)
    qdot_min = np.full(model.nv, -0.05)
    qdot_max = np.full(model.nv, 0.05)
    result = simulate_planar_force_motion(
        MODEL_PATH,
        initial_q=np.array([0.0, -0.02, 0.03, -0.01, 0.0, 0.0]),
        base_z_offset_m=-4e-5,
        target_force_N=5.0,
        planar_trajectory=paper_e1_cycloid_planar_state,
        duration_s=1.0,
        dt_s=0.002,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        force_gain=5e-5,
        r=0.5,
        planar_kp=0.5,
    )
    summary = summarize_force_motion(
        result,
        target_force_N=5.0,
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
    )
    assert summary["solver_success_fraction"] == 1.0
    assert summary["contact_present_fraction"] == 1.0
    assert summary["desired_tangential_displacement_m"][1] > 0.0
    assert summary["final_tangential_displacement_m"][1] > 0.0
    assert summary["max_tangential_position_error_m"] < 1e-5
    assert summary["tail_mean_abs_force_error_N"] < abs(summary["initial_force_N"] - 5.0)
    assert summary["max_qdot_violation_rad_s"] == 0.0
    assert summary["max_joint_limit_violation_rad"] == 0.0


def test_planar_force_motion_accepts_normal_axis_weight() -> None:
    model = load_model(MODEL_PATH)
    q_min, q_max = joint_ranges(model)
    qdot_min = np.full(model.nv, -0.05)
    qdot_max = np.full(model.nv, 0.05)
    result = simulate_planar_force_motion(
        MODEL_PATH,
        initial_q=np.array([0.0, -0.02, 0.03, -0.01, 0.0, 0.0]),
        base_z_offset_m=-4e-5,
        target_force_N=5.0,
        planar_trajectory=paper_e1_cycloid_planar_state,
        duration_s=0.25,
        dt_s=0.002,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        force_gain=5e-5,
        r=0.5,
        planar_kp=0.5,
        axis_weights=np.array([1.0, 1.0, 10.0]),
    )
    summary = summarize_force_motion(
        result,
        target_force_N=5.0,
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
    )
    assert summary["solver_success_fraction"] == 1.0
    assert summary["contact_present_fraction"] == 1.0


def test_planar_force_motion_guard_scales_planar_command_when_force_low() -> None:
    model = load_model(MODEL_PATH)
    q_min, q_max = joint_ranges(model)
    qdot_min = np.full(model.nv, -0.05)
    qdot_max = np.full(model.nv, 0.05)
    result = simulate_planar_force_motion(
        MODEL_PATH,
        initial_q=np.array([0.0, -0.02, 0.03, -0.01, 0.0, 0.0]),
        base_z_offset_m=0.0,
        target_force_N=5.0,
        planar_trajectory=paper_e1_cycloid_planar_state,
        duration_s=0.05,
        dt_s=0.002,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        force_gain=5e-5,
        r=0.5,
        planar_kp=0.5,
        normal_guard_force_fraction=0.9,
        normal_guard_min_planar_scale=0.0,
    )
    summary = summarize_force_motion(
        result,
        target_force_N=5.0,
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
    )
    assert 0.0 < summary["min_planar_scale"] < 1.0
    assert np.max(result.planar_scale) < 1.0


def test_planar_force_motion_orientation_hold_records_metrics() -> None:
    model = load_model(MODEL_PATH)
    q_min, q_max = joint_ranges(model)
    qdot_min = np.full(model.nv, -0.15)
    qdot_max = np.full(model.nv, 0.15)
    result = simulate_planar_force_motion(
        MODEL_PATH,
        initial_q=np.array([0.0, -0.1, 0.15, -0.05, 0.0, 0.0]),
        base_z_offset_m=-0.0009710693359375,
        target_force_N=5.0,
        planar_trajectory=paper_e1_cycloid_planar_state,
        duration_s=0.1,
        dt_s=0.002,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        force_gain=5e-4,
        r=0.5,
        planar_kp=0.5,
        slack_axis_weights=np.array([1.0, 1.0, 10000.0]),
        slack_constraint_weight=1000.0,
        orientation_mode="hold",
        orientation_kp=1.0,
        angular_slack_axis_weights=np.array([1.0, 1.0, 1.0]),
    )
    summary = summarize_force_motion(
        result,
        target_force_N=5.0,
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
    )
    assert result.orientation_task_enabled
    assert result.tcp_rotation.shape[1:] == (3, 3)
    assert result.desired_tcp_rotation.shape[1:] == (3, 3)
    assert result.commanded_angular_velocity.shape == result.actual_angular_velocity.shape
    assert summary["orientation_task_enabled"] is True
    assert summary["max_orientation_error_rad"] >= 0.0
    assert summary["max_angular_velocity_slack_rad_s"] >= 0.0
