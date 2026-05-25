from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_post_v117_evidence_readiness import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_build_payload_marks_post_v117_goal_incomplete() -> None:
    payload = build_payload(
        completion_blockers_path=ROOT
        / "runs"
        / "offline_completion_blockers"
        / "20260525T020734"
        / "metrics.yaml",
        strict_terminal_path=ROOT
        / "runs"
        / "strict_terminal_constrained_optimization"
        / "20260525T085000"
        / "metrics.yaml",
        matrix_restatement_path=ROOT
        / "runs"
        / "weighted_profile_matrix_restatement"
        / "20260525T075040"
        / "metrics.yaml",
        read_only_run_root=ROOT / "runs" / "read_only_calibration_measurement",
        read_only_audit_root=ROOT / "runs" / "read_only_calibration_measurement_run_audit",
        orientation_review_root=ROOT / "runs" / "orientation_gate_acceptance_review",
        orientation_audit_root=ROOT / "runs" / "orientation_gate_acceptance_review_audit",
        contact_review_root=ROOT / "runs" / "contact_setup_target_acceptance_review",
        contact_audit_root=ROOT / "runs" / "contact_setup_target_acceptance_review_audit",
        run_id="TEST",
    )

    summary = payload["summary"]
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

    checklist = {row["requirement_id"]: row for row in payload["completion_checklist"]}
    assert checklist["approved_read_only_calibration_evidence"]["achieved"] is False
    assert checklist["approved_read_only_calibration_evidence"]["requires_explicit_approval"] is True
    assert checklist["contact_setup_target_acceptance"]["achieved"] is False
    assert checklist["orientation_gate_acceptance"]["achieved"] is False
    assert checklist["strict_terminal_or_full_staged_feasibility"]["can_advance_offline"] is True
    assert checklist["robustness_to_contact_model_perturbations"]["can_advance_offline"] is True
    assert checklist["hardware_readiness"]["requires_explicit_approval"] is True

    assert payload["claim_boundary"]["robot_motion_authorized"] is False
    assert payload["claim_boundary"]["hardware_writes_authorized"] is False
    assert payload["claim_boundary"]["force_control_authorized"] is False
    assert payload["claim_boundary"]["do_not_mark_goal_complete"] is True


def test_post_v117_audit_includes_v117_contact_review_scan() -> None:
    payload = build_payload(
        completion_blockers_path=ROOT
        / "runs"
        / "offline_completion_blockers"
        / "20260525T020734"
        / "metrics.yaml",
        strict_terminal_path=ROOT
        / "runs"
        / "strict_terminal_constrained_optimization"
        / "20260525T085000"
        / "metrics.yaml",
        matrix_restatement_path=ROOT
        / "runs"
        / "weighted_profile_matrix_restatement"
        / "20260525T075040"
        / "metrics.yaml",
        read_only_run_root=ROOT / "runs" / "read_only_calibration_measurement",
        read_only_audit_root=ROOT / "runs" / "read_only_calibration_measurement_run_audit",
        orientation_review_root=ROOT / "runs" / "orientation_gate_acceptance_review",
        orientation_audit_root=ROOT / "runs" / "orientation_gate_acceptance_review_audit",
        contact_review_root=ROOT / "runs" / "contact_setup_target_acceptance_review",
        contact_audit_root=ROOT / "runs" / "contact_setup_target_acceptance_review_audit",
        run_id="TEST",
    )

    contact = {
        row["requirement_id"]: row for row in payload["completion_checklist"]
    }["contact_setup_target_acceptance"]
    evidence = contact["evidence"]
    assert evidence["review_count"] >= 1
    assert evidence["audit_count"] >= 1
    assert evidence["latest_audit_passed"] is True
    assert evidence["latest_decision"] == "not_accepted"
    assert evidence["accepted_review_count"] == 0
    assert evidence["accepted_audit_count"] == 0


def test_post_v117_audit_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "post_v117_evidence_readiness"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_post_v117_evidence_readiness.py",
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
    assert metrics["summary"]["overall_goal_complete"] is False
    assert metrics["summary"]["approved_read_only_run_count"] == 0
    assert metrics["summary"]["accepted_contact_setup_target_review_count"] == 0
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
