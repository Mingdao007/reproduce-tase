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


def test_audit_read_only_calibration_measurement_run_accepts_scaffold(tmp_path) -> None:
    run_dir = tmp_path / "readonly_measurement"
    audit_dir = tmp_path / "audit"
    subprocess.run(
        [
            sys.executable,
            "scripts/create_read_only_calibration_measurement_run.py",
            "--output-dir",
            str(run_dir),
            "--run-id",
            "TEST_RUN",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_calibration_measurement_run.py",
            str(run_dir),
            "--output-dir",
            str(audit_dir),
            "--run-id",
            "TEST_AUDIT",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.strip() == str(audit_dir)
    audit = yaml.safe_load((audit_dir / "metrics.yaml").read_text(encoding="utf-8"))
    audit_json = json.loads((audit_dir / "metrics.json").read_text(encoding="utf-8"))
    assert audit_json == audit
    assert audit["audit_mode"] == "scaffold"
    assert audit["audit_passed"] is True
    assert audit["violations"] == []
    assert audit["run_status"] == "scaffold_created_not_executed"
    assert audit["execution"]["live_hardware_accessed"] is False
    assert audit["verdict"]["supports_hardware_claim"] is False
    assert audit["claim_boundary"]["hardware_readiness"] is False


def test_audit_read_only_calibration_measurement_run_accepts_approved_read_only(tmp_path) -> None:
    run_dir = tmp_path / "readonly_measurement"
    audit_dir = tmp_path / "audit"
    subprocess.run(
        [
            sys.executable,
            "scripts/create_read_only_calibration_measurement_run.py",
            "--output-dir",
            str(run_dir),
            "--run-id",
            "TEST_RUN",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )
    metrics = yaml.safe_load((run_dir / "metrics.yaml").read_text(encoding="utf-8"))
    metrics["status"] = "approved_read_only_evidence"
    metrics["execution"]["user_confirmed_read_only_step"] = True
    metrics["execution"]["live_hardware_accessed"] = True
    metrics["evidence_status"]["mounted_stack_tcp_contact_point"] = "collected_read_only"
    (run_dir / "metrics.yaml").write_text(yaml.safe_dump(metrics, sort_keys=False), encoding="utf-8")
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    tcp_path = run_dir / "tcp_contact_measurements.csv"
    tcp_path.write_text(
        tcp_path.read_text(encoding="utf-8")
        + "s1,approved_read_only_fixture,+z,85.0,caliper,0.01,test,synthetic test row\n",
        encoding="utf-8",
    )
    (run_dir / "summary.md").write_text(
        "# Read-Only Calibration Measurement Summary\n\n"
        "Status: `approved_read_only_evidence`\n\n"
        "All hardware-readiness claims remain false.\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_calibration_measurement_run.py",
            str(run_dir),
            "--audit-mode",
            "approved-read-only",
            "--output-dir",
            str(audit_dir),
            "--run-id",
            "TEST_AUDIT",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.strip() == str(audit_dir)
    audit = yaml.safe_load((audit_dir / "metrics.yaml").read_text(encoding="utf-8"))
    assert audit["audit_mode"] == "approved-read-only"
    assert audit["audit_passed"] is True
    assert audit["violations"] == []
    assert audit["execution"]["user_confirmed_read_only_step"] is True
    assert audit["execution"]["live_hardware_accessed"] is True
    assert audit["verdict"]["supports_hardware_claim"] is False
    assert audit["claim_boundary"]["hardware_readiness"] is False


def test_audit_read_only_calibration_measurement_run_rejects_claim_drift(tmp_path) -> None:
    run_dir = tmp_path / "readonly_measurement"
    audit_dir = tmp_path / "audit"
    subprocess.run(
        [
            sys.executable,
            "scripts/create_read_only_calibration_measurement_run.py",
            "--output-dir",
            str(run_dir),
            "--run-id",
            "TEST_RUN",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )
    metrics = yaml.safe_load((run_dir / "metrics.yaml").read_text(encoding="utf-8"))
    metrics["verdict"]["supports_hardware_claim"] = True
    (run_dir / "metrics.yaml").write_text(yaml.safe_dump(metrics, sort_keys=False), encoding="utf-8")
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_calibration_measurement_run.py",
            str(run_dir),
            "--output-dir",
            str(audit_dir),
            "--run-id",
            "TEST_AUDIT",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    audit = yaml.safe_load((audit_dir / "metrics.yaml").read_text(encoding="utf-8"))
    assert audit["audit_passed"] is False
    assert "expected false field is not false: verdict.supports_hardware_claim" in audit["violations"]
