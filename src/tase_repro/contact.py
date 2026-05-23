from __future__ import annotations

import numpy as np

from tase_repro.finite_time import sigr


def unit_vector(v: np.ndarray, *, eps: float = 1e-12) -> np.ndarray:
    arr = np.asarray(v, dtype=float)
    norm = float(np.linalg.norm(arr))
    if norm < eps:
        raise ValueError("cannot normalize a near-zero vector")
    return arr / norm


def tangential_projector(normal: np.ndarray) -> np.ndarray:
    n = unit_vector(normal).reshape(3, 1)
    return np.eye(3) - n @ n.T


def normal_force(force: np.ndarray, normal: np.ndarray) -> float:
    return float(unit_vector(normal).dot(np.asarray(force, dtype=float)))


def finite_time_normal_velocity_command(
    measured_normal_force: float,
    desired_normal_force: float,
    *,
    gain: float,
    r: float,
) -> float:
    """Velocity correction template for force error.

    MuJoCo contact-ladder evidence in this repo uses positive z/TCP normal
    velocity as contact relief: if measured force is too high, move away from
    the plane. Hardware force sign must still be verified separately.
    """
    error = float(measured_normal_force) - float(desired_normal_force)
    return float(gain * sigr(error, r))


def sphere_plane_penetration_depth(
    tcp_z_m: float,
    *,
    plane_z_m: float,
    sphere_radius_m: float,
) -> float:
    return max(0.0, float(plane_z_m) + float(sphere_radius_m) - float(tcp_z_m))
