from __future__ import annotations

import numpy as np

from tase_repro.contact import (
    finite_time_normal_velocity_command,
    normal_force,
    sphere_plane_penetration_depth,
    tangential_projector,
)


def test_tangential_projector_removes_normal_component() -> None:
    n = np.array([0.0, 0.0, 2.0])
    projector = tangential_projector(n)
    vec = np.array([1.0, -2.0, 3.0])
    projected = projector @ vec
    np.testing.assert_allclose(projected.dot(np.array([0.0, 0.0, 1.0])), 0.0, atol=1e-12)
    np.testing.assert_allclose(projector @ projector, projector, atol=1e-12)


def test_normal_force_uses_unit_normal() -> None:
    assert normal_force(np.array([1.0, 2.0, 3.0]), np.array([0.0, 0.0, 2.0])) == 3.0


def test_finite_time_force_command_sign_contract() -> None:
    assert finite_time_normal_velocity_command(6.0, 5.0, gain=2.0, r=0.5) > 0.0
    assert finite_time_normal_velocity_command(4.0, 5.0, gain=2.0, r=0.5) < 0.0


def test_sphere_plane_penetration_depth() -> None:
    assert sphere_plane_penetration_depth(0.044, plane_z_m=0.0, sphere_radius_m=0.045) > 0.0
    assert sphere_plane_penetration_depth(0.050, plane_z_m=0.0, sphere_radius_m=0.045) == 0.0
