from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from tase_repro.ik_rnn import bounded_finite_time_velocity, run_ik_rnn_frontier
from tase_repro.kinematics import load_model, make_data, set_qpos, site_position, site_rotation_matrix

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "assets" / "mjcf" / "ur10e_nominal.xml"
SITE = "tcp_site_unverified_85mm"


def rotation_matrix_from_z(theta: float) -> np.ndarray:
    c = np.cos(theta)
    s = np.sin(theta)
    return np.asarray([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]], dtype=float)


def test_bounded_finite_time_velocity_preserves_direction_and_norm_cap() -> None:
    error = np.array([4.0, 0.0, 0.0])
    velocity = bounded_finite_time_velocity(error, gain=2.0, r=0.5, max_norm=1.5)
    np.testing.assert_allclose(velocity, np.array([1.5, 0.0, 0.0]))


def test_bounded_finite_time_velocity_rejects_invalid_exponent() -> None:
    with pytest.raises(ValueError, match="r"):
        bounded_finite_time_velocity(np.ones(3), gain=1.0, r=0.0, max_norm=1.0)


def test_ik_rnn_frontier_reduces_position_error_with_qdot_bounds() -> None:
    model = load_model(MODEL_PATH)
    data = make_data(model)
    q0 = np.array([0.1, -0.4, 0.3, -0.2, 0.15, 0.0])
    set_qpos(model, data, q0)
    target = site_position(model, data, SITE) + np.array([0.001, -0.0005, 0.0002])
    result = run_ik_rnn_frontier(
        model,
        data,
        site_name=SITE,
        initial_q=q0,
        target_tcp_m=target,
        target_rotation=None,
        duration_s=0.8,
        dt_s=0.01,
        r=0.5,
        linear_gain=0.05,
        angular_gain=0.0,
        max_linear_speed_m_s=0.02,
        max_angular_speed_rad_s=0.01,
        qdot_limit_rad_s=0.5,
    )
    metrics = result.metrics()
    assert metrics["final_position_error_m"] < metrics["initial_position_error_m"]
    assert metrics["solver_success_fraction"] == 1.0
    assert metrics["hidden_qdot_clip_count"] == 0
    assert metrics["max_abs_qdot_rad_s"] <= 0.5 + 1e-9


def test_ik_rnn_frontier_reduces_orientation_error_when_target_rotation_is_set() -> None:
    model = load_model(MODEL_PATH)
    data = make_data(model)
    q0 = np.array([0.1, -0.4, 0.3, -0.2, 0.15, 0.0])
    set_qpos(model, data, q0)
    target_tcp = site_position(model, data, SITE) + np.array([0.0005, 0.0, 0.0])
    target_rotation = rotation_matrix_from_z(0.02) @ site_rotation_matrix(model, data, SITE)
    result = run_ik_rnn_frontier(
        model,
        data,
        site_name=SITE,
        initial_q=q0,
        target_tcp_m=target_tcp,
        target_rotation=target_rotation,
        duration_s=1.2,
        dt_s=0.01,
        r=0.5,
        linear_gain=0.05,
        angular_gain=0.08,
        max_linear_speed_m_s=0.02,
        max_angular_speed_rad_s=0.08,
        qdot_limit_rad_s=0.5,
        angular_priority_mode="linear_primary",
    )
    metrics = result.metrics()
    assert metrics["final_orientation_error_rad"] < metrics["initial_orientation_error_rad"]
    assert metrics["solver_success_fraction"] == 1.0
    assert metrics["hidden_qdot_clip_count"] == 0
