from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_post_v122_completion_gate import build_payload


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
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_post_v122_completion_gate_keeps_goal_incomplete() -> None:
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
    assert summary["readiness_artifact_count"] == 2
    assert summary["readiness_artifacts_are_non_evidence"] is True
    assert summary["readiness_completion_evidence_ids"] == []

    readiness = {row["readiness_id"]: row for row in payload["readiness_artifacts"]}
    assert readiness["not_approved_packet_coverage"]["completion_evidence"] is False
    assert readiness["execution_preflight"]["completion_evidence"] is False
    assert readiness["not_approved_packet_coverage"]["evidence"]["covered_step_count"] == 5
    assert readiness["execution_preflight"]["evidence"]["preflight_ready_step_count"] == 5

    checklist = {row["requirement_id"]: row for row in payload["completion_checklist"]}
    assert checklist["approved_read_only_calibration_evidence"]["achieved"] is False
    assert checklist["hardware_readiness"]["achieved"] is False
    assert payload["claim_boundary"]["readiness_artifacts_do_not_complete_goal"] is True
    assert payload["claim_boundary"]["do_not_mark_goal_complete"] is True


def test_post_v122_completion_gate_rejects_preflight_execution_drift(tmp_path) -> None:
    preflight = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "read_only_step_execution_preflight"
            / "20260525T101000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    preflight["summary"]["preflight_authorizes_execution"] = True
    preflight["claim_boundary"]["execution_authorized"] = True
    drifted_preflight = tmp_path / "preflight.yaml"
    drifted_preflight.write_text(yaml.safe_dump(preflight, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(execution_preflight_path=drifted_preflight)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["completion_claim_allowed"] is False
    assert payload["summary"]["readiness_completion_evidence_ids"] == ["execution_preflight"]
    assert "execution_preflight drifted into completion evidence" in payload["summary"]["violations"]
    assert "execution_preflight.claim_boundary.execution_authorized is not false" in payload[
        "summary"
    ]["violations"]


def test_post_v122_completion_gate_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "post_v122_completion_gate"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_post_v122_completion_gate.py",
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
    assert metrics["summary"]["readiness_artifacts_are_non_evidence"] is True
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
