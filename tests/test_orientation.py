from __future__ import annotations

import numpy as np
import pytest

from tase_repro.orientation import rotation_aligning_local_z_to_normal


def test_rotation_aligning_local_z_to_normal_preserves_identity_for_world_z() -> None:
    rotation = rotation_aligning_local_z_to_normal(
        np.array([0.0, 0.0, 2.0]),
        reference_rotation=np.eye(3),
    )
    np.testing.assert_allclose(rotation, np.eye(3), atol=1e-12)


def test_rotation_aligning_local_z_to_normal_matches_requested_normal() -> None:
    normal = np.array([1.0, 2.0, 3.0])
    rotation = rotation_aligning_local_z_to_normal(normal, reference_rotation=np.eye(3))
    expected_z = normal / np.linalg.norm(normal)
    np.testing.assert_allclose(rotation[:, 2], expected_z, atol=1e-12)
    np.testing.assert_allclose(rotation.T @ rotation, np.eye(3), atol=1e-12)
    assert np.linalg.det(rotation) == pytest.approx(1.0)


def test_rotation_aligning_local_z_to_normal_handles_parallel_reference_axis() -> None:
    reference = np.eye(3)
    rotation = rotation_aligning_local_z_to_normal(
        np.array([1.0, 0.0, 0.0]),
        reference_rotation=reference,
    )
    np.testing.assert_allclose(rotation[:, 2], np.array([1.0, 0.0, 0.0]), atol=1e-12)
    np.testing.assert_allclose(rotation.T @ rotation, np.eye(3), atol=1e-12)
