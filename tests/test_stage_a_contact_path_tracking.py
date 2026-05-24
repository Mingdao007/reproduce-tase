from __future__ import annotations

import numpy as np
import pytest

from tase_repro.stage_a_contact_path_tracking import (
    interpolate_joint_path,
    replay_qdot_limited_joint_path,
)


def test_interpolate_joint_path_interpolates_uniform_segments() -> None:
    q_path = np.array([[0.0, 0.0], [2.0, 4.0], [4.0, 0.0]])

    q = interpolate_joint_path(q_path, np.array([0.0, 0.25, 0.5, 0.75, 1.0]))

    np.testing.assert_allclose(
        q,
        np.array(
            [
                [0.0, 0.0],
                [1.0, 2.0],
                [2.0, 4.0],
                [3.0, 2.0],
                [4.0, 0.0],
            ]
        ),
    )


def test_replay_qdot_limited_joint_path_tracks_when_duration_allows_limit() -> None:
    q_path = np.array([[0.0], [0.2], [0.4]])

    result = replay_qdot_limited_joint_path(q_path, duration_s=4.0, dt_s=1.0, qdot_limit_rad_s=0.1)

    np.testing.assert_allclose(result.q, result.desired_q)
    summary = result.summary()
    assert summary["max_abs_qdot_rad_s"] == pytest.approx(0.1)
    assert summary["final_tracking_error_norm_rad"] == pytest.approx(0.0)


def test_replay_qdot_limited_joint_path_reports_tracking_error_when_clipped() -> None:
    q_path = np.array([[0.0], [1.0]])

    result = replay_qdot_limited_joint_path(q_path, duration_s=1.0, dt_s=0.5, qdot_limit_rad_s=0.2)

    summary = result.summary()
    assert summary["max_abs_qdot_rad_s"] == pytest.approx(0.2)
    assert summary["final_tracking_error_norm_rad"] == pytest.approx(0.8)


def test_replay_qdot_limited_joint_path_rejects_invalid_dt() -> None:
    with pytest.raises(ValueError, match="dt_s"):
        replay_qdot_limited_joint_path(np.array([[0.0], [1.0]]), duration_s=1.0, dt_s=0.0, qdot_limit_rad_s=1.0)
