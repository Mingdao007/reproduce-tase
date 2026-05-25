from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_post_v140_completion_gate import build_payload


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
        "margin_separation_path": ROOT
        / "runs"
        / "strict_vs_diagnostic_margin_separation"
        / "20260525T124000"
        / "metrics.yaml",
        "v139_status_path": ROOT
        / "runs"
        / "full_reproduction_status_after_v138"
        / "20260525T130000"
        / "metrics.yaml",
        "v140_continuation_path": ROOT
        / "runs"
        / "post_v139_continuation_boundary"
        / "20260525T140000"
        / "metrics.yaml",
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_post_v140_completion_gate_keeps_status_and_continuation_non_evidence() -> None:
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
    assert summary["readiness_artifact_count"] == 6
    assert summary["readiness_completion_evidence_ids"] == []
    assert summary["readiness_artifacts_are_non_evidence"] is True
    assert summary["finalization_rehearsal_is_non_evidence"] is True
    assert summary["margin_separation_is_non_evidence"] is True
    assert summary["status_answer_is_non_evidence"] is True
    assert summary["continuation_boundary_is_non_evidence"] is True
    assert summary["v139_user_question_answer"] == "not_fully_reproduced"
    assert summary["v139_full_reproduction_complete"] is False
    assert summary["v139_continue_required"] is True
    assert summary["v140_freeform_continue_is_approval"] is False
    assert summary["v140_read_only_sop_can_execute_now"] is False
    assert summary["v140_live_access_authorized_now"] is False
    assert summary["v140_execution_authorized_now"] is False
    assert summary["v140_repeat_strict_family_recommended"] is False

    readiness = {row["readiness_id"]: row for row in payload["readiness_artifacts"]}
    assert readiness["full_reproduction_status_after_v138"]["completion_evidence"] is False
    assert readiness["full_reproduction_status_after_v138"]["status"] == (
        "status_answer_not_complete_not_evidence"
    )
    assert readiness["post_v139_continuation_boundary"]["completion_evidence"] is False
    assert readiness["post_v139_continuation_boundary"]["status"] == (
        "freeform_continuation_guarded_not_evidence"
    )
    assert payload["claim_boundary"]["status_answer_is_not_evidence"] is True
    assert payload["claim_boundary"]["continuation_boundary_is_not_evidence"] is True
    assert payload["claim_boundary"]["live_hardware_access_authorized"] is False
    assert payload["claim_boundary"]["execution_authorized"] is False


def test_post_v140_completion_gate_rejects_v139_completion_drift(tmp_path) -> None:
    status = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "full_reproduction_status_after_v138"
            / "20260525T130000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    status["summary"]["full_reproduction_complete"] = True
    status["summary"]["user_question_answer"] = "complete"
    status["claim_boundary"]["full_reproduction_claim_allowed"] = True
    drifted = tmp_path / "v139_status.yaml"
    drifted.write_text(yaml.safe_dump(status, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(v139_status_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["readiness_completion_evidence_ids"] == [
        "full_reproduction_status_after_v138"
    ]
    assert "full_reproduction_status_after_v138 drifted into completion evidence" in payload[
        "summary"
    ]["violations"]
    assert (
        "full_reproduction_status_after_v138.evidence.user_question_answer is 'complete', expected 'not_fully_reproduced'"
        in payload["summary"]["violations"]
    )


def test_post_v140_completion_gate_rejects_continuation_authorization_drift(tmp_path) -> None:
    continuation = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "post_v139_continuation_boundary"
            / "20260525T140000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    continuation["summary"]["freeform_continue_is_approval"] = True
    continuation["summary"]["read_only_sop_can_execute_now"] = True
    continuation["claim_boundary"]["execution_authorized"] = True
    drifted = tmp_path / "v140_continuation.yaml"
    drifted.write_text(yaml.safe_dump(continuation, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(v140_continuation_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["readiness_completion_evidence_ids"] == [
        "post_v139_continuation_boundary"
    ]
    assert "post_v139_continuation_boundary drifted into completion evidence" in payload[
        "summary"
    ]["violations"]
    assert (
        "post_v139_continuation_boundary.evidence.freeform_continue_is_approval is True, expected False"
        in payload["summary"]["violations"]
    )
    assert (
        "post_v139_continuation_boundary.claim_boundary.execution_authorized is True, expected False"
        in payload["summary"]["violations"]
    )


def test_post_v140_completion_gate_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "post_v140_completion_gate"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_post_v140_completion_gate.py",
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
    assert metrics["summary"]["status_answer_is_non_evidence"] is True
    assert metrics["summary"]["continuation_boundary_is_non_evidence"] is True
    assert metrics["summary"]["readiness_artifacts_are_non_evidence"] is True
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
