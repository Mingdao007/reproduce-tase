from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_post_v135_completion_gate import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]


def build_current_payload(**overrides):
    kwargs = {
        "completion_blockers_path": ROOT
        / "runs"
        / "offline_completion_blockers"
        / "20260525T020734"
        / "metrics.yaml",
        "strict_terminal_path": ROOT
        / "runs"
        / "strict_terminal_constrained_optimization"
        / "20260525T085000"
        / "metrics.yaml",
        "matrix_restatement_path": ROOT
        / "runs"
        / "weighted_profile_matrix_restatement"
        / "20260525T075040"
        / "metrics.yaml",
        "read_only_run_root": ROOT / "runs" / "read_only_calibration_measurement",
        "read_only_audit_root": ROOT / "runs" / "read_only_calibration_measurement_run_audit",
        "orientation_review_root": ROOT / "runs" / "orientation_gate_acceptance_review",
        "orientation_audit_root": ROOT / "runs" / "orientation_gate_acceptance_review_audit",
        "contact_review_root": ROOT / "runs" / "contact_setup_target_acceptance_review",
        "contact_audit_root": ROOT / "runs" / "contact_setup_target_acceptance_review_audit",
        "packet_coverage_path": ROOT
        / "runs"
        / "read_only_step_approval_packet_coverage"
        / "20260525T100500"
        / "metrics.yaml",
        "execution_preflight_path": ROOT
        / "runs"
        / "read_only_step_execution_preflight"
        / "20260525T101000"
        / "metrics.yaml",
        "finalization_rehearsal_path": ROOT
        / "runs"
        / "read_only_finalization_rehearsal_boundary"
        / "20260525T122000"
        / "metrics.yaml",
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_post_v135_completion_gate_keeps_rehearsal_non_evidence() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True
    assert summary["top_blocker"] == "approved_read_only_calibration_evidence"
    assert summary["approved_read_only_run_count"] == 0
    assert summary["approved_read_only_audit_passed_count"] == 0
    assert summary["accepted_orientation_review_count"] == 0
    assert summary["accepted_contact_setup_target_review_count"] == 0
    assert summary["strict_terminal_pass_count"] == 0
    assert summary["closed_robustness_cell_count"] == 0
    assert summary["hardware_gate_report_exists"] is False
    assert summary["readiness_artifact_count"] == 3
    assert summary["readiness_artifacts_are_non_evidence"] is True
    assert summary["readiness_completion_evidence_ids"] == []
    assert summary["finalization_rehearsal_is_non_evidence"] is True
    assert summary["rehearsal_temporary_finalization_count"] == 5
    assert summary["rehearsal_approved_read_only_verifier_passed_count"] == 5
    assert summary["rehearsal_temporary_path_existing_count"] == 0
    assert summary["rehearsal_repository_approved_read_only_run_delta"] == 0
    assert summary["rehearsal_repository_finalization_record_delta"] == 0
    assert summary["rehearsal_repository_approved_read_only_audit_delta"] == 0

    readiness = {row["readiness_id"]: row for row in payload["readiness_artifacts"]}
    assert readiness["not_approved_packet_coverage"]["completion_evidence"] is False
    assert readiness["execution_preflight"]["completion_evidence"] is False
    rehearsal = readiness["finalization_rehearsal_boundary"]
    assert rehearsal["completion_evidence"] is False
    assert rehearsal["status"] == "temporary_rehearsal_not_evidence"
    assert rehearsal["evidence"]["temporary_finalization_count"] == 5
    assert rehearsal["evidence"]["temporary_path_existing_count"] == 0

    checklist = {row["requirement_id"]: row for row in payload["completion_checklist"]}
    assert checklist["approved_read_only_calibration_evidence"]["achieved"] is False
    assert checklist["hardware_readiness"]["achieved"] is False
    assert payload["claim_boundary"]["finalization_rehearsal_is_not_evidence"] is True
    assert payload["claim_boundary"]["do_not_mark_goal_complete"] is True


def test_post_v135_completion_gate_rejects_rehearsal_evidence_drift(tmp_path) -> None:
    rehearsal = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "read_only_finalization_rehearsal_boundary"
            / "20260525T122000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    rehearsal["summary"]["approved_read_only_evidence_created"] = True
    rehearsal["summary"]["repository_approved_read_only_run_delta"] = 1
    rehearsal["claim_boundary"]["approved_read_only_evidence"] = True
    drifted = tmp_path / "rehearsal.yaml"
    drifted.write_text(yaml.safe_dump(rehearsal, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(finalization_rehearsal_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["completion_claim_allowed"] is False
    assert payload["summary"]["readiness_completion_evidence_ids"] == [
        "finalization_rehearsal_boundary"
    ]
    assert "finalization_rehearsal_boundary drifted into completion evidence" in payload[
        "summary"
    ]["violations"]
    assert (
        "finalization_rehearsal_boundary.claim_boundary.approved_read_only_evidence is not false"
        in payload["summary"]["violations"]
    )
    assert (
        "finalization_rehearsal_boundary.evidence.repository_approved_read_only_run_delta is 1, expected 0"
        in payload["summary"]["violations"]
    )


def test_post_v135_completion_gate_rejects_persistent_temporary_paths(tmp_path) -> None:
    rehearsal = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "read_only_finalization_rehearsal_boundary"
            / "20260525T122000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    persistent_run = tmp_path / "still_present_run"
    persistent_run.mkdir()
    rehearsal["rehearsal_rows"][0]["temporary_run_dir"] = str(persistent_run)
    drifted = tmp_path / "rehearsal.yaml"
    drifted.write_text(yaml.safe_dump(rehearsal, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(finalization_rehearsal_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["rehearsal_temporary_path_existing_count"] == 1
    assert (
        "finalization_rehearsal_boundary.evidence.temporary_path_existing_count is 1, expected 0"
        in payload["summary"]["violations"]
    )


def test_post_v135_completion_gate_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "post_v135_completion_gate"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_post_v135_completion_gate.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_RUN",
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
    assert metrics["summary"]["overall_goal_complete"] is False
    assert metrics["summary"]["finalization_rehearsal_is_non_evidence"] is True
    assert metrics["summary"]["readiness_artifacts_are_non_evidence"] is True
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
