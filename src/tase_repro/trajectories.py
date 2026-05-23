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
