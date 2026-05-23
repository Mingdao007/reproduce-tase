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

