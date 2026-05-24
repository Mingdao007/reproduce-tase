from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import yaml

from tase_repro.paper_7dof import (
    PaperSectionV7DofResult,
    PaperSectionV7DofConfig,
    escape_velocity_bounds,
    paper_section_v_desired_position,
    plane_contact,
    simulate_paper_section_v_7dof,
    summarize_paper_section_v_7dof,
)


ROOT = Path(__file__).resolve().parents[1]


def test_paper_section_v_trajectory_uses_explicit_z0() -> None:
    state = paper_section_v_desired_position(0.0, z0_m=0.42)
    np.testing.assert_allclose(state, [0.2, 0.0, 0.42])


def test_plane_contact_equilibrium_force() -> None:
    penetration = 5.0 / 4.0e4
    result = plane_contact(
        np.array([0.0, 0.0, -penetration]),
        np.zeros(3),
        plane_z_m=0.0,
        plane_normal=np.array([0.0, 0.0, 1.0]),
        stiffness_N_m=4.0e4,
        damping_N_s_m=220.0,
        max_force_N=50.0,
    )
    assert result[2]
    np.testing.assert_allclose(result[1], 5.0)


def test_escape_velocity_bounds_combine_paper_limits_and_position_margin() -> None:
    lower, upper = escape_velocity_bounds(
        np.array([2.45, 0.0]),
        q_min_rad=np.array([-2.5, -2.5]),
        q_max_rad=np.array([2.5, 2.5]),
        qdot_min_rad_s=np.array([-1.5, -1.5]),
        qdot_max_rad_s=np.array([1.5, 1.5]),
        alpha=2.0,
    )
    np.testing.assert_allclose(lower, [-1.5, -1.5])
    np.testing.assert_allclose(upper, [0.1, 1.5])


def test_short_paper_7dof_diagnostic_executes_with_hard_bounds() -> None:
    config = PaperSectionV7DofConfig(duration_s=0.02, dt_s=0.002, solver_mode="pinv_bounded")
    result = simulate_paper_section_v_7dof(config)
    metrics = summarize_paper_section_v_7dof(result)
    assert result.q_rad.shape[1] == 7
    assert result.commanded_task_velocity.shape[1] == 6
    assert metrics["execution_success"]
    assert metrics["q_bound_violation_count"] == 0
    assert metrics["qdot_bound_violation_count"] == 0
    assert metrics["contact_fraction"] > 0.0


def test_contact_stabilized_pinv_diagnostic_passes_tail_force_gate() -> None:
    config = PaperSectionV7DofConfig(
        duration_s=3.0,
        dt_s=0.004,
        solver_mode="pinv_bounded",
        communication_delay_s=0.032,
        force_integral_limit=0.1,
    )
    result = simulate_paper_section_v_7dof(config)
    metrics = summarize_paper_section_v_7dof(result)
    assert metrics["execution_success"]
    assert metrics["contact_force_tail_success"]
    assert metrics["tail_contact_fraction"] == 1.0
    assert metrics["tail_force_error_mean_N"] <= 1.0
    assert metrics["q_bound_violation_count"] == 0
    assert metrics["qdot_bound_violation_count"] == 0


def test_capped_integral_kkt_diagnostic_passes_tail_force_gate() -> None:
    config = PaperSectionV7DofConfig(
        duration_s=5.0,
        dt_s=0.002,
        solver_mode="kkt_projection",
        force_integral_limit=0.1,
    )
    result = simulate_paper_section_v_7dof(config)
    metrics = summarize_paper_section_v_7dof(result)
    assert metrics["execution_success"]
    assert metrics["contact_force_tail_success"]
    assert metrics["tail_contact_fraction"] == 1.0
    assert metrics["tail_force_error_mean_N"] <= 1.0
    assert metrics["q_bound_violation_count"] == 0
    assert metrics["qdot_bound_violation_count"] == 0


