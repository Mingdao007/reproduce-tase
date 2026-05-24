from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class JointPathTrackingResult:
    time_s: np.ndarray
    alpha: np.ndarray
    desired_q: np.ndarray
    q: np.ndarray
    qdot_command: np.ndarray
    qdot_limit_rad_s: float

    def summary(self) -> dict[str, Any]:
        qdot_abs = np.abs(self.qdot_command)
        qdot_utilization = np.max(qdot_abs / self.qdot_limit_rad_s, axis=1)
        tracking_error = self.q - self.desired_q
        tracking_error_abs = np.abs(tracking_error)
        tail = max(1, int(round(len(qdot_utilization) * 0.2)))
        return {
            "duration_s": float(self.time_s[-1] - self.time_s[0]),
            "sample_count": int(len(self.time_s)),
            "dt_min_s": float(np.min(np.diff(self.time_s))),
            "dt_max_s": float(np.max(np.diff(self.time_s))),
            "qdot_limit_rad_s": float(self.qdot_limit_rad_s),
            "max_abs_qdot_rad_s": float(np.max(qdot_abs)),
            "max_qdot_utilization": float(np.max(qdot_utilization)),
            "qdot_saturation_fraction": float(np.mean(qdot_utilization >= 0.98)),
            "tail_max_qdot_utilization": float(np.max(qdot_utilization[-tail:])),
            "max_abs_tracking_error_rad": float(np.max(tracking_error_abs)),
            "max_tracking_error_norm_rad": float(np.max(np.linalg.norm(tracking_error, axis=1))),
            "final_tracking_error_norm_rad": float(np.linalg.norm(tracking_error[-1])),
        }


def interpolate_joint_path(q_path: np.ndarray, alphas: np.ndarray) -> np.ndarray:
    path = np.asarray(q_path, dtype=float)
    values = np.asarray(alphas, dtype=float)
    if path.ndim != 2 or len(path) < 2:
        raise ValueError("q_path must be a two-dimensional array with at least two knots")
    if values.ndim != 1:
        raise ValueError("alphas must be one-dimensional")
    clipped = np.clip(values, 0.0, 1.0)
    position = clipped * float(len(path) - 1)
    lower = np.floor(position).astype(int)
    upper = np.minimum(lower + 1, len(path) - 1)
    weight = (position - lower)[:, None]
    return (1.0 - weight) * path[lower] + weight * path[upper]


def replay_qdot_limited_joint_path(
    q_path: np.ndarray,
    *,
    duration_s: float,
    dt_s: float,
    qdot_limit_rad_s: float,
) -> JointPathTrackingResult:
    path = np.asarray(q_path, dtype=float)
    duration = float(duration_s)
    dt = float(dt_s)
    qdot_limit = abs(float(qdot_limit_rad_s))
    if path.ndim != 2 or len(path) < 2:
        raise ValueError("q_path must be a two-dimensional array with at least two knots")
    if duration <= 0.0:
        raise ValueError("duration_s must be positive")
    if dt <= 0.0:
        raise ValueError("dt_s must be positive")
    if qdot_limit <= 0.0:
        raise ValueError("qdot_limit_rad_s must be positive")

    step_count = int(np.ceil(duration / dt))
    time_s = np.linspace(0.0, duration, step_count + 1)
    alpha = time_s / duration
    desired_q = interpolate_joint_path(path, alpha)
    q = np.empty_like(desired_q)
    qdot_command = np.empty((step_count, path.shape[1]), dtype=float)
    q[0] = desired_q[0]
    for idx in range(step_count):
        step_s = time_s[idx + 1] - time_s[idx]
        raw_command = (desired_q[idx + 1] - q[idx]) / step_s
        command = np.clip(raw_command, -qdot_limit, qdot_limit)
        qdot_command[idx] = command
        q[idx + 1] = q[idx] + command * step_s
    return JointPathTrackingResult(
        time_s=time_s,
        alpha=alpha,
        desired_q=desired_q,
        q=q,
        qdot_command=qdot_command,
        qdot_limit_rad_s=qdot_limit,
    )
