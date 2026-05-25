from __future__ import annotations

import json
import subprocess
import sys

import yaml

from scripts.audit_read_only_sop_step_registry import audit_registry


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
        "ksm_contact_patch_convention.csv",
        "plane_normal_measurements.csv",
        "force_source_comparison.csv",
        "orientation_gate_semantics.csv",
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
    assert metrics["approved_step_registry"] == "configs/read_only_sop_step_registry.yaml"
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
    assert metrics["orientation_gate_acceptance"]["decision"] == "not_accepted"
    assert metrics["orientation_gate_acceptance"]["evidence_only"] is True
    assert metrics["orientation_gate_acceptance"]["requires_separate_gate_audit"] is True
    assert metrics["orientation_gate_acceptance"]["accepted_gate_value_rad"] is None


def test_read_only_sop_step_registry_is_scoped_and_auditable() -> None:
    payload = audit_registry()

    assert payload["audit_passed"] is True
    assert payload["violations"] == []
    assert payload["step_count"] == 6
    assert payload["finalizer_eligible_step_count"] == 5
    assert "phase0_static_bench_preflight" not in payload["finalizer_eligible_step_ids"]
    assert "phase1_mounted_stack_tcp_contact_measurement" in payload[
        "finalizer_eligible_step_ids"
    ]
    assert payload["claim_boundary"]["registry_authorizes_robot_motion"] is False
    assert payload["claim_boundary"]["registry_authorizes_configuration_writes"] is False
    assert payload["claim_boundary"]["registry_accepts_orientation_gate"] is False


def test_audit_read_only_sop_step_registry_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "registry_audit"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_sop_step_registry.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_REGISTRY",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.strip() == str(out_dir)
    metrics_yaml_text = (out_dir / "metrics.yaml").read_text(encoding="utf-8")
    metrics = yaml.safe_load(metrics_yaml_text)
    metrics_json = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))
    assert metrics_json == metrics
    assert "&id" not in metrics_yaml_text
    assert "*id" not in metrics_yaml_text
    assert metrics["audit_passed"] is True
    assert metrics["finalizer_eligible_step_count"] == 5
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()


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
    assert audit["orientation_gate_acceptance"]["decision"] == "not_accepted"
    assert audit["verdict"]["supports_hardware_claim"] is False
    assert audit["claim_boundary"]["hardware_readiness"] is False


def test_audit_read_only_calibration_measurement_run_rejects_optional_rows_in_scaffold(
    tmp_path,
) -> None:
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
    ksm_path = run_dir / "ksm_contact_patch_convention.csv"
    ksm_path.write_text(
        ksm_path.read_text(encoding="utf-8")
        + "k1,fixture_tip,flat leading face,seated visually,visual,pytest,synthetic test row\n",
        encoding="utf-8",
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
        check=False,
    )

    assert completed.returncode == 1
    audit = yaml.safe_load((audit_dir / "metrics.yaml").read_text(encoding="utf-8"))
    assert audit["audit_passed"] is False
    assert "ksm_contact_patch_convention.csv contains rows in scaffold mode" in audit["violations"]


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
    metrics["read_only_evidence_finalization"] = {
        "confirmation_phrase_matched": True,
        "approved_step_id": "phase1_mounted_stack_tcp_contact_measurement",
        "approved_step_title": "Mounted stack TCP/contact point read-only measurement",
        "approved_step_registry": "configs/read_only_sop_step_registry.yaml",
        "allowed_worksheets": ["tcp_contact_measurements.csv"],
        "operator": "pytest",
        "finalized_at_utc": "2026-05-25T00:00:00Z",
        "finalizer": "scripts/finalize_read_only_calibration_measurement_evidence.py",
        "live_hardware_accessed_declared": True,
        "worksheet_row_counts": {
            "tcp_contact_measurements.csv": 1,
            "ksm_contact_patch_convention.csv": 0,
            "plane_normal_measurements.csv": 0,
            "force_source_comparison.csv": 0,
            "orientation_gate_semantics.csv": 0,
        },
    }
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


