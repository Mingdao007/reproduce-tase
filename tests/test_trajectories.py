from __future__ import annotations

import pytest
import numpy as np

from tase_repro.trajectories import (
    linear_planar_state,
    paper_e1_cycloid_planar_state,
    paper_e2_figure_eight_planar_state,
    paper_e3_circle_planar_state,
    paper_e4_cardioid_planar_state,
)


def test_linear_planar_state() -> None:
    state = linear_planar_state(2.0, np.array([0.1, -0.2]))
    np.testing.assert_allclose(state.displacement_m, [0.2, -0.4])
    np.testing.assert_allclose(state.velocity_m_s, [0.1, -0.2])


def test_paper_e1_cycloid_state_matches_formula_and_derivative() -> None:
    t_s = 4.0
    amplitude = 0.015
    omega = 0.1
    phase = omega * t_s
    state = paper_e1_cycloid_planar_state(t_s, amplitude_m=amplitude, omega_rad_s=omega)
    np.testing.assert_allclose(
        state.displacement_m,
        [
            amplitude * (phase - np.sin(phase)),
            amplitude * (1.0 - np.cos(phase)),
        ],
    )
    np.testing.assert_allclose(
        state.velocity_m_s,
        [
            amplitude * omega * (1.0 - np.cos(phase)),
            amplitude * omega * np.sin(phase),
        ],
    )


def test_paper_e2_figure_eight_state_matches_formula_and_derivative() -> None:
    t_s = 3.0
    ax = 0.04
    ay = 0.01
    omega = 0.1
    phase = omega * t_s
    state = paper_e2_figure_eight_planar_state(
        t_s,
        amplitude_x_m=ax,
        amplitude_y_m=ay,
        omega_rad_s=omega,
    )
    np.testing.assert_allclose(state.displacement_m, [ax * np.sin(phase), ay * np.sin(2.0 * phase)])
    np.testing.assert_allclose(
        state.velocity_m_s,
        [
            ax * omega * np.cos(phase),
            ay * 2.0 * omega * np.cos(2.0 * phase),
        ],
    )


@pytest.mark.parametrize("zero_initial_offset", [False, True])
def test_paper_e3_circle_state_matches_formula_and_derivative(zero_initial_offset: bool) -> None:
    t_s = 5.0
    radius = 0.03
    omega = 0.1
    phase = omega * t_s
    expected_displacement = np.array([radius * np.cos(phase), radius * np.sin(phase)])
    if zero_initial_offset:
        expected_displacement -= np.array([radius, 0.0])
    state = paper_e3_circle_planar_state(
        t_s,
        radius_m=radius,
        omega_rad_s=omega,
        zero_initial_offset=zero_initial_offset,
    )
    np.testing.assert_allclose(state.displacement_m, expected_displacement)
    np.testing.assert_allclose(
        state.velocity_m_s,
        [
            -radius * omega * np.sin(phase),
            radius * omega * np.cos(phase),
        ],
    )


@pytest.mark.parametrize("zero_initial_offset", [False, True])
def test_paper_e4_cardioid_state_matches_formula_and_derivative(zero_initial_offset: bool) -> None:
    t_s = 5.0
    amplitude = 0.015
    omega = 0.1
    phase = omega * t_s
    expected_displacement = np.array(
        [
            amplitude * (2.0 * np.cos(phase) - np.cos(2.0 * phase)),
            amplitude * (2.0 * np.sin(phase) - np.sin(2.0 * phase)),
        ]
    )
    if zero_initial_offset:
        expected_displacement -= np.array([amplitude, 0.0])
    state = paper_e4_cardioid_planar_state(
        t_s,
        amplitude_m=amplitude,
        omega_rad_s=omega,
        zero_initial_offset=zero_initial_offset,
    )
    np.testing.assert_allclose(state.displacement_m, expected_displacement)
    np.testing.assert_allclose(
        state.velocity_m_s,
        [
            amplitude * (-2.0 * omega * np.sin(phase) + 2.0 * omega * np.sin(2.0 * phase)),
            amplitude * (2.0 * omega * np.cos(phase) - 2.0 * omega * np.cos(2.0 * phase)),
        ],
    )
