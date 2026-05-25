from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_post_v137_completion_gate import build_payload


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
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_post_v137_completion_gate_keeps_margin_separation_non_evidence() -> None:
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
    assert summary["readiness_artifact_count"] == 4
    assert summary["readiness_artifacts_are_non_evidence"] is True
    assert summary["readiness_completion_evidence_ids"] == []
    assert summary["finalization_rehearsal_is_non_evidence"] is True
    assert summary["margin_separation_is_non_evidence"] is True
    assert summary["margin_strict_to_diagnostic_orientation_ratio"] == 59.31389790209757
    assert summary["margin_v85_can_close_strict_paper_equivalent_goal"] is False
    assert summary["margin_replacement_gate_accepted"] is False
    assert summary["margin_minimum_uniform_requires_all_three_scalar_gates"] is True

    readiness = {row["readiness_id"]: row for row in payload["readiness_artifacts"]}
    assert readiness["not_approved_packet_coverage"]["completion_evidence"] is False
    assert readiness["execution_preflight"]["completion_evidence"] is False
    assert readiness["finalization_rehearsal_boundary"]["completion_evidence"] is False
    margin = readiness["strict_vs_diagnostic_margin_separation"]
    assert margin["completion_evidence"] is False
    assert margin["status"] == "diagnostic_margin_separated_not_evidence"
    assert margin["evidence"]["v85_margin_can_close_strict_orientation"] is False
    assert margin["claim_boundary"]["diagnostic_margin_only"] is True

    checklist = {row["requirement_id"]: row for row in payload["completion_checklist"]}
    assert checklist["approved_read_only_calibration_evidence"]["achieved"] is False
    assert checklist["hardware_readiness"]["achieved"] is False
    assert payload["claim_boundary"]["margin_separation_is_not_evidence"] is True
    assert payload["claim_boundary"]["do_not_mark_goal_complete"] is True


def test_post_v137_completion_gate_rejects_margin_completion_drift(tmp_path) -> None:
    margin = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "strict_vs_diagnostic_margin_separation"
            / "20260525T124000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    margin["summary"]["replacement_gate_accepted"] = True
    margin["summary"]["completion_claim_allowed"] = True
    margin["claim_boundary"]["canonical_orientation_gate_change"] = True
    drifted = tmp_path / "margin.yaml"
    drifted.write_text(yaml.safe_dump(margin, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(margin_separation_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["completion_claim_allowed"] is False
    assert payload["summary"]["readiness_completion_evidence_ids"] == [
        "strict_vs_diagnostic_margin_separation"
    ]
    assert "strict_vs_diagnostic_margin_separation drifted into completion evidence" in payload[
        "summary"
    ]["violations"]
    assert (
        "strict_vs_diagnostic_margin_separation.evidence.replacement_gate_accepted is True, expected False"
        in payload["summary"]["violations"]
    )
    assert (
        "strict_vs_diagnostic_margin_separation.claim_boundary.canonical_orientation_gate_change is True, expected False"
        in payload["summary"]["violations"]
    )


def test_post_v137_completion_gate_rejects_ratio_collapse(tmp_path) -> None:
    margin = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "strict_vs_diagnostic_margin_separation"
            / "20260525T124000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    margin["summary"]["strict_to_diagnostic_orientation_margin_ratio"] = 1.0
    drifted = tmp_path / "margin.yaml"
    drifted.write_text(yaml.safe_dump(margin, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(margin_separation_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert any(
        "strict_to_diagnostic_orientation_margin_ratio is 1.0" in violation
        for violation in payload["summary"]["violations"]
    )


def test_post_v137_completion_gate_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "post_v137_completion_gate"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_post_v137_completion_gate.py",
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
    assert metrics["summary"]["margin_separation_is_non_evidence"] is True
    assert metrics["summary"]["readiness_artifacts_are_non_evidence"] is True
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
