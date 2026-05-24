from __future__ import annotations

import json
import subprocess
import sys

import yaml


def test_create_read_only_calibration_measurement_run_keeps_claims_false(tmp_path) -> None:
    out_dir = tmp_path / "readonly_measurement"
    command = [
        sys.executable,
        "scripts/create_read_only_calibration_measurement_run.py",
        "--output-dir",
        str(out_dir),
        "--run-id",
        "TEST_RUN",
    ]

    completed = subprocess.run(command, cwd="/home/andy/reproduce-tase", text=True, capture_output=True, check=True)

    assert completed.stdout.strip() == str(out_dir)
    expected_files = {
        "README.md",
        "measurement_plan.md",
        "operator_checklist.md",
        "tcp_contact_measurements.csv",
        "plane_normal_measurements.csv",
        "force_source_comparison.csv",
        "orientation_gate_decision.md",
        "photos_manifest.md",
        "metrics.yaml",
        "metrics.json",
        "summary.md",
        "git_state.md",
    }
    assert expected_files.issubset({path.name for path in out_dir.iterdir()})

    metrics = yaml.safe_load((out_dir / "metrics.yaml").read_text(encoding="utf-8"))
    metrics_json = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))
    assert metrics_json == metrics
    assert metrics["run_id"] == "TEST_RUN"
    assert metrics["status"] == "scaffold_created_not_executed"
    assert metrics["template_source"] == "templates/read_only_calibration_measurement"
    assert metrics["execution"]["user_confirmed_read_only_step"] is False
    assert metrics["execution"]["live_hardware_accessed"] is False
    assert metrics["execution"]["robot_motion_commanded"] is False
    assert metrics["execution"]["configuration_written"] is False
    assert metrics["execution"]["zeroing_or_biasing_performed"] is False
    assert metrics["execution"]["force_control_run"] is False
    assert metrics["verdict"]["supports_contact_model_update"] is False
    assert metrics["verdict"]["supports_accepting_v85_margin"] is False
    assert metrics["verdict"]["supports_gate_relaxation"] is False
    assert metrics["verdict"]["supports_hardware_claim"] is False
    assert metrics["claim_boundary"]["hardware_readiness"] is False
