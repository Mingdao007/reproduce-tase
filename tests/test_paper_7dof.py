from __future__ import annotations

import numpy as np

from tase_repro.paper_7dof import (
    PaperSectionV7DofConfig,
    escape_velocity_bounds,
    paper_section_v_desired_position,
    plane_contact,
    simulate_paper_section_v_7dof,
    summarize_paper_section_v_7dof,
)


def test_paper_section_v_trajectory_uses_explicit_z0() -> None:
    state = paper_section_v_desired_position(0.0, z0_m=0.42)
    np.testing.assert_allclose(state, [0.2, 0.0, 0.42])


def test_plane_contact_equilibrium_force() -> None:
    penetration = 5.0 / 4.0e4
    result = plane_contact(
        np.array([0.0, 0.0, -penetration]),
        np.zeros(3),
        plane_z_m=0.0,
        plane_normal=np.array([0.0, 0.0, 1.0]),
        stiffness_N_m=4.0e4,
        damping_N_s_m=220.0,
        max_force_N=50.0,
    )
    assert result[2]
    np.testing.assert_allclose(result[1], 5.0)


def test_escape_velocity_bounds_combine_paper_limits_and_position_margin() -> None:
    lower, upper = escape_velocity_bounds(
        np.array([2.45, 0.0]),
        q_min_rad=np.array([-2.5, -2.5]),
        q_max_rad=np.array([2.5, 2.5]),
        qdot_min_rad_s=np.array([-1.5, -1.5]),
        qdot_max_rad_s=np.array([1.5, 1.5]),
        alpha=2.0,
    )
    np.testing.assert_allclose(lower, [-1.5, -1.5])
    np.testing.assert_allclose(upper, [0.1, 1.5])


def test_short_paper_7dof_diagnostic_executes_with_hard_bounds() -> None:
    config = PaperSectionV7DofConfig(duration_s=0.02, dt_s=0.002, solver_mode="pinv_bounded")
    result = simulate_paper_section_v_7dof(config)
    metrics = summarize_paper_section_v_7dof(result)
    assert result.q_rad.shape[1] == 7
    assert result.commanded_task_velocity.shape[1] == 6
    assert metrics["execution_success"]
    assert metrics["q_bound_violation_count"] == 0
    assert metrics["qdot_bound_violation_count"] == 0
    assert metrics["contact_fraction"] > 0.0


def test_contact_stabilized_pinv_diagnostic_passes_tail_force_gate() -> None:
    config = PaperSectionV7DofConfig(
        duration_s=3.0,
        dt_s=0.004,
        solver_mode="pinv_bounded",
        communication_delay_s=0.032,
        force_integral_limit=0.1,
    )
    result = simulate_paper_section_v_7dof(config)
    metrics = summarize_paper_section_v_7dof(result)
    assert metrics["execution_success"]
    assert metrics["contact_force_tail_success"]
    assert metrics["tail_contact_fraction"] == 1.0
    assert metrics["tail_force_error_mean_N"] <= 1.0
    assert metrics["q_bound_violation_count"] == 0
    assert metrics["qdot_bound_violation_count"] == 0
