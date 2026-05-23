from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PlanarTrajectoryState:
    displacement_m: np.ndarray
    velocity_m_s: np.ndarray


def linear_planar_state(t_s: float, velocity_m_s: np.ndarray) -> PlanarTrajectoryState:
    velocity = np.asarray(velocity_m_s, dtype=float)
    if velocity.shape != (2,):
        raise ValueError("velocity_m_s must have shape (2,) for x/y")
    return PlanarTrajectoryState(
        displacement_m=velocity * float(t_s),
        velocity_m_s=velocity,
    )


def paper_e1_cycloid_planar_state(
    t_s: float,
    *,
    amplitude_m: float = 0.015,
    omega_rad_s: float = 0.1,
    time_scale: float = 1.0,
) -> PlanarTrajectoryState:
    """Paper Section VI Experiment 1 cycloid trajectory in the x/y plane."""
    phase = float(omega_rad_s) * float(time_scale) * float(t_s)
    amplitude = float(amplitude_m)
    phase_rate = float(omega_rad_s) * float(time_scale)
    return PlanarTrajectoryState(
        displacement_m=np.array(
            [
                amplitude * (phase - np.sin(phase)),
                amplitude * (1.0 - np.cos(phase)),
            ],
            dtype=float,
        ),
        velocity_m_s=np.array(
            [
                amplitude * phase_rate * (1.0 - np.cos(phase)),
                amplitude * phase_rate * np.sin(phase),
            ],
            dtype=float,
        ),
    )


def paper_e2_figure_eight_planar_state(
    t_s: float,
    *,
    amplitude_x_m: float = 0.04,
    amplitude_y_m: float = 0.01,
    omega_rad_s: float = 0.1,
    time_scale: float = 1.0,
) -> PlanarTrajectoryState:
    """Paper Section VI Experiment 2 figure-eight trajectory in x/y."""
    phase = float(omega_rad_s) * float(time_scale) * float(t_s)
    phase_rate = float(omega_rad_s) * float(time_scale)
    return PlanarTrajectoryState(
        displacement_m=np.array(
            [
                float(amplitude_x_m) * np.sin(phase),
                float(amplitude_y_m) * np.sin(2.0 * phase),
            ],
            dtype=float,
        ),
        velocity_m_s=np.array(
            [
                float(amplitude_x_m) * phase_rate * np.cos(phase),
                float(amplitude_y_m) * 2.0 * phase_rate * np.cos(2.0 * phase),
            ],
            dtype=float,
        ),
    )


def paper_e3_circle_planar_state(
    t_s: float,
    *,
    radius_m: float = 0.03,
    omega_rad_s: float = 0.1,
    time_scale: float = 1.0,
    zero_initial_offset: bool = True,
) -> PlanarTrajectoryState:
    """Paper Section VI Experiment 3 circle trajectory in x/y."""
    phase = float(omega_rad_s) * float(time_scale) * float(t_s)
    phase_rate = float(omega_rad_s) * float(time_scale)
    radius = float(radius_m)
    displacement = np.array([radius * np.cos(phase), radius * np.sin(phase)], dtype=float)
    if zero_initial_offset:
        displacement = displacement - np.array([radius, 0.0], dtype=float)
    return PlanarTrajectoryState(
        displacement_m=displacement,
        velocity_m_s=np.array(
            [
                -radius * phase_rate * np.sin(phase),
                radius * phase_rate * np.cos(phase),
            ],
            dtype=float,
        ),
    )


def paper_e4_cardioid_planar_state(
    t_s: float,
    *,
    amplitude_m: float = 0.015,
    omega_rad_s: float = 0.1,
    time_scale: float = 1.0,
    zero_initial_offset: bool = True,
) -> PlanarTrajectoryState:
    """Paper Section VI Experiment 4 cardioid trajectory in x/y."""
    phase = float(omega_rad_s) * float(time_scale) * float(t_s)
    phase_rate = float(omega_rad_s) * float(time_scale)
    amplitude = float(amplitude_m)
    displacement = np.array(
        [
            amplitude * (2.0 * np.cos(phase) - np.cos(2.0 * phase)),
            amplitude * (2.0 * np.sin(phase) - np.sin(2.0 * phase)),
        ],
        dtype=float,
    )
    if zero_initial_offset:
        displacement = displacement - np.array([amplitude, 0.0], dtype=float)
    return PlanarTrajectoryState(
        displacement_m=displacement,
        velocity_m_s=np.array(
            [
                amplitude * (-2.0 * phase_rate * np.sin(phase) + 2.0 * phase_rate * np.sin(2.0 * phase)),
                amplitude * (2.0 * phase_rate * np.cos(phase) - 2.0 * phase_rate * np.cos(2.0 * phase)),
            ],
            dtype=float,
        ),
    )
