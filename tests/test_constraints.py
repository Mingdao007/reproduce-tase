from __future__ import annotations

import numpy as np

from tase_repro.constraints import (
    is_velocity_feasible,
    solve_constrained_velocity_least_squares,
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

