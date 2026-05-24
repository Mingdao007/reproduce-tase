from __future__ import annotations

import numpy as np

from tase_repro.panda_kinematics import (
    finite_difference_panda_position_jacobian,
    panda_forward_kinematics,
    panda_geometric_jacobian,
)


def test_panda_forward_kinematics_returns_valid_pose() -> None:
    q = np.array([0.0, -np.pi / 4.0, 0.0, -3.0 * np.pi / 4.0, 0.0, np.pi / 2.0, np.pi / 4.0])
    pose = panda_forward_kinematics(q)
    assert pose.position_m.shape == (3,)
    assert pose.rotation.shape == (3, 3)
    assert pose.quaternion_xyzw.shape == (4,)
    np.testing.assert_allclose(pose.rotation.T @ pose.rotation, np.eye(3), atol=1e-12)
    np.testing.assert_allclose(np.linalg.det(pose.rotation), 1.0, atol=1e-12)
    np.testing.assert_allclose(np.linalg.norm(pose.quaternion_xyzw), 1.0, atol=1e-12)


def test_panda_geometric_jacobian_matches_position_finite_difference() -> None:
    q = np.array([0.18, -0.51, -0.15, -2.31, -0.07, 1.80, 0.07])
    analytic = panda_geometric_jacobian(q)
    numeric = finite_difference_panda_position_jacobian(q)
    assert analytic.shape == (6, 7)
    np.testing.assert_allclose(analytic[:3, :], numeric, atol=1e-6)
    assert np.linalg.matrix_rank(analytic) >= 5
