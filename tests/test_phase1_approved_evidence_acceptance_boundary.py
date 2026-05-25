from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_phase1_approved_evidence_acceptance_boundary import (
    APPROVAL_PHRASE,
    EXPECTED_STEP_ID,
    EXPECTED_WORKSHEET,
    build_payload,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]


def build_current_payload(**overrides):
    kwargs = {
        "dependency_map_path": ROOT
        / "runs"
        / "read_only_evidence_dependency_map"
        / "20260525T110000"
        / "metrics.yaml",
        "next_step_selection_path": ROOT
        / "runs"
        / "read_only_next_step_selection"
        / "20260525T111000"
        / "metrics.yaml",
        "approval_freeze_path": ROOT
        / "runs"
        / "read_only_phase1_approval_request_freeze"
        / "20260525T112000"
        / "metrics.yaml",
        "finalizer_guard_path": ROOT
        / "runs"
        / "read_only_phase1_preapproval_finalizer_guard"
        / "20260525T113000"
        / "metrics.yaml",
        "post_v122_completion_gate_path": ROOT
        / "runs"
        / "post_v122_completion_gate"
        / "20260525T102000"
        / "metrics.yaml",
        "read_only_run_root": ROOT / "runs" / "read_only_calibration_measurement",
        "read_only_audit_root": ROOT / "runs" / "read_only_calibration_measurement_run_audit",
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_current_phase1_acceptance_boundary_has_no_approved_evidence() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["phase1_acceptance_boundary_complete"] is True
    assert summary["source_artifact_count"] == 5
    assert summary["boundary_row_count"] == 6
    assert summary["completion_evidence_ids"] == []
    assert summary["readiness_artifacts_are_non_evidence"] is True
    assert summary["current_repository_scan_finds_no_approved_evidence"] is True
    assert summary["read_only_run_count"] == 3
    assert summary["read_only_audit_count"] == 4
    assert summary["approved_read_only_run_count"] == 0
    assert summary["phase1_approved_read_only_run_count"] == 0
    assert summary["read_only_evidence_finalization_present_count"] == 0
    assert summary["approved_read_only_audit_passed_count"] == 0
    assert summary["phase1_approved_read_only_audit_passed_count"] == 0
    assert summary["selected_phase1_step_id"] == EXPECTED_STEP_ID
    assert summary["selected_phase1_worksheet"] == EXPECTED_WORKSHEET
    assert summary["approval_phrase_required"] == APPROVAL_PHRASE
    assert summary["guard_rejected_case_count"] == 5
    assert summary["guard_approved_evidence_created_count"] == 0
    assert summary["approved_read_only_evidence_created"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["overall_goal_complete"] is False
    assert summary["do_not_mark_goal_complete"] is True

    boundary = payload["claim_boundary"]
    assert boundary["phase1_acceptance_boundary_only"] is True
    assert boundary["approved_read_only_evidence"] is False
    assert boundary["live_hardware_access_authorized"] is False
    assert boundary["execution_authorized"] is False
    assert boundary["do_not_mark_goal_complete"] is True


def test_phase1_acceptance_boundary_rejects_synthetic_approved_phase1_run(tmp_path) -> None:
    run_root = tmp_path / "runs"
    approved_run = run_root / "APPROVED_PHASE1"
    approved_run.mkdir(parents=True)
    scaffold = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "read_only_calibration_measurement"
            / "20260525T012234"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    scaffold["status"] = "approved_read_only_evidence"
    scaffold["execution"]["user_confirmed_read_only_step"] = True
    scaffold["read_only_evidence_finalization"] = {
        "confirmation_phrase_matched": True,
        "approved_step_id": EXPECTED_STEP_ID,
        "approved_step_title": "Mounted stack TCP/contact point read-only measurement",
        "approved_step_registry": "configs/read_only_sop_step_registry.yaml",
        "allowed_worksheets": [EXPECTED_WORKSHEET],
        "operator": "test_operator",
        "finalized_at_utc": "2026-05-25T12:00:00Z",
        "live_hardware_accessed_declared": False,
        "worksheet_row_counts": {EXPECTED_WORKSHEET: 1},
    }
    (approved_run / "metrics.yaml").write_text(
        yaml.safe_dump(scaffold, sort_keys=False),
        encoding="utf-8",
    )

    payload = build_current_payload(
        read_only_run_root=run_root,
        read_only_audit_root=tmp_path / "audits",
    )

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["phase1_approved_read_only_run_count"] == 1
    assert payload["summary"]["read_only_evidence_finalization_present_count"] == 1
    assert payload["summary"]["completion_evidence_ids"] == [
        "current_repository_read_only_evidence_scan"
    ]
    assert "current read-only run scan found approved read-only evidence" in payload[
        "summary"
    ]["violations"]
    assert "current read-only run scan found phase1 approved evidence" in payload["summary"][
        "violations"
    ]
    assert "current read-only run scan found finalization metadata" in payload["summary"][
        "violations"
    ]


def test_phase1_acceptance_boundary_rejects_guard_evidence_drift(tmp_path) -> None:
    guard = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "read_only_phase1_preapproval_finalizer_guard"
            / "20260525T113000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    guard["summary"]["approved_read_only_evidence_created_count"] = 1
    guard["summary"]["repository_evidence_run_created"] = True
    drifted_guard = tmp_path / "guard.yaml"
    drifted_guard.write_text(yaml.safe_dump(guard, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(finalizer_guard_path=drifted_guard)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["guard_approved_evidence_created_count"] == 1
    assert "v130.summary.approved_read_only_evidence_created_count is 1, expected 0" in payload[
        "summary"
    ]["violations"]
    assert "v130.summary.repository_evidence_run_created is not false" in payload["summary"][
        "violations"
    ]


def test_phase1_acceptance_boundary_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "phase1_acceptance_boundary"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_phase1_approved_evidence_acceptance_boundary.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_PHASE1_BOUNDARY",
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
    assert metrics["summary"]["current_repository_scan_finds_no_approved_evidence"] is True
    assert metrics["summary"]["phase1_approved_read_only_run_count"] == 0
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
