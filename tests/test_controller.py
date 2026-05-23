from __future__ import annotations

from pathlib import Path

import numpy as np

from tase_repro.controller import CartesianVelocityCommand, solve_site_linear_velocity_step
from tase_repro.kinematics import joint_ranges, load_model, make_data, set_qpos

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "assets" / "mjcf" / "ur10e_nominal.xml"
SITE = "tcp_site_unverified_85mm"


def test_controller_zero_velocity_command_returns_feasible_zero_motion() -> None:
    model = load_model(MODEL_PATH)
    data = make_data(model)
    q = np.zeros(model.nq)
    set_qpos(model, data, q)
    q_min, q_max = joint_ranges(model)
    result = solve_site_linear_velocity_step(
        model,
        data,
        site_name=SITE,
        q=q,
        command=CartesianVelocityCommand(np.zeros(3)),
        dt=0.002,
        q_min=q_min,
        q_max=q_max,
        qdot_min=np.full(model.nv, -0.05),
        qdot_max=np.full(model.nv, 0.05),
    )
    assert result.solver_success
    np.testing.assert_allclose(result.qdot, np.zeros(model.nv), atol=1e-8)
    np.testing.assert_allclose(result.actual_linear_velocity_m_s, np.zeros(3), atol=1e-8)
    np.testing.assert_allclose(result.residual_linear_velocity_m_s, np.zeros(3), atol=1e-8)
    assert result.planar_residual_norm_m_s == 0.0
    assert result.normal_residual_m_s == 0.0


def test_controller_respects_velocity_bound_for_large_command() -> None:
    model = load_model(MODEL_PATH)
    data = make_data(model)
    q = np.zeros(model.nq)
    set_qpos(model, data, q)
    q_min, q_max = joint_ranges(model)
    result = solve_site_linear_velocity_step(
        model,
        data,
        site_name=SITE,
        q=q,
        command=CartesianVelocityCommand(np.array([1.0, 0.0, 0.0])),
        dt=0.002,
        q_min=q_min,
        q_max=q_max,
        qdot_min=np.full(model.nv, -0.05),
        qdot_max=np.full(model.nv, 0.05),
    )
    assert result.solver_success
    assert np.max(np.abs(result.qdot)) <= 0.05 + 1e-9


def test_controller_axis_weights_prioritize_weighted_direction() -> None:
    model = load_model(MODEL_PATH)
    data = make_data(model)
    q = np.array([0.0, -0.02, 0.03, -0.01, 0.0, 0.0])
    set_qpos(model, data, q)
    q_min, q_max = joint_ranges(model)
    qdot_min = np.full(model.nv, -0.05)
    qdot_max = np.full(model.nv, 0.05)
    desired = np.array([0.004, 0.002, -0.0002])
    equal = solve_site_linear_velocity_step(
        model,
        data,
        site_name=SITE,
        q=q,
        command=CartesianVelocityCommand(desired),
        dt=0.002,
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
    )
    weighted = solve_site_linear_velocity_step(
        model,
        data,
        site_name=SITE,
        q=q,
        command=CartesianVelocityCommand(desired, axis_weights=np.array([1.0, 1.0, 20.0])),
        dt=0.002,
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
    )
    assert equal.solver_success
    assert weighted.solver_success
    equal_z_error = abs(equal.actual_linear_velocity_m_s[2] - desired[2])
    weighted_z_error = abs(weighted.actual_linear_velocity_m_s[2] - desired[2])
    assert weighted.planar_residual_norm_m_s >= 0.0
    assert weighted_z_error < equal_z_error
