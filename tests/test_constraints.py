from __future__ import annotations

import numpy as np

from tase_repro.constraints import (
    is_velocity_feasible,
    solve_constrained_velocity_least_squares,
    solve_linear_primary_angular_secondary_with_slack,
    solve_primary_secondary_with_slack,
    step_velocity_bounds,
)


def test_step_velocity_bounds_combine_velocity_and_position_limits() -> None:
    q = np.array([0.95, 0.0])
    lower, upper = step_velocity_bounds(
        q,
        dt=0.1,
        q_min=np.array([-1.0, -1.0]),
        q_max=np.array([1.0, 1.0]),
        qdot_min=np.array([-2.0, -2.0]),
        qdot_max=np.array([2.0, 2.0]),
        margin=0.0,
    )
    np.testing.assert_allclose(lower, [-2.0, -2.0])
    np.testing.assert_allclose(upper, [0.5, 2.0])


def test_solver_respects_hard_bounds_inside_optimization() -> None:
    A = np.eye(2)
    b = np.array([10.0, -10.0])
    q = np.zeros(2)
    qdot_min = np.array([-0.05, -0.05])
    qdot_max = np.array([0.05, 0.05])
    result = solve_constrained_velocity_least_squares(
        A,
        b,
        q=q,
        dt=0.01,
        q_min=np.array([-1.0, -1.0]),
        q_max=np.array([1.0, 1.0]),
        qdot_min=qdot_min,
        qdot_max=qdot_max,
    )
    assert result.success
    np.testing.assert_allclose(result.qdot, [0.05, -0.05], atol=1e-8)
    assert result.active_bound_count == 2
    assert is_velocity_feasible(
        q,
        result.qdot,
        dt=0.01,
        q_min=np.array([-1.0, -1.0]),
        q_max=np.array([1.0, 1.0]),
        qdot_min=qdot_min,
        qdot_max=qdot_max,
    )


def test_solver_reports_infeasible_bounds() -> None:
    result = solve_constrained_velocity_least_squares(
        np.eye(1),
        np.array([0.0]),
        q=np.array([1.1]),
        dt=0.1,
        q_min=np.array([-1.0]),
        q_max=np.array([1.0]),
        qdot_min=np.array([0.0]),
        qdot_max=np.array([0.1]),
    )
    assert not result.success
    assert result.message == "infeasible bounds"


def test_solver_damping_target_biases_free_velocity_variable_and_respects_bounds() -> None:
    result = solve_constrained_velocity_least_squares(
        np.array([[1.0, 0.0]]),
        np.array([0.2]),
        q=np.zeros(2),
        dt=0.01,
        q_min=np.full(2, -1.0),
        q_max=np.full(2, 1.0),
        qdot_min=np.array([-1.0, -0.05]),
        qdot_max=np.array([1.0, 0.05]),
        damping=1.0,
        damping_target=np.array([0.2, 0.4]),
    )
    assert result.success
    np.testing.assert_allclose(result.qdot, [0.2, 0.05], atol=1e-8)
    assert result.active_bound_count == 1


def test_linear_primary_angular_secondary_preserves_primary_rows() -> None:
    linear_A = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    linear_b = np.array([0.1, -0.2])
    angular_A = np.array([[0.0, 0.0, 1.0]])
    angular_b = np.array([0.3])
    result = solve_linear_primary_angular_secondary_with_slack(
        linear_A,
        linear_b,
        angular_A,
        angular_b,
        q=np.zeros(3),
        dt=0.01,
        q_min=np.full(3, -1.0),
        q_max=np.full(3, 1.0),
        qdot_min=np.full(3, -1.0),
        qdot_max=np.full(3, 1.0),
        linear_slack_weights=np.ones(2),
        angular_axis_weights=np.ones(1),
    )
    assert result.success
    np.testing.assert_allclose(linear_A @ result.qdot, linear_b, atol=1e-7)
    np.testing.assert_allclose(angular_A @ result.qdot, angular_b, atol=1e-7)
    np.testing.assert_allclose(result.slack, np.zeros(3), atol=1e-7)


def test_linear_primary_angular_secondary_uses_damping_target_in_secondary_nullspace() -> None:
    result = solve_linear_primary_angular_secondary_with_slack(
        np.array([[1.0, 0.0]]),
        np.array([0.1]),
        np.array([[0.0, 1.0]]),
        np.array([0.0]),
        q=np.zeros(2),
        dt=0.01,
        q_min=np.full(2, -1.0),
        q_max=np.full(2, 1.0),
        qdot_min=np.full(2, -1.0),
        qdot_max=np.full(2, 1.0),
        linear_slack_weights=np.ones(1),
        angular_axis_weights=np.zeros(1),
        damping=1e-8,
        damping_target=np.array([0.1, 0.25]),
        secondary_damping=1.0,
    )
    assert result.success
    np.testing.assert_allclose(result.qdot, [0.1, 0.25], atol=1e-7)
    np.testing.assert_allclose(np.array([[1.0, 0.0]]) @ result.qdot, [0.1], atol=1e-7)


def test_primary_secondary_solver_preserves_primary_rows_and_optimizes_secondary() -> None:
    result = solve_primary_secondary_with_slack(
        np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
        np.array([0.1, -0.2]),
        np.array([[0.0, 0.0, 1.0]]),
        np.array([0.3]),
        q=np.zeros(3),
        dt=0.01,
        q_min=np.full(3, -1.0),
        q_max=np.full(3, 1.0),
        qdot_min=np.full(3, -1.0),
        qdot_max=np.full(3, 1.0),
        primary_slack_weights=np.ones(2),
        secondary_axis_weights=np.ones(1),
    )
    assert result.success
    np.testing.assert_allclose(result.qdot, [0.1, -0.2, 0.3], atol=1e-7)
    np.testing.assert_allclose(result.slack, np.zeros(3), atol=1e-7)
