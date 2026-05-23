from __future__ import annotations

import numpy as np

from tase_repro.trajectories import linear_planar_state, paper_e1_cycloid_planar_state


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
