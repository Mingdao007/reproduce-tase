from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.spatial.transform import Rotation, Slerp


@dataclass(frozen=True)
class ContactPathTiming:
    knot_count: int
    qdot_limit_rad_s: float
    min_duration_s: float
    segment_duration_s: float
    max_abs_segment_delta_rad: float
    max_abs_qdot_rad_s: float
    qdot_saturation_fraction: float
    tail_max_qdot_utilization: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "knot_count": int(self.knot_count),
            "qdot_limit_rad_s": float(self.qdot_limit_rad_s),
            "min_duration_s": float(self.min_duration_s),
            "segment_duration_s": float(self.segment_duration_s),
            "max_abs_segment_delta_rad": float(self.max_abs_segment_delta_rad),
            "max_abs_qdot_rad_s": float(self.max_abs_qdot_rad_s),
            "qdot_saturation_fraction": float(self.qdot_saturation_fraction),
            "tail_max_qdot_utilization": float(self.tail_max_qdot_utilization),
        }


def parse_joint_vector(text: str, *, expected_size: int | None = None) -> np.ndarray:
    values = np.asarray([float(part.strip()) for part in text.split(",") if part.strip()], dtype=float)
    if values.ndim != 1 or len(values) == 0:
        raise ValueError("joint vector must contain at least one value")
    if expected_size is not None and len(values) != int(expected_size):
        raise ValueError(f"joint vector must contain {int(expected_size)} values")
    return values


def rotation_slerp_path(start_rotation: np.ndarray, target_rotation: np.ndarray, alphas: np.ndarray) -> np.ndarray:
    start = np.asarray(start_rotation, dtype=float)
    target = np.asarray(target_rotation, dtype=float)
    values = np.asarray(alphas, dtype=float)
    if start.shape != (3, 3) or target.shape != (3, 3):
        raise ValueError("start_rotation and target_rotation must have shape (3, 3)")
    if values.ndim != 1:
        raise ValueError("alphas must be one-dimensional")
    slerp = Slerp([0.0, 1.0], Rotation.from_matrix([start, target]))
    return slerp(values).as_matrix()


def qdot_for_path_duration(q_path: np.ndarray, duration_s: float) -> np.ndarray:
    path = np.asarray(q_path, dtype=float)
    if path.ndim != 2:
        raise ValueError("q_path must be two-dimensional")
    if len(path) < 2:
        raise ValueError("q_path must contain at least two knots")
    duration = float(duration_s)
    if duration <= 0.0:
        raise ValueError("duration_s must be positive")
    segment_duration = duration / float(len(path) - 1)
    return np.diff(path, axis=0) / segment_duration


def contact_path_timing(q_path: np.ndarray, *, qdot_limit_rad_s: float, duration_s: float | None = None) -> ContactPathTiming:
    path = np.asarray(q_path, dtype=float)
    if path.ndim != 2 or len(path) < 2:
        raise ValueError("q_path must be a two-dimensional array with at least two knots")
    qdot_limit = abs(float(qdot_limit_rad_s))
    if qdot_limit <= 0.0:
        raise ValueError("qdot_limit_rad_s must be positive")
    segment_delta = np.diff(path, axis=0)
    max_abs_segment_delta = float(np.max(np.abs(segment_delta)))
    min_duration = 0.0 if max_abs_segment_delta == 0.0 else (len(path) - 1) * max_abs_segment_delta / qdot_limit
    duration = min_duration if duration_s is None else float(duration_s)
    if duration <= 0.0:
        raise ValueError("duration_s must be positive when provided")
    qdot = qdot_for_path_duration(path, duration)
    utilization = np.max(np.abs(qdot) / qdot_limit, axis=1)
    tail = max(1, int(round(len(utilization) * 0.2)))
    return ContactPathTiming(
        knot_count=len(path),
        qdot_limit_rad_s=qdot_limit,
        min_duration_s=min_duration,
        segment_duration_s=duration / float(len(path) - 1),
        max_abs_segment_delta_rad=max_abs_segment_delta,
        max_abs_qdot_rad_s=float(np.max(np.abs(qdot))),
        qdot_saturation_fraction=float(np.mean(utilization >= 0.98)),
        tail_max_qdot_utilization=float(np.max(utilization[-tail:])),
    )


def path_passes_diagnostic_terminal(
    *,
    terminal_force_error_N: float,
    terminal_xy_error_m: float,
    terminal_force_normal_orientation_error_rad: float,
    target_contact_count: int,
    force_threshold_N: float,
    xy_threshold_m: float,
    orientation_threshold_rad: float,
    min_target_contact_count: int,
) -> dict[str, Any]:
    criteria = {
        "terminal_force_error_N": {
            "actual": float(terminal_force_error_N),
            "operator": "<=",
            "threshold": float(force_threshold_N),
            "passed": float(terminal_force_error_N) <= float(force_threshold_N),
        },
        "terminal_xy_error_m": {
            "actual": float(terminal_xy_error_m),
            "operator": "<=",
            "threshold": float(xy_threshold_m),
            "passed": float(terminal_xy_error_m) <= float(xy_threshold_m),
        },
        "terminal_force_normal_orientation_error_rad": {
            "actual": float(terminal_force_normal_orientation_error_rad),
            "operator": "<=",
            "threshold": float(orientation_threshold_rad),
            "passed": float(terminal_force_normal_orientation_error_rad) <= float(orientation_threshold_rad),
        },
        "target_contact_count": {
            "actual": int(target_contact_count),
            "operator": ">=",
            "threshold": int(min_target_contact_count),
            "passed": int(target_contact_count) >= int(min_target_contact_count),
        },
    }
    failed = [name for name, criterion in criteria.items() if not criterion["passed"]]
    return {
        "passed": not failed,
        "failed_criteria": failed,
        "criteria": criteria,
    }
