from __future__ import annotations

from pathlib import Path

import numpy as np

from tase_repro.kinematics import (
    finite_difference_site_position_jacobian,
    joint_names,
    joint_ranges,
    load_model,
    make_data,
    set_qpos,
    site_jacobian,
)

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "assets" / "mjcf" / "ur10e_nominal.xml"
SITE = "tcp_site_unverified_85mm"


def test_ur10e_v1_model_joint_contract() -> None:
    model = load_model(MODEL_PATH)
    assert model.nq == 6
    assert model.nv == 6
    assert joint_names(model) == [
        "shoulder_pan_joint",
        "shoulder_lift_joint",
        "elbow_joint",
        "wrist_1_joint",
        "wrist_2_joint",
        "wrist_3_joint",
    ]
    q_min, q_max = joint_ranges(model)
    assert q_min.shape == (6,)
    assert q_max.shape == (6,)
    assert np.all(q_min < q_max)


def test_site_position_jacobian_matches_finite_difference() -> None:
    model = load_model(MODEL_PATH)
    data = make_data(model)
    q = np.array([0.1, -0.2, 0.15, -0.1, 0.05, -0.08])
    set_qpos(model, data, q)
    jacp, _ = site_jacobian(model, data, SITE)
    fd = finite_difference_site_position_jacobian(model, data, SITE, q, eps=1e-6)
    np.testing.assert_allclose(jacp, fd, atol=2e-6)

