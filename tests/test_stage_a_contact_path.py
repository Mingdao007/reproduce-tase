from __future__ import annotations

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from tase_repro.stage_a_contact_path import (
    contact_path_timing,
    parse_joint_vector,
    path_passes_diagnostic_terminal,
    qdot_for_path_duration,
    rotation_slerp_path,
)


def test_rotation_slerp_path_returns_start_midpoint_and_target() -> None:
    start = np.eye(3)
    target = Rotation.from_euler("z", 90.0, degrees=True).as_matrix()

    rotations = rotation_slerp_path(start, target, np.array([0.0, 0.5, 1.0]))

    assert rotations.shape == (3, 3, 3)
    np.testing.assert_allclose(rotations[0], start)
    np.testing.assert_allclose(rotations[-1], target)
    midpoint_angle = Rotation.from_matrix(rotations[1]).as_euler("zyx", degrees=True)[0]
    assert midpoint_angle == pytest.approx(45.0)


def test_parse_joint_vector_validates_expected_size() -> None:
    q = parse_joint_vector("0.0, -0.1, 0.2", expected_size=3)

    np.testing.assert_allclose(q, np.array([0.0, -0.1, 0.2]))

    with pytest.raises(ValueError, match="3 values"):
        parse_joint_vector("0.0, 0.1", expected_size=3)


def test_contact_path_timing_reports_min_duration_and_qdot_utilization() -> None:
    q_path = np.array(
        [
            [0.0, 0.0],
            [0.2, -0.1],
            [0.5, -0.4],
        ]
    )

    timing = contact_path_timing(q_path, qdot_limit_rad_s=0.1)

    assert timing.knot_count == 3
    assert timing.max_abs_segment_delta_rad == pytest.approx(0.3)
    assert timing.min_duration_s == pytest.approx(6.0)
    assert timing.max_abs_qdot_rad_s == pytest.approx(0.1)
    assert timing.tail_max_qdot_utilization == pytest.approx(1.0)


def test_qdot_for_path_duration_rejects_invalid_duration() -> None:
    with pytest.raises(ValueError, match="positive"):
        qdot_for_path_duration(np.array([[0.0], [1.0]]), 0.0)


def test_path_passes_diagnostic_terminal_reports_failed_criteria() -> None:
    result = path_passes_diagnostic_terminal(
        terminal_force_error_N=0.1,
        terminal_xy_error_m=0.006,
        terminal_force_normal_orientation_error_rad=0.04,
        target_contact_count=0,
        force_threshold_N=0.25,
        xy_threshold_m=0.004,
        orientation_threshold_rad=0.08,
        min_target_contact_count=1,
    )

    assert result["passed"] is False
    assert result["failed_criteria"] == ["terminal_xy_error_m", "target_contact_count"]
    assert result["criteria"]["terminal_force_error_N"]["passed"] is True
