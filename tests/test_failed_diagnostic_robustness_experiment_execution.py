from __future__ import annotations

import json
import subprocess
import sys

import yaml


def run_audit(tmp_path):
    out_dir = tmp_path / "failed_diagnostic_robustness_experiment_audit"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_failed_diagnostic_robustness_experiment_execution.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_FAILED_EXECUTION_AUDIT",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )
    assert completed.stdout.strip() == str(out_dir)
    return out_dir, yaml.safe_load((out_dir / "metrics.yaml").read_text(encoding="utf-8"))


def test_failed_experiment_execution_audit_preserves_claim_boundary(tmp_path) -> None:
    out_dir, metrics = run_audit(tmp_path)
    metrics_json = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))

    assert metrics_json == metrics
    assert metrics["run_id"] == "TEST_FAILED_EXECUTION_AUDIT"
    assert metrics["status"] == "completed"
    assert metrics["summary"]["cell_count"] == 4
    assert metrics["summary"]["executed_cell_count"] == 3
    assert metrics["summary"]["closed_cell_count"] == 0
    assert metrics["summary"]["not_executed_cell_count"] == 1
    assert metrics["summary"]["all_failed_cells_closed"] is False
    assert metrics["summary"]["closed_cell_ids"] == []
    assert metrics["summary"]["unresolved_executed_cell_ids"] == [
        "base_z_plus1mm",
        "positive_fast_timing_0p0075",
        "positive_orientation_gate_0p119",
    ]

    boundary = metrics["claim_boundary"]
    assert boundary["do_not_mark_goal_complete"] is True
    assert boundary["robustness_claim"] is False
    assert boundary["paper_equivalent_feasibility"] is False
    assert boundary["contact_calibration_claim"] is False
    assert boundary["orientation_gate_acceptance"] is False
    assert boundary["robot_motion_authorized"] is False
    assert boundary["hardware_writes_authorized"] is False
    assert boundary["force_control_authorized"] is False
    assert boundary["hardware_readiness_claim"] is False


def test_failed_experiment_execution_audit_reports_base_z_unresolved(tmp_path) -> None:
    _, metrics = run_audit(tmp_path)

    results = {item["cell_id"]: item for item in metrics["cell_results"]}
    base_z = results["base_z_plus1mm"]

    assert base_z["status"] == "executed_unresolved"
    assert base_z["closure_passed"] is False
    assert base_z["experiment_metrics"].endswith(
        "runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm/metrics.yaml"
    )
    assert base_z["aggregate"]["case_count"] == 1
    assert base_z["aggregate"]["start_pass_count"] == 0
    assert base_z["aggregate"]["terminal_pass_count"] == 0
    assert base_z["aggregate"]["path_geometry_pass_count"] == 0
    assert base_z["aggregate"]["duration_recovered_count"] == 0

    checks = base_z["closure_checks"]
    assert checks["planned_parameters_match"]["all_matched"] is True
    assert checks["source_delta_present"]["passed"] is True
    assert checks["start_contact_recovered"]["passed"] is False
    assert checks["terminal_target_recovered"]["passed"] is False
    assert checks["path_geometry_recovered"]["passed"] is False
    assert checks["duration_recovered"]["passed"] is False
    assert checks["terminal_target_recovered"]["orientation_error_rad"] == 0.11948560786548146

    assert results["weighted_plus1mm_0p119_gate"]["status"] == "not_executed"


def test_failed_experiment_execution_audit_reports_fast_timing_unresolved(tmp_path) -> None:
    _, metrics = run_audit(tmp_path)

    results = {item["cell_id"]: item for item in metrics["cell_results"]}
    fast_timing = results["positive_fast_timing_0p0075"]

    assert fast_timing["status"] == "executed_unresolved"
    assert fast_timing["closure_passed"] is False
    assert fast_timing["experiment_metrics"].endswith(
        "runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075/metrics.yaml"
    )
    assert fast_timing["aggregate"]["matrix_case_count"] == 1
    assert fast_timing["aggregate"]["matrix_stitched_pass_count"] == 0
    assert fast_timing["aggregate"]["matrix_stitched_fail_count"] == 1
    assert fast_timing["aggregate"]["failing_scenarios"] == ["paper_time_scale_0p0075"]

    checks = fast_timing["closure_checks"]
    assert checks["planned_parameters_match"]["all_matched"] is True
    assert checks["source_delta_present"]["passed"] is True
    assert checks["scenario_present"]["passed"] is True
    assert checks["stage_a_recovered"]["passed"] is True
    assert checks["stitched_recovered"]["passed"] is False
    assert checks["stitched_recovered"]["handoff_pass_count"] == 3
    assert checks["stitched_recovered"]["handoff_trajectory_count"] == 4
    assert checks["stage_b_all_rows_passed"]["passed"] is False
    assert checks["stage_b_all_rows_passed"]["failed_rows"] == [
        {
            "trajectory": "e2-figure-eight",
            "failed_criteria": [
                "qdot_saturation_fraction",
                "tail_max_qdot_utilization",
                "max_orientation_error_rad",
            ],
        }
    ]
    assert checks["qdot_saturation_clear"]["passed"] is False
    assert checks["tail_qdot_utilization_clear"]["passed"] is False
    assert checks["orientation_gate_clear"]["passed"] is False
    assert checks["orientation_gate_clear"]["stage_b_max_orientation_error_rad"] == 0.12020305872871904


def test_failed_experiment_execution_audit_reports_orientation_gate_unresolved(tmp_path) -> None:
    _, metrics = run_audit(tmp_path)

    results = {item["cell_id"]: item for item in metrics["cell_results"]}
    orientation = results["positive_orientation_gate_0p119"]

    assert orientation["status"] == "executed_unresolved"
    assert orientation["closure_passed"] is False
    assert orientation["experiment_metrics"].endswith(
        "runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119/metrics.yaml"
    )
    assert orientation["aggregate"]["case_count"] == 9
    assert orientation["aggregate"]["stitched_pass_count"] == 2
    assert orientation["aggregate"]["stitched_fail_count"] == 7
    assert orientation["aggregate"]["min_passing_orientation_gate_rad"] == 0.11998
    assert orientation["aggregate"]["max_failing_orientation_gate_rad"] == 0.11997
    assert orientation["aggregate"]["max_stage_b_orientation_error_rad"] == 0.1199788204275829

    checks = orientation["closure_checks"]
    assert checks["planned_parameters_match"]["all_matched"] is True
    assert checks["source_delta_present"]["passed"] is True
    assert checks["current_gate_present"]["passed"] is True
    assert checks["current_gate_stitched_recovered"]["passed"] is False
    assert checks["current_gate_stitched_recovered"]["stage_a_passed"] is False
    assert checks["current_gate_stitched_recovered"]["handoff_pass_count"] == 0
    assert checks["current_gate_stitched_recovered"]["handoff_trajectory_count"] == 4
    assert checks["boundary_identified"]["passed"] is True
    assert checks["passes_at_or_below_current_gate"]["passed"] is False
    assert checks["passes_at_or_below_current_gate"]["current_gate_rad"] == 0.119
    assert checks["passes_at_or_below_current_gate"]["min_passing_orientation_gate_rad"] == 0.11998
    assert checks["gate_relaxation_not_accepted"]["passed"] is True