def test_tuned_figure_match_candidate_records_explicit_nonpaper_knobs() -> None:
    config = PaperSectionV7DofConfig(
        duration_s=0.1,
        dt_s=0.004,
        solver_mode="pinv_bounded",
        orientation_mode="normal_only",
        force_loop_mode="admittance_proxy",
        force_integral_limit=5.0,
        force_integral_leak=1.5,
        escape_velocity_alpha=20.0,
        kp=25.0,
        max_angular_speed_rad_s=1.5,
        q7_nullspace_speed_rad_s=0.35,
    )
    result = simulate_paper_section_v_7dof(config)
    metrics = summarize_paper_section_v_7dof(result)
    assert metrics["execution_success"]
    assert metrics["claim_level"] == "paper_platform_7dof_tuned_figure_match_candidate"
    assert metrics["force_loop_mode"] == "admittance_proxy"
    assert metrics["solver_mode"] == "pinv_bounded"
    assert metrics["orientation_mode"] == "normal_only"
    assert metrics["force_integral_limit"] == 5.0
    assert metrics["force_integral_leak"] == 1.5
    assert metrics["q7_nullspace_speed_rad_s"] == 0.35
    assert metrics["escape_velocity_alpha"] == 20.0
    assert metrics["kp"] == 25.0
    assert metrics["max_angular_speed_rad_s"] == 1.5
    assert result.q_rad[-1, 6] > config.q0_rad[6]


def test_summary_records_fig6_q7_landmark_when_duration_covers_22s() -> None:
    q_rad = np.zeros((3, 7), dtype=float)
    q_rad[1, 6] = 1.675
    result = PaperSectionV7DofResult(
        config=PaperSectionV7DofConfig(duration_s=30.0),
        t_s=np.array([0.0, 22.0, 30.0], dtype=float),
        q_rad=q_rad,
        qdot_rad_s=np.zeros((3, 7), dtype=float),
        qddot_rad_s2=np.zeros((3, 7), dtype=float),
        lambda_1=np.zeros((3, 6), dtype=float),
        position_m=np.zeros((3, 3), dtype=float),
        desired_position_m=np.zeros((3, 3), dtype=float),
        position_error_m=np.zeros((3, 3), dtype=float),
        orientation_error_rad=np.zeros((3, 3), dtype=float),
        task_residual_norm=np.zeros(3, dtype=float),
        force_error_N=np.zeros(3, dtype=float),
        measured_force_N=np.full(3, 5.0, dtype=float),
        contact_active=np.ones(3, dtype=bool),
        penetration_m=np.zeros(3, dtype=float),
        commanded_task_velocity=np.zeros((3, 6), dtype=float),
        projected_qdot_raw=np.zeros((3, 7), dtype=float),
        projected_qdot=np.zeros((3, 7), dtype=float),
        velocity_clamp_active=np.zeros((3, 7), dtype=bool),
        condition_number=np.ones(3, dtype=float),
        desired_rotation_valid=np.ones(3, dtype=bool),
        z0_m=0.0,
        plane_z_m=0.0,
    )
    metrics = summarize_paper_section_v_7dof(result)
    assert metrics["fig6_q7_sample_time_s"] == 22.0
    assert metrics["fig6_q7_at_22s_rad"] == 1.675
    np.testing.assert_allclose(metrics["fig6_q7_abs_error_to_2p5_rad"], 0.825)


def test_q7_variant_probe_script_writes_single_short_variant(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            str(ROOT / "scripts/run_paper_7dof_q7_variant_probe.py"),
            "--duration-s",
            "0.02",
            "--dt-s",
            "0.01",
            "--solver-modes",
            "kkt_projection",
            "--orientation-modes",
            "normal_only",
            "--force-integral-limits",
            "0.1",
            "--output-dir",
            str(tmp_path / "q7_probe"),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "wrote" in completed.stdout
    payload = yaml.safe_load((tmp_path / "q7_probe" / "summary.yaml").read_text(encoding="utf-8"))
    assert payload["summary"]["variant_count"] == 1
    assert not payload["summary"]["all_q7_available"]
    assert payload["variants"][0]["variant_label"] == "kkt_normal_cap0p1"
    assert payload["variants"][0]["metrics"]["execution_success"]
