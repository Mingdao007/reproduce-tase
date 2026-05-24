from __future__ import annotations

import json
import subprocess
import sys

import yaml


def run_audit(tmp_path):
    out_dir = tmp_path / "robustness_blockers"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_robustness_blockers.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_ROBUSTNESS",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )
    assert completed.stdout.strip() == str(out_dir)
    return out_dir, yaml.safe_load((out_dir / "metrics.yaml").read_text(encoding="utf-8"))


def test_robustness_blockers_reports_incomplete_goal(tmp_path) -> None:
    out_dir, metrics = run_audit(tmp_path)
    metrics_json = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))

    assert metrics_json == metrics
    assert metrics["overall_goal_complete"] is False
    assert metrics["robustness_complete"] is False
    assert metrics["completion_claim_allowed"] is False
    assert metrics["offline_actionable_from_v95"] is True
    assert metrics["strict_feasibility_complete_from_v96"] is False

    boundary = metrics["claim_boundary"]
    assert boundary["do_not_mark_goal_complete"] is True
    assert boundary["robustness_claim"] is False
    assert boundary["robot_motion_authorized"] is False
    assert boundary["hardware_writes_authorized"] is False
    assert boundary["force_control_authorized"] is False
    assert boundary["hardware_readiness_claim"] is False


def test_robustness_blockers_summarizes_current_failures(tmp_path) -> None:
    _, metrics = run_audit(tmp_path)

    baseline = metrics["baseline_sensitivity"]
    assert baseline["case_count"] == 9
    assert baseline["stitched_pass_count"] == 4
    assert baseline["stitched_fail_count"] == 5
    assert baseline["all_cases_passed"] is False
    assert set(baseline["failing_cases"]) == {
        "base_z_minus_1mm",
        "base_z_plus_1mm",
        "stage_a_14s",
        "qdot_limit_0p12",
        "paper_time_scale_0p02",
    }
    assert baseline["stage_b_failed_criteria_counts"]["qdot_saturation_fraction"] >= 1
    assert baseline["stage_b_failed_criteria_counts"]["tail_mean_abs_force_error_N"] >= 1

    base_z_recovery = metrics["base_z_recovery"]
    assert base_z_recovery["recovered_count"] == 1
    assert base_z_recovery["unresolved_cases"] == ["base_z_minus_1mm", "base_z_plus_1mm"]

    base_z_bracket = metrics["base_z_bracket"]
    assert base_z_bracket["case_count"] == 13
    assert base_z_bracket["max_positive_terminal_pass_delta_mm"] is None
    assert base_z_bracket["max_positive_recovered_delta_mm"] is None
    assert "delta_p1p000mm" in base_z_bracket["unresolved_cases"]

    positive = metrics["positive_stitched_sensitivity"]
    assert positive["matrix_case_count"] == 40
    assert positive["matrix_stitched_pass_count"] == 37
    assert positive["matrix_stitched_fail_count"] == 3
    assert set(positive["failing_scenarios"]) == {
        "qdot012_stage_a18s",
        "paper_time_scale_0p0075",
        "orientation_gate_0p119",
    }
    assert positive["failing_scenario_details"]["paper_time_scale_0p0075"]["failing_cases"] == [
        "delta_p1p000mm"
    ]

    qdot012 = metrics["qdot012_positive_recovery"]
    assert qdot012["case_count"] == 8
    assert qdot012["stitched_pass_count"] == 8
    assert qdot012["all_cases_passed"] is True
    assert qdot012["claim_scope"] == "diagnostic_positive_recovery_not_formal_robustness"

    orientation = metrics["weighted_orientation_model_sensitivity"]
    assert orientation["orientation_gate_rad"] == 0.119
    assert orientation["all_critical_rows_fail_plus1mm_gate"] is True
    assert orientation["max_stage_b_excess_over_gate_rad"] == 0.0005664520369604714

    blockers = metrics["blocker_summary"]
    assert blockers["primary_blocker"] == "accepted_model_robustness_not_closed"
    assert "contact_model_calibration_missing" in blockers["unresolved_blocker_ids"]
    assert "positive_relaxed_full_matrix_qdot012_18p035" in blockers["recovered_nonfinal_ids"]