def test_audit_read_only_calibration_measurement_run_rejects_orientation_acceptance_drift(
    tmp_path,
) -> None:
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
    metrics["execution"]["live_hardware_accessed"] = False
    metrics["evidence_status"]["orientation_gate_semantics"] = "collected_read_only"
    metrics["orientation_gate_acceptance"]["decision"] = "accepted"
    metrics["orientation_gate_acceptance"]["accepted_gate_value_rad"] = 0.119
    metrics["read_only_evidence_finalization"] = {
        "confirmation_phrase_matched": True,
        "approved_step_id": "phase5_orientation_gate_semantics_evidence",
        "approved_step_title": "Orientation gate semantics read-only evidence",
        "approved_step_registry": "configs/read_only_sop_step_registry.yaml",
        "allowed_worksheets": ["orientation_gate_semantics.csv"],
        "operator": "pytest",
        "finalized_at_utc": "2026-05-25T00:00:00Z",
        "finalizer": "scripts/finalize_read_only_calibration_measurement_evidence.py",
        "live_hardware_accessed_declared": False,
        "worksheet_row_counts": {
            "tcp_contact_measurements.csv": 0,
            "ksm_contact_patch_convention.csv": 0,
            "plane_normal_measurements.csv": 0,
            "force_source_comparison.csv": 0,
            "orientation_gate_semantics.csv": 1,
        },
    }
    (run_dir / "metrics.yaml").write_text(yaml.safe_dump(metrics, sort_keys=False), encoding="utf-8")
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    gate_path = run_dir / "orientation_gate_semantics.csv"
    gate_path.write_text(
        gate_path.read_text(encoding="utf-8")
        + "g1,normal_alignment,0.119,plane_normal_fixture,contact_fixture,0.03,14.0,unresolved,pytest,synthetic test row\n",
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
        check=False,
    )

    assert completed.returncode == 1
    audit = yaml.safe_load((audit_dir / "metrics.yaml").read_text(encoding="utf-8"))
    assert audit["audit_passed"] is False
    assert "orientation_gate_acceptance.decision is not not_accepted" in audit["violations"]
    assert "orientation_gate_acceptance.accepted_gate_value_rad is not null" in audit["violations"]


