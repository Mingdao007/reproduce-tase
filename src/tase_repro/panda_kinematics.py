from __future__ import annotations

from dataclasses import dataclass

import numpy as np


PANDA_D_M = np.array([0.333, 0.0, 0.316, 0.0, 0.384, 0.0, 0.2104], dtype=float)
PANDA_A_M = np.array([0.0, 0.0, 0.0825, -0.0825, 0.0, 0.088, 0.0], dtype=float)
PANDA_ALPHA_RAD = np.array(
    [-np.pi / 2.0, np.pi / 2.0, np.pi / 2.0, -np.pi / 2.0, np.pi / 2.0, np.pi / 2.0, 0.0],
    dtype=float,
)


@dataclass(frozen=True)
class PandaPose:
    position_m: np.ndarray
    rotation: np.ndarray
    quaternion_xyzw: np.ndarray


def _as_joint_vector(q: np.ndarray) -> np.ndarray:
    q_array = np.asarray(q, dtype=float)
    if q_array.shape != (7,):
        raise ValueError("Panda joint vector must have shape (7,)")
    return q_array


def dh_transform(theta_rad: float, d_m: float, a_m: float, alpha_rad: float) -> np.ndarray:
    ctheta = float(np.cos(theta_rad))
    stheta = float(np.sin(theta_rad))
    calpha = float(np.cos(alpha_rad))
    salpha = float(np.sin(alpha_rad))
    return np.array(
        [
            [ctheta, -stheta * calpha, stheta * salpha, a_m * ctheta],
            [stheta, ctheta * calpha, -ctheta * salpha, a_m * stheta],
            [0.0, salpha, calpha, d_m],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def panda_link_transforms(q: np.ndarray) -> list[np.ndarray]:
    q_array = _as_joint_vector(q)
    transforms = [np.eye(4, dtype=float)]
    transform = np.eye(4, dtype=float)
    for idx in range(7):
        transform = transform @ dh_transform(
            q_array[idx],
            PANDA_D_M[idx],
            PANDA_A_M[idx],
            PANDA_ALPHA_RAD[idx],
        )
        transforms.append(transform.copy())
    return transforms


def quaternion_xyzw_from_rotation(rotation: np.ndarray) -> np.ndarray:
    rot = np.asarray(rotation, dtype=float)
    if rot.shape != (3, 3):
        raise ValueError("rotation must have shape (3, 3)")
    trace = float(np.trace(rot))
    if trace > 0.0:
        scale = np.sqrt(trace + 1.0) * 2.0
        qw = 0.25 * scale
        qx = (rot[2, 1] - rot[1, 2]) / scale
        qy = (rot[0, 2] - rot[2, 0]) / scale
        qz = (rot[1, 0] - rot[0, 1]) / scale
    else:
        diag = np.diag(rot)
        idx = int(np.argmax(diag))
        if idx == 0:
            scale = np.sqrt(1.0 + rot[0, 0] - rot[1, 1] - rot[2, 2]) * 2.0
            qw = (rot[2, 1] - rot[1, 2]) / scale
            qx = 0.25 * scale
            qy = (rot[0, 1] + rot[1, 0]) / scale
            qz = (rot[0, 2] + rot[2, 0]) / scale
        elif idx == 1:
            scale = np.sqrt(1.0 + rot[1, 1] - rot[0, 0] - rot[2, 2]) * 2.0
            qw = (rot[0, 2] - rot[2, 0]) / scale
            qx = (rot[0, 1] + rot[1, 0]) / scale
            qy = 0.25 * scale
            qz = (rot[1, 2] + rot[2, 1]) / scale
        else:
            scale = np.sqrt(1.0 + rot[2, 2] - rot[0, 0] - rot[1, 1]) * 2.0
            qw = (rot[1, 0] - rot[0, 1]) / scale
            qx = (rot[0, 2] + rot[2, 0]) / scale
            qy = (rot[1, 2] + rot[2, 1]) / scale
            qz = 0.25 * scale
    quat = np.array([qx, qy, qz, qw], dtype=float)
    return quat / np.linalg.norm(quat)


def panda_forward_kinematics(q: np.ndarray) -> PandaPose:
    transform = panda_link_transforms(q)[-1]
    rotation = transform[:3, :3].copy()
    return PandaPose(
        position_m=transform[:3, 3].copy(),
        rotation=rotation,
        quaternion_xyzw=quaternion_xyzw_from_rotation(rotation),
    )


def panda_geometric_jacobian(q: np.ndarray) -> np.ndarray:
    transforms = panda_link_transforms(q)
    end_position = transforms[-1][:3, 3]
    jacobian = np.zeros((6, 7), dtype=float)
    for idx in range(7):
        z_axis = transforms[idx][:3, 2]
        origin = transforms[idx][:3, 3]
        jacobian[:3, idx] = np.cross(z_axis, end_position - origin)
        jacobian[3:, idx] = z_axis
    return jacobian


def finite_difference_panda_position_jacobian(q: np.ndarray, *, eps: float = 1e-6) -> np.ndarray:
    q_array = _as_joint_vector(q)
    jacobian = np.zeros((3, 7), dtype=float)
    for idx in range(7):
        q_plus = q_array.copy()
        q_minus = q_array.copy()
        q_plus[idx] += eps
        q_minus[idx] -= eps
        p_plus = panda_forward_kinematics(q_plus).position_m
        p_minus = panda_forward_kinematics(q_minus).position_m
        jacobian[:, idx] = (p_plus - p_minus) / (2.0 * eps)
    return jacobian
