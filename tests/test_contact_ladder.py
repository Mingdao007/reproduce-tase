from __future__ import annotations

from pathlib import Path

import numpy as np

from tase_repro.contact_ladder import (
    calibrate_base_z_for_initial_q_target_force,
    calibrate_base_z_for_target_force,
    measure_static_contact_force,
)

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "assets" / "mjcf" / "ur10e_nominal.xml"


def test_static_contact_force_decreases_when_base_is_lifted() -> None:
    baseline = measure_static_contact_force(MODEL_PATH, base_z_offset_m=0.0, steps=120, tail_steps=40)
    lifted = measure_static_contact_force(MODEL_PATH, base_z_offset_m=0.002, steps=120, tail_steps=40)
    assert baseline.mean_normal_force_N > 1.0
    assert lifted.mean_normal_force_N == 0.0


def test_calibrate_base_z_for_one_newton_contact() -> None:
    meas = calibrate_base_z_for_target_force(
        MODEL_PATH,
        target_force_N=1.0,
        lower_offset_m=0.0,
        upper_offset_m=0.002,
        steps=120,
        tail_steps=40,
        tolerance_N=0.02,
    )
    assert abs(meas.mean_normal_force_N - 1.0) <= 0.02
    assert meas.mean_contact_count > 0.0


def test_calibrate_base_z_for_initial_posture_contact() -> None:
    meas = calibrate_base_z_for_initial_q_target_force(
        MODEL_PATH,
        initial_q=np.array([0.0, -0.02, 0.03, -0.01, 0.0, 0.0]),
        target_force_N=5.0,
        lower_offset_m=-0.002,
        upper_offset_m=0.002,
        tolerance_N=0.02,
    )
    assert abs(meas.normal_force_N - 5.0) <= 0.02
    assert meas.contact_count > 0
