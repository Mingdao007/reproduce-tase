from __future__ import annotations

import json
import os
import subprocess
import sys

import yaml


EXPECTED_FAILED_CELLS = [
    "base_z_plus1mm",
    "positive_fast_timing_0p0075",
    "positive_orientation_gate_0p119",
    "weighted_plus1mm_0p119_gate",
]


def run_audit(tmp_path):
    out_dir = tmp_path / "failed_diagnostic_robustness_experiment_matrix"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/create_failed_diagnostic_robustness_experiment_matrix.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_FAILED_MATRIX",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )
    assert completed.stdout.strip() == str(out_dir)
    return out_dir, yaml.safe_load((out_dir / "metrics.yaml").read_text(encoding="utf-8"))


def test_failed_diagnostic_robustness_matrix_is_planned_only(tmp_path) -> None:
    out_dir, metrics = run_audit(tmp_path)
    metrics_json = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))

    assert metrics_json == metrics
    assert metrics["run_id"] == "TEST_FAILED_MATRIX"
    assert metrics["status"] == "planned_not_executed"
    assert metrics["source_failed_cell_ids"] == EXPECTED_FAILED_CELLS
    assert metrics["experiment_summary"]["experiment_count"] == 4
    assert metrics["experiment_summary"]["planned_not_executed_count"] == 4
    assert metrics["experiment_summary"]["cell_ids"] == EXPECTED_FAILED_CELLS
    assert metrics["experiment_summary"]["all_expected_scripts_exist"] is True
    assert metrics["experiment_summary"]["all_commands_have_output_dirs"] is True

    commands_path = out_dir / "commands.sh"
    assert commands_path.exists()
    assert os.access(commands_path, os.X_OK)
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
    assert not any((out_dir / "experiments" / cell_id).exists() for cell_id in EXPECTED_FAILED_CELLS)

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


def test_failed_diagnostic_robustness_matrix_commands_target_failed_cells(tmp_path) -> None:
    out_dir, metrics = run_audit(tmp_path)

    experiments = {item["id"]: item for item in metrics["experiments"]}
    assert list(experiments) == EXPECTED_FAILED_CELLS
    assert all(item["status"] == "planned_not_executed" for item in experiments.values())
    assert all(item["execution_scope"] == "offline_simulation_only" for item in experiments.values())
    assert all(item["source_failed_cell"]["status"] == "failed" for item in experiments.values())
    assert all("--output-dir" in item["command"] for item in experiments.values())

    assert experiments["base_z_plus1mm"]["command"][1].endswith(
        "scripts/audit_stage_a_base_z_bracket.py"
    )
    assert "--stage-a-durations-s" in experiments["base_z_plus1mm"]["command"]
    assert "15.0,16.0,18.0" in experiments["base_z_plus1mm"]["command"]

    positive_fast = experiments["positive_fast_timing_0p0075"]["command"]
    assert positive_fast[1].endswith("scripts/audit_positive_stitched_sensitivity.py")
    assert "--scenarios" in positive_fast
    assert "paper_time_scale_0p0075" in positive_fast

    positive_gate = experiments["positive_orientation_gate_0p119"]["command"]
    assert positive_gate[1].endswith("scripts/audit_positive_orientation_gate_boundary.py")
    assert "--orientation-gates" in positive_gate
    assert "0.119,0.11925,0.1195,0.11975,0.1199,0.11995,0.11997,0.11998,0.12" in positive_gate

    weighted = experiments["weighted_plus1mm_0p119_gate"]["command"]
    assert weighted[1].endswith("scripts/audit_weighted_gate_time_matrix.py")
    assert "--boundary-base-z-delta-mm" in weighted
    assert "0.119,0.11925,0.1195,0.11955,0.1196,0.1197,0.11995" in weighted

    commands = (out_dir / "commands.sh").read_text(encoding="utf-8")
    for cell_id in EXPECTED_FAILED_CELLS:
        assert f"# {cell_id}:" in commands
        assert str(out_dir / "experiments" / cell_id) in commands
