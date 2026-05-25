from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_read_only_finalization_rehearsal_boundary import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "configs" / "read_only_sop_step_registry.yaml"
DOWNSTREAM_GUARD = (
    ROOT / "runs" / "downstream_row_quality_guard" / "20260525T121000" / "metrics.yaml"
)
READ_ONLY_RUN_ROOT = ROOT / "runs" / "read_only_calibration_measurement"
READ_ONLY_AUDIT_ROOT = ROOT / "runs" / "read_only_calibration_measurement_run_audit"


def build_current_payload(**overrides):
    kwargs = {
        "registry_path": REGISTRY,
        "downstream_guard_path": DOWNSTREAM_GUARD,
        "read_only_run_root": READ_ONLY_RUN_ROOT,
        "read_only_audit_root": READ_ONLY_AUDIT_ROOT,
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_finalization_rehearsal_boundary_rehearses_all_registered_steps() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["finalization_rehearsal_boundary_complete"] is True
    assert summary["source_downstream_guard_audit_passed"] is True
    assert summary["registered_finalizer_step_count"] == 5
    assert summary["rehearsed_step_count"] == 5
    assert summary["rehearsal_passed_step_count"] == 5
    assert summary["temporary_finalization_count"] == 5
    assert summary["approved_read_only_verifier_passed_count"] == 5
    assert summary["synthetic_row_only_count"] == 5
    assert summary["live_hardware_accessed_count"] == 0
    assert summary["temporary_root_removed"] is True
    assert summary["repository_approved_read_only_run_delta"] == 0
    assert summary["repository_finalization_record_delta"] == 0
    assert summary["repository_approved_read_only_audit_delta"] == 0
    assert summary["repository_evidence_run_created_by_rehearsal"] is False
    assert summary["repository_evidence_audit_created_by_rehearsal"] is False
    assert summary["approved_read_only_evidence_created"] is False
    assert summary["rehearsal_authorizes_live_access"] is False
    assert summary["rehearsal_authorizes_execution"] is False
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True

    expected_steps = {
        "phase1_mounted_stack_tcp_contact_measurement": "tcp_contact_measurements.csv",
        "phase2_ksm_contact_patch_convention": "ksm_contact_patch_convention.csv",
        "phase3_plane_normal_external_measurement": "plane_normal_measurements.csv",
        "phase4_force_source_read_only_comparison": "force_source_comparison.csv",
        "phase5_orientation_gate_semantics_evidence": "orientation_gate_semantics.csv",
    }
    rows = {row["step_id"]: row for row in payload["rehearsal_rows"]}
    assert rows.keys() == expected_steps.keys()
    for step_id, worksheet in expected_steps.items():
        row = rows[step_id]
        assert row["worksheet"] == worksheet
        assert row["finalize_returncode"] == 0
        assert row["audit_returncode"] == 0
        assert row["rehearsal_passed"] is True
        assert row["scope_preserved"] is True
        assert row["evidence_changed_only_for_step"] is True
        assert row["claim_boundary_preserved"] is True
        assert row["status_after_rehearsal"] == "approved_read_only_evidence"
        assert row["audit_mode"] == "approved-read-only"
        assert row["audit_passed"] is True
        assert row["audit_violations"] == []
        assert row["live_hardware_accessed_after_rehearsal"] is False
        assert row["worksheet_row_counts"][worksheet] == 1
        assert row["allowed_worksheets"] == [worksheet]
        assert not pathlib.Path(row["temporary_run_dir"]).exists()
        assert not pathlib.Path(row["temporary_audit_dir"]).exists()

    assert payload["repository_state_before"] == payload["repository_state_after"]
    boundary = payload["claim_boundary"]
    assert boundary["temporary_rehearsal_only"] is True
    assert boundary["synthetic_rows_only"] is True
    assert boundary["approved_read_only_evidence_created_in_repository"] is False
    assert boundary["live_hardware_access_authorized"] is False
    assert boundary["execution_authorized"] is False
    assert boundary["do_not_mark_goal_complete"] is True


def test_finalization_rehearsal_boundary_rejects_source_guard_drift(tmp_path) -> None:
    source = yaml.safe_load(DOWNSTREAM_GUARD.read_text(encoding="utf-8"))
    source["summary"]["downstream_row_quality_guard_complete"] = False
    source["summary"]["approved_read_only_evidence_created"] = True
    drifted = tmp_path / "downstream_guard.yaml"
    drifted.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(downstream_guard_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["finalization_rehearsal_boundary_complete"] is False
    assert "v134 source summary downstream_row_quality_guard_complete is False, expected True" in payload[
        "summary"
    ]["violations"]
    assert "v134 source summary approved_read_only_evidence_created is True, expected False" in payload[
        "summary"
    ]["violations"]


def test_finalization_rehearsal_boundary_rejects_registry_scope_drift(tmp_path) -> None:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    registry["steps"][2]["allowed_worksheets"] = ["tcp_contact_measurements.csv"]
    drifted = tmp_path / "registry.yaml"
    drifted.write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(registry_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["finalization_rehearsal_boundary_complete"] is False
    assert "registered step 'phase2_ksm_contact_patch_convention' worksheet does not match rehearsal row" in payload[
        "summary"
    ]["violations"]


def test_finalization_rehearsal_boundary_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "finalization_rehearsal_boundary"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_finalization_rehearsal_boundary.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_FINALIZATION_REHEARSAL",
        ],
        cwd=ROOT,
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
    assert metrics["summary"]["audit_passed"] is True
    assert metrics["summary"]["rehearsal_passed_step_count"] == 5
    assert metrics["summary"]["repository_approved_read_only_run_delta"] == 0
    assert metrics["summary"]["approved_read_only_evidence_created"] is False
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
