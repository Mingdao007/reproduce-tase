from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_post_v142_completion_gate import build_payload


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
        "v142_frontier_path": ROOT
        / "runs"
        / "robustness_dependency_frontier_after_v141"
        / "20260525T160000"
        / "metrics.yaml",
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_post_v142_completion_gate_keeps_frontier_non_evidence() -> None:
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
    assert summary["readiness_artifact_count"] == 7
    assert summary["readiness_completion_evidence_ids"] == []
    assert summary["readiness_artifacts_are_non_evidence"] is True
    assert summary["status_answer_is_non_evidence"] is True
    assert summary["continuation_boundary_is_non_evidence"] is True
    assert summary["robustness_frontier_is_non_evidence"] is True
    assert summary["v142_robustness_complete"] is False
    assert summary["v142_accepted_as_robustness_proof"] is False
    assert summary["v142_closed_cell_count"] == 0
    assert summary["v142_frontier_row_count"] == 4
    assert summary["v142_profile_overlay_supported_noncanonical_cell_ids"] == [
        "base_z_plus1mm",
        "positive_fast_timing_0p0075",
    ]
    assert summary["v142_gate_or_contact_acceptance_blocked_cell_ids"] == [
        "positive_orientation_gate_0p119",
        "weighted_plus1mm_0p119_gate",
    ]
    assert summary["v142_new_simulation_selected"] is False
    assert summary["v142_additional_failed_cell_execution_recommended"] is False

    readiness = {row["readiness_id"]: row for row in payload["readiness_artifacts"]}
    frontier = readiness["robustness_dependency_frontier_after_v141"]
    assert frontier["completion_evidence"] is False
    assert frontier["status"] == "robustness_frontier_classified_not_evidence"
    assert payload["claim_boundary"]["robustness_frontier_is_not_evidence"] is True
    assert payload["claim_boundary"]["failed_robustness_cells_closed"] is False
    assert payload["claim_boundary"]["robustness_claim"] is False
    assert payload["claim_boundary"]["live_hardware_access_authorized"] is False
    assert payload["claim_boundary"]["execution_authorized"] is False


def test_post_v142_completion_gate_rejects_frontier_robustness_drift(tmp_path) -> None:
    frontier = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "robustness_dependency_frontier_after_v141"
            / "20260525T160000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    frontier["summary"]["robustness_complete"] = True
    frontier["summary"]["accepted_as_robustness_proof"] = True
    frontier["summary"]["closed_cell_count"] = 1
    frontier["frontier_rows"][0]["failed_cell_closed"] = True
    frontier["claim_boundary"]["robustness_proof"] = True
    drifted = tmp_path / "v142_frontier.yaml"
    drifted.write_text(yaml.safe_dump(frontier, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(v142_frontier_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["readiness_completion_evidence_ids"] == [
        "robustness_dependency_frontier_after_v141"
    ]
    violations = payload["summary"]["violations"]
    assert "robustness_dependency_frontier_after_v141 drifted into completion evidence" in violations
    assert (
        "robustness_dependency_frontier_after_v141.evidence.accepted_as_robustness_proof is True, expected False"
        in violations
    )
    assert "base_z_plus1mm unexpectedly closed in robustness frontier" in violations


def test_post_v142_completion_gate_rejects_frontier_execution_drift(tmp_path) -> None:
    frontier = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "robustness_dependency_frontier_after_v141"
            / "20260525T160000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    frontier["summary"]["new_simulation_selected"] = True
    frontier["summary"]["additional_failed_cell_execution_recommended"] = True
    frontier["claim_boundary"]["execution_authorized"] = True
    frontier["claim_boundary"]["live_hardware_access_authorized"] = True
    drifted = tmp_path / "v142_frontier_execution.yaml"
    drifted.write_text(yaml.safe_dump(frontier, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(v142_frontier_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["readiness_completion_evidence_ids"] == [
        "robustness_dependency_frontier_after_v141"
    ]
    violations = payload["summary"]["violations"]
    assert (
        "robustness_dependency_frontier_after_v141.evidence.new_simulation_selected is True, expected False"
        in violations
    )
    assert (
        "robustness_dependency_frontier_after_v141.claim_boundary.execution_authorized is True, expected False"
        in violations
    )


def test_post_v142_completion_gate_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "post_v142_completion_gate"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_post_v142_completion_gate.py",
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
    assert metrics["summary"]["robustness_frontier_is_non_evidence"] is True
    assert metrics["summary"]["readiness_artifact_count"] == 7
    assert metrics["summary"]["readiness_completion_evidence_ids"] == []
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
