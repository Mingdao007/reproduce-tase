from __future__ import annotations

from pathlib import Path

import numpy as np

from tase_repro.force_feedback import apply_base_z_offset
from tase_repro.kinematics import load_model, make_data, set_qpos
from tase_repro.setup_terminal_ik import (
    SetupTerminalThresholds,
    evaluate_setup_terminal_candidate,
    solve_setup_terminal_ik,
)
from tase_repro.orientation import rotation_aligning_local_z_to_normal

ROOT = Path(__file__).resolve().parents[1]
TILTED_MODEL_PATH = ROOT / "assets" / "mjcf" / "ur10e_tilted_plane_10deg.xml"


def test_initial_tilted_setup_candidate_fails_only_orientation_gate() -> None:
    model = load_model(TILTED_MODEL_PATH)
    apply_base_z_offset(model, -0.0011631221220595766)
    data = make_data(model)
    q = np.array([0.0, -0.1, 0.15, -0.05, 0.0, 0.0])
    set_qpos(model, data, q)
    surface_normal = np.array([0.1736481777, 0.0, 0.9848077530])
    desired_rotation = rotation_aligning_local_z_to_normal(surface_normal)
    candidate = evaluate_setup_terminal_candidate(
        model,
        data,
        q=q,
        seed_label="initial",
        cost=0.0,
        success=True,
        status=0,
        message="test",
        nfev=0,
        site_name="tcp_site_unverified_85mm",
        reference_xy_m=np.array([0.00497793, 0.0]),
        desired_rotation=desired_rotation,
        target_force_N=5.0,
        thresholds=SetupTerminalThresholds(),
    )

    assert candidate.force_error_N < 1e-6
    assert candidate.tangential_error_m < 1e-6
    assert candidate.orientation_error_rad > 0.03
    assert candidate.failed_criteria == ["orientation_error_rad"]


def test_setup_terminal_ik_returns_ranked_candidates() -> None:
    result = solve_setup_terminal_ik(
        TILTED_MODEL_PATH,
        initial_q=np.array([0.0, -0.1, 0.15, -0.05, 0.0, 0.0]),
        base_z_offset_m=-0.0011631221220595766,
        target_force_N=5.0,
        thresholds=SetupTerminalThresholds(),
        surface_normal_world=np.array([0.1736481777, 0.0, 0.9848077530]),
        random_seed_count=1,
        random_seed_std_rad=0.01,
        max_nfev=20,
    )

    assert len(result.candidates) == 2
    assert result.best_candidate.max_gate_ratio <= result.candidates[-1].max_gate_ratio
    assert result.initial_candidate.force_error_N < 1e-6
    assert result.to_dict()["candidate_count"] == 2
