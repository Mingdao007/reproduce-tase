from __future__ import annotations

import numpy as np

from tase_repro.contact import unit_vector


def _orthogonal_seed(axis: np.ndarray) -> np.ndarray:
    """Return a stable world-axis seed that is not parallel to `axis`."""
    candidates = (
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([0.0, 0.0, 1.0]),
    )
    return min(candidates, key=lambda candidate: abs(float(candidate.dot(axis))))


def rotation_aligning_local_z_to_normal(
    normal: np.ndarray,
    *,
    reference_rotation: np.ndarray | None = None,
    eps: float = 1e-9,
) -> np.ndarray:
    """Build a desired TCP rotation from a 3D force/contact normal.

    The paper defines the orientation input as a force-normal vector
    `u = F / ||F||`, but it does not fully specify yaw about that normal. This
    repo convention aligns the TCP local z-axis to `normal` and preserves the
    reference local x-axis projected into the tangent plane whenever possible.
    """
    z_axis = unit_vector(np.asarray(normal, dtype=float), eps=eps)
    if reference_rotation is None:
        x_seed = _orthogonal_seed(z_axis)
    else:
        reference = np.asarray(reference_rotation, dtype=float)
        if reference.shape != (3, 3):
            raise ValueError("reference_rotation must have shape (3, 3)")
        x_seed = reference[:, 0]

    x_axis = np.asarray(x_seed, dtype=float) - z_axis * float(np.asarray(x_seed, dtype=float).dot(z_axis))
    if np.linalg.norm(x_axis) < eps:
        x_seed = _orthogonal_seed(z_axis)
        x_axis = x_seed - z_axis * float(x_seed.dot(z_axis))
    x_axis = unit_vector(x_axis, eps=eps)
    y_axis = unit_vector(np.cross(z_axis, x_axis), eps=eps)
    x_axis = unit_vector(np.cross(y_axis, z_axis), eps=eps)
    rotation = np.column_stack([x_axis, y_axis, z_axis])
    if np.linalg.det(rotation) < 0.0:
        y_axis = -y_axis
        rotation = np.column_stack([x_axis, y_axis, z_axis])
    return rotation
