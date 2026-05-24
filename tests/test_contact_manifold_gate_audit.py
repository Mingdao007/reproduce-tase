from __future__ import annotations

from pathlib import Path

import numpy as np

from tase_repro.contact_manifold_gate_audit import run_contact_manifold_gate_audit
from tase_repro.setup_terminal_ik import SetupTerminalThresholds

ROOT = Path(__file__).resolve().parents[1]
TCP_CONTACT_POINT_MODEL_PATH = (
    ROOT / "assets" / "mjcf" / "ur10e_tilted_plane_10deg_tcp_contact_point.xml"
)


def test_contact_manifold_gate_audit_identifies_gate_tradeoffs() -> None:
    result = run_contact_manifold_gate_audit(
        TCP_CONTACT_POINT_MODEL_PATH,
        initial_q=np.array([0.0, -0.1, 0.15, -0.05, 0.0, 0.0]),
        base_z_offset_m=-0.04612594095298278,
        target_force_N=5.0,
        thresholds=SetupTerminalThresholds(),
        surface_normal_world=np.array([0.1736481777, 0.0, 0.9848077530]),
        random_seed=11,
        random_seed_stds_rad=(0.03,),
        random_seed_count_per_std=2,
        max_nfev=200,
    )
    cases = {case.name: case for case in result.cases}

    assert set(cases) == {
        "xy_force",
        "xy_orientation",
        "force_orientation",
        "xy_force_orientation",
    }
    assert result.strict_case.name == "xy_force_orientation"
    assert result.strict_case.pass_count == 0

    xy_force_best = cases["xy_force"].best_optimized_candidate
    assert xy_force_best.force_error_N < 1e-6
    assert xy_force_best.tangential_error_m < 1e-6
    assert xy_force_best.orientation_error_rad > 0.03

    xy_orientation_best = cases["xy_orientation"].best_optimized_candidate
    assert xy_orientation_best.tangential_error_m < 1e-6
    assert xy_orientation_best.orientation_error_rad < 1e-6
    assert "force_error_N" in xy_orientation_best.failed_criteria
    assert "contact_present" in xy_orientation_best.failed_criteria

    strict_best = result.strict_case.best_candidate
    assert "tangential_error_m" in strict_best.failed_criteria
    assert "orientation_error_rad" in strict_best.failed_criteria
    assert result.to_dict()["strict_case_pass_count"] == 0
