from __future__ import annotations

import json
import subprocess
import sys

import yaml


def run_audit(tmp_path):
    out_dir = tmp_path / "diagnostic_robustness_matrix_candidate"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_diagnostic_robustness_matrix_candidate.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_MATRIX",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )
    assert completed.stdout.strip() == str(out_dir)
    return out_dir, yaml.safe_load((out_dir / "metrics.yaml").read_text(encoding="utf-8"))


def test_diagnostic_robustness_matrix_candidate_reports_incomplete_goal(tmp_path) -> None:
    out_dir, metrics = run_audit(tmp_path)
    metrics_json = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))

    assert metrics_json == metrics
    assert metrics["overall_goal_complete"] is False
    assert metrics["candidate_matrix_complete"] is False
    assert metrics["accepted_as_robustness_proof"] is False
    assert metrics["completion_claim_allowed"] is False
    assert metrics["offline_actionable_from_v95"] is True

    boundary = metrics["claim_boundary"]
    assert boundary["do_not_mark_goal_complete"] is True
    assert boundary["robustness_claim"] is False
    assert boundary["robot_motion_authorized"] is False
    assert boundary["hardware_writes_authorized"] is False
    assert boundary["force_control_authorized"] is False
    assert boundary["hardware_readiness_claim"] is False


def test_diagnostic_robustness_matrix_candidate_tracks_failed_cells_and_dependencies(tmp_path) -> None:
    _, metrics = run_audit(tmp_path)

    matrix = metrics["matrix_definition"]
    cells = {item["id"]: item for item in matrix["cells"]}
    summary = metrics["matrix_summary"]

    assert matrix["scope"] == "diagnostic_candidate_only"
    assert summary["cell_count"] == 12
    assert summary["status_counts"]["passed_diagnostic"] == 7
    assert summary["status_counts"]["passed_diagnostic_nonfinal"] == 1
    assert summary["status_counts"]["failed"] == 4
    assert summary["all_cells_passed"] is False

    assert cells["baseline_nominal"]["status"] == "passed_diagnostic"
    assert cells["base_z_plus1mm"]["status"] == "failed"
    assert cells["positive_qdot012_full_matrix_18p035"]["status"] == "passed_diagnostic_nonfinal"
    assert cells["positive_qdot012_full_matrix_18p035"]["evidence"]["stitched_pass_count"] == 8
    assert cells["positive_fast_timing_0p0075"]["status"] == "failed"
    assert cells["positive_fast_timing_0p0075"]["evidence"]["failing_cases"] == [
        "delta_p1p000mm"
    ]
    assert cells["positive_orientation_gate_0p119"]["status"] == "failed"
    assert cells["weighted_plus1mm_0p119_gate"]["status"] == "failed"
    assert cells["weighted_plus1mm_0p119_gate"]["evidence"][
        "max_stage_b_excess_over_gate_rad"
    ] == 0.0005664520369604714

    assert "base_z_plus1mm" in summary["failed_cell_ids"]
    assert "positive_fast_timing_0p0075" in summary["failed_cell_ids"]
    assert "positive_orientation_gate_0p119" in summary["failed_cell_ids"]
    assert "weighted_plus1mm_0p119_gate" in summary["failed_cell_ids"]
    assert "positive_qdot012_full_matrix_18p035" in summary["nonfinal_recovered_cell_ids"]

    assert metrics["claim_dependencies"]["strict_feasibility_complete"] is False
    assert metrics["claim_dependencies"]["robustness_complete_from_v97"] is False
    assert "contact_calibration_claim" in metrics["blocking_dependencies"]