def test_finalize_read_only_calibration_measurement_evidence_derives_status(tmp_path) -> None:
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
    tcp_path = run_dir / "tcp_contact_measurements.csv"
    tcp_path.write_text(
        tcp_path.read_text(encoding="utf-8")
        + "s1,approved_read_only_fixture,+z,85.0,caliper,0.01,test,synthetic test row\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/finalize_read_only_calibration_measurement_evidence.py",
            str(run_dir),
            "--confirmation-phrase",
            "I approve this read-only measurement step",
            "--approved-step-id",
            "phase1_mounted_stack_tcp_contact_measurement",
            "--operator",
            "pytest",
            "--live-hardware-accessed",
            "false",
            "--finalized-at-utc",
            "2026-05-25T00:00:00Z",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.strip() == str(run_dir.resolve())
    metrics = yaml.safe_load((run_dir / "metrics.yaml").read_text(encoding="utf-8"))
    metrics_json = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    assert metrics_json == metrics
    assert metrics["status"] == "approved_read_only_evidence"
    assert metrics["execution"]["user_confirmed_read_only_step"] is True
    assert metrics["execution"]["live_hardware_accessed"] is False
    assert metrics["execution"]["robot_motion_commanded"] is False
    assert metrics["execution"]["configuration_written"] is False
    assert metrics["execution"]["zeroing_or_biasing_performed"] is False
    assert metrics["execution"]["force_control_run"] is False
    assert metrics["evidence_status"]["mounted_stack_tcp_contact_point"] == "collected_read_only"
    assert metrics["evidence_status"]["ksm_contact_patch_convention"] == "not_collected"
    assert metrics["evidence_status"]["plane_normal_robot_base_frame"] == "not_collected"
    assert metrics["evidence_status"]["orientation_gate_semantics"] == "not_accepted"
    assert metrics["orientation_gate_acceptance"]["decision"] == "not_accepted"
    assert metrics["orientation_gate_acceptance"]["evidence_only"] is True
    assert metrics["orientation_gate_acceptance"]["requires_separate_gate_audit"] is True
    assert metrics["orientation_gate_acceptance"]["accepted_gate_value_rad"] is None
    assert metrics["orientation_gate_acceptance"]["orientation_semantics_rows"] == 0
    assert metrics["verdict"]["supports_hardware_claim"] is False
    assert metrics["claim_boundary"]["hardware_readiness"] is False
    assert (
        metrics["read_only_evidence_finalization"]["approved_step_id"]
        == "phase1_mounted_stack_tcp_contact_measurement"
    )
    assert (
        metrics["read_only_evidence_finalization"]["approved_step_registry"]
        == "configs/read_only_sop_step_registry.yaml"
    )
    assert metrics["read_only_evidence_finalization"]["allowed_worksheets"] == [
        "tcp_contact_measurements.csv"
    ]
    assert metrics["read_only_evidence_finalization"]["worksheet_row_counts"][
        "tcp_contact_measurements.csv"
    ] == 1
    assert metrics["read_only_evidence_finalization"]["worksheet_row_counts"][
        "ksm_contact_patch_convention.csv"
    ] == 0
    assert metrics["read_only_evidence_finalization"]["worksheet_row_counts"][
        "orientation_gate_semantics.csv"
    ] == 0

    subprocess.run(
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
    audit = yaml.safe_load((audit_dir / "metrics.yaml").read_text(encoding="utf-8"))
    assert audit["audit_mode"] == "approved-read-only"
    assert audit["audit_passed"] is True
    assert audit["violations"] == []


def test_audit_read_only_calibration_measurement_rejects_invalid_phase1_row(
    tmp_path,
) -> None:
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
    metrics["evidence_status"]["mounted_stack_tcp_contact_point"] = "collected_read_only"
    metrics["read_only_evidence_finalization"] = {
        "confirmation_phrase_matched": True,
        "approved_step_id": "phase1_mounted_stack_tcp_contact_measurement",
        "approved_step_title": "Mounted stack TCP/contact point read-only measurement",
        "approved_step_registry": "configs/read_only_sop_step_registry.yaml",
        "allowed_worksheets": ["tcp_contact_measurements.csv"],
        "operator": "pytest",
        "finalized_at_utc": "2026-05-25T00:00:00Z",
        "finalizer": "scripts/finalize_read_only_calibration_measurement_evidence.py",
        "live_hardware_accessed_declared": False,
        "worksheet_row_counts": {
            "tcp_contact_measurements.csv": 1,
            "ksm_contact_patch_convention.csv": 0,
            "plane_normal_measurements.csv": 0,
            "force_source_comparison.csv": 0,
            "orientation_gate_semantics.csv": 0,
        },
    }
    (run_dir / "metrics.yaml").write_text(yaml.safe_dump(metrics, sort_keys=False), encoding="utf-8")
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    tcp_path = run_dir / "tcp_contact_measurements.csv"
    tcp_path.write_text(
        tcp_path.read_text(encoding="utf-8")
        + "s1,TBD,sideways,not_numeric,unknown,0,TBD,invalid test row\n",
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
        check=False,
    )

    assert completed.returncode == 1
    audit = yaml.safe_load((audit_dir / "metrics.yaml").read_text(encoding="utf-8"))
    assert audit["audit_passed"] is False
    assert "tcp_contact_measurements.csv row 1.datum must be non-empty and not a placeholder" in audit[
        "violations"
    ]
    assert any("tool_axis_sign must be one of" in violation for violation in audit["violations"])
    assert "tcp_contact_measurements.csv row 1.distance_mm is not numeric" in audit[
        "violations"
    ]
    assert "tcp_contact_measurements.csv row 1.resolution_mm must be finite and positive" in audit[
        "violations"
    ]
    assert "tcp_contact_measurements.csv row 1.operator must be non-empty and not a placeholder" in audit[
        "violations"
    ]


def test_finalize_read_only_calibration_measurement_rejects_invalid_phase1_row_before_write(
    tmp_path,
) -> None:
    run_dir = tmp_path / "readonly_measurement"
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
    tcp_path = run_dir / "tcp_contact_measurements.csv"
    tcp_path.write_text(
        tcp_path.read_text(encoding="utf-8")
        + "s1,approved_read_only_fixture,+z,0,caliper,0.01,TBD,invalid test row\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/finalize_read_only_calibration_measurement_evidence.py",
            str(run_dir),
            "--confirmation-phrase",
            "I approve this read-only measurement step",
            "--approved-step-id",
            "phase1_mounted_stack_tcp_contact_measurement",
            "--operator",
            "pytest",
            "--live-hardware-accessed",
            "false",
            "--finalized-at-utc",
            "2026-05-25T00:00:00Z",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "tcp_contact_measurements.csv row 1.distance_mm must be finite and positive" in completed.stderr
    assert "tcp_contact_measurements.csv row 1.operator must be non-empty and not a placeholder" in completed.stderr
    metrics = yaml.safe_load((run_dir / "metrics.yaml").read_text(encoding="utf-8"))
    assert metrics["status"] == "scaffold_created_not_executed"
    assert metrics["execution"]["user_confirmed_read_only_step"] is False
    assert "read_only_evidence_finalization" not in metrics


def test_finalize_read_only_calibration_measurement_evidence_rejects_missing_approval(
    tmp_path,
) -> None:
    run_dir = tmp_path / "readonly_measurement"
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
    tcp_path = run_dir / "tcp_contact_measurements.csv"
    tcp_path.write_text(
        tcp_path.read_text(encoding="utf-8")
        + "s1,approved_read_only_fixture,+z,85.0,caliper,0.01,test,synthetic test row\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/finalize_read_only_calibration_measurement_evidence.py",
            str(run_dir),
            "--confirmation-phrase",
            "wrong phrase",
            "--approved-step-id",
            "TEST_READ_ONLY_STEP",
            "--operator",
            "pytest",
            "--live-hardware-accessed",
            "false",
            "--finalized-at-utc",
            "2026-05-25T00:00:00Z",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "approval phrase mismatch" in completed.stderr
    metrics = yaml.safe_load((run_dir / "metrics.yaml").read_text(encoding="utf-8"))
    assert metrics["status"] == "scaffold_created_not_executed"
    assert metrics["execution"]["user_confirmed_read_only_step"] is False


def test_finalize_read_only_calibration_measurement_evidence_rejects_unknown_step_id(
    tmp_path,
) -> None:
    run_dir = tmp_path / "readonly_measurement"
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
    tcp_path = run_dir / "tcp_contact_measurements.csv"
    tcp_path.write_text(
        tcp_path.read_text(encoding="utf-8")
        + "s1,approved_read_only_fixture,+z,85.0,caliper,0.01,test,synthetic test row\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/finalize_read_only_calibration_measurement_evidence.py",
            str(run_dir),
            "--confirmation-phrase",
            "I approve this read-only measurement step",
            "--approved-step-id",
            "TEST_READ_ONLY_STEP",
            "--operator",
            "pytest",
            "--live-hardware-accessed",
            "false",
            "--finalized-at-utc",
            "2026-05-25T00:00:00Z",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "approved_step_id 'TEST_READ_ONLY_STEP' is not in" in completed.stderr
    metrics = yaml.safe_load((run_dir / "metrics.yaml").read_text(encoding="utf-8"))
    assert metrics["status"] == "scaffold_created_not_executed"


def test_finalize_read_only_calibration_measurement_evidence_rejects_disallowed_rows(
    tmp_path,
) -> None:
    run_dir = tmp_path / "readonly_measurement"
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
    tcp_path = run_dir / "tcp_contact_measurements.csv"
    tcp_path.write_text(
        tcp_path.read_text(encoding="utf-8")
        + "s1,approved_read_only_fixture,+z,85.0,caliper,0.01,test,synthetic test row\n",
        encoding="utf-8",
    )
    ksm_path = run_dir / "ksm_contact_patch_convention.csv"
    ksm_path.write_text(
        ksm_path.read_text(encoding="utf-8")
        + "k1,fixture_tip,flat leading face,seated visually,visual,pytest,synthetic test row\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/finalize_read_only_calibration_measurement_evidence.py",
            str(run_dir),
            "--confirmation-phrase",
            "I approve this read-only measurement step",
            "--approved-step-id",
            "phase1_mounted_stack_tcp_contact_measurement",
            "--operator",
            "pytest",
            "--live-hardware-accessed",
            "false",
            "--finalized-at-utc",
            "2026-05-25T00:00:00Z",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "does not allow rows in: ksm_contact_patch_convention.csv" in completed.stderr
    metrics = yaml.safe_load((run_dir / "metrics.yaml").read_text(encoding="utf-8"))
    assert metrics["status"] == "scaffold_created_not_executed"
