from __future__ import annotations

import json
import subprocess
import sys

import yaml


def run_audit(tmp_path):
    out_dir = tmp_path / "strict_feasibility_blockers"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_strict_feasibility_blockers.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_STRICT",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )
    assert completed.stdout.strip() == str(out_dir)
    return out_dir, yaml.safe_load((out_dir / "metrics.yaml").read_text(encoding="utf-8"))


def test_strict_feasibility_blockers_reports_incomplete_goal(tmp_path) -> None:
    out_dir, metrics = run_audit(tmp_path)
    metrics_json = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))

    assert metrics_json == metrics
    assert metrics["overall_goal_complete"] is False
    assert metrics["strict_feasibility_complete"] is False
    assert metrics["strict_setup_gate_complete"] is False
    assert metrics["strict_paper_equivalent_full_staged_feasibility_achieved"] is False
    assert metrics["trajectory_gate_often_passes"] is True
    assert metrics["completion_claim_allowed"] is False
    assert metrics["offline_actionable_from_v95"] is True

    boundary = metrics["claim_boundary"]
    assert boundary["do_not_mark_goal_complete"] is True
    assert boundary["robot_motion_authorized"] is False
    assert boundary["hardware_writes_authorized"] is False
    assert boundary["force_control_authorized"] is False
    assert boundary["hardware_readiness_claim"] is False


def test_strict_feasibility_blockers_identifies_setup_tradeoff(tmp_path) -> None:
    _, metrics = run_audit(tmp_path)

    blockers = metrics["blocker_summary"]
    assert blockers["strict_case_count"] == 4
    assert blockers["strict_full_staged_feasibility_pass_count"] == 0
    assert blockers["three_phase_case_count"] == 10
    assert blockers["setup_terminal_state_pass_count"] == 0
    assert blockers["trajectory_feasibility_pass_count"] == 8
    assert blockers["three_phase_full_staged_feasibility_pass_count"] == 0
    assert blockers["primary_blocker"] == "strict_setup_terminal_tradeoff"
    assert "strict_setup_terminal_tradeoff" in blockers["blocker_ids"]

    posture = metrics["posture_regularized"]
    assert posture["case_count"] == 4
    assert posture["approach_feasibility_pass_count"] == 0
    assert posture["trajectory_feasibility_pass_count"] == 4
    assert posture["full_staged_feasibility_pass_count"] == 0
    assert posture["all_approaches_orientation_within_strict_gate"] is True
    assert posture["all_approaches_tangential_outside_strict_gate"] is True
    assert posture["strict_failure_counts"]["final_tangential_position_error_m"] == 4
    assert posture["strict_failure_counts"]["final_orientation_error_rad"] == 0

    three_phase = metrics["three_phase_settle"]
    assert three_phase["case_count"] == 10
    assert three_phase["setup_terminal_state_pass_count"] == 0
    assert three_phase["trajectory_feasibility_pass_count"] == 8
    assert three_phase["planned_setup_then_trajectory_pass_count"] == 0
    assert three_phase["setup_failed_criteria_counts"]["final_tangential_position_error_m"] == 8
    assert three_phase["setup_failed_criteria_counts"]["final_orientation_error_rad"] == 2
    assert three_phase["setup_failed_criteria_counts"]["tail_mean_abs_force_error_N"] == 3
    assert three_phase["qdot_saturation_summary"]["exceedance_count"] == 8
    assert three_phase["qdot_saturation_summary"]["missing_count"] == 2
    assert three_phase["qdot_saturation_summary"]["settled_rows_all_exceed"] is True

    best = three_phase["best_observed_metrics"]
    assert best["best_tangential_position_error_m"]["case"] == "lp4_settle_lp4"
    assert best["best_orientation_error_rad"]["case"] == "baseline_no_recenter"
    assert best["best_settle_tail_mean_abs_force_error_N"]["case"] == "lp4_settle_lp4"
