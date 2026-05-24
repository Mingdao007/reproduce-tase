from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_remaining_blocker_prioritization import (
    build_payload,
    prioritize_blockers,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_prioritize_blockers_preserves_explicit_priority_order() -> None:
    rows = [
        {
            "blocker_id": "strict_paper_equivalent_full_staged_feasibility",
            "priority_rank": 3,
            "can_advance_offline": True,
            "requires_explicit_approval": False,
            "completion_claim_allowed": False,
        },
        {
            "blocker_id": "approved_read_only_calibration_evidence",
            "priority_rank": 0,
            "can_advance_offline": False,
            "requires_explicit_approval": True,
            "completion_claim_allowed": False,
        },
        {
            "blocker_id": "hardware_readiness",
            "priority_rank": 5,
            "can_advance_offline": False,
            "requires_explicit_approval": True,
            "completion_claim_allowed": False,
        },
    ]

    sorted_rows = prioritize_blockers(rows)

    assert [row["blocker_id"] for row in sorted_rows] == [
        "approved_read_only_calibration_evidence",
        "strict_paper_equivalent_full_staged_feasibility",
        "hardware_readiness",
    ]


def test_build_payload_prioritizes_real_remaining_blockers() -> None:
    payload = build_payload(
        completion_blockers_path=ROOT
        / "runs"
        / "offline_completion_blockers"
        / "20260525T020734"
        / "metrics.yaml",
        strict_blockers_path=ROOT
        / "runs"
        / "strict_feasibility_blockers"
        / "20260525T051640"
        / "metrics.yaml",
        robustness_blockers_path=ROOT
        / "runs"
        / "robustness_blockers"
        / "20260525T052457"
        / "metrics.yaml",
        matrix_restatement_path=ROOT
        / "runs"
        / "weighted_profile_matrix_restatement"
        / "20260525T075040"
        / "metrics.yaml",
        measured_geometry_path=ROOT
        / "runs"
        / "measured_geometry_readiness"
        / "20260525T000739"
        / "metrics.yaml",
        read_only_audit_path=ROOT
        / "runs"
        / "read_only_calibration_measurement_run_audit"
        / "20260525T015401"
        / "metrics.yaml",
        gate_review_audit_path=ROOT
        / "runs"
        / "orientation_gate_acceptance_review_audit"
        / "20260525T020055"
        / "metrics.yaml",
    )

    summary = payload["summary"]
    assert summary["overall_goal_complete"] is False
    assert summary["completion_blocked"] is True
    assert summary["do_not_mark_goal_complete"] is True
    assert summary["top_priority_blocker_id"] == "approved_read_only_calibration_evidence"
    assert summary["remaining_blocker_count"] == 6
    assert summary["live_or_approval_blocked_count"] == 4
    assert summary["offline_actionable_nonfinal_count"] == 2
    assert summary["profile_overlay_supported_cell_count"] == 2
    assert summary["profile_overlay_supported_cell_ids"] == [
        "base_z_plus1mm",
        "positive_fast_timing_0p0075",
    ]
    assert summary["gate_acceptance_blocked_cell_count"] == 2
    assert summary["gate_acceptance_blocked_cell_ids"] == [
        "positive_orientation_gate_0p119",
        "weighted_plus1mm_0p119_gate",
    ]
    assert summary["closed_cell_count"] == 0
    assert summary["candidate_matrix_complete"] is False
    assert summary["accepted_as_robustness_proof"] is False

    rows = {row["blocker_id"]: row for row in payload["blocker_rows"]}
    read_only = rows["approved_read_only_calibration_evidence"]
    assert read_only["priority_rank"] == 0
    assert read_only["category"] == "approval_blocked_prerequisite"
    assert read_only["can_advance_offline"] is False
    assert read_only["requires_explicit_approval"] is True
    assert read_only["evidence_summary"]["approved_read_only_run_count"] == 0

    strict = rows["strict_paper_equivalent_full_staged_feasibility"]["evidence_summary"]
    assert strict["strict_full_staged_feasibility_pass_count"] == 0
    assert strict["strict_full_staged_feasibility_case_count"] == 4
    assert strict["three_phase_setup_terminal_state_pass_count"] == 0
    assert strict["three_phase_setup_terminal_state_case_count"] == 10
    assert strict["three_phase_trajectory_feasibility_pass_count"] == 8
    assert strict["three_phase_trajectory_feasibility_case_count"] == 10
    assert strict["primary_blocker"] == "strict_setup_terminal_tradeoff"

    gate = rows["orientation_gate_acceptance"]
    assert gate["evidence_summary"]["decision"] == "not_accepted"
    assert gate["evidence_summary"]["accepted_review_count"] == 0
    assert gate["completion_claim_allowed"] is False

    assert payload["claim_boundary"]["strict_paper_equivalent_feasibility"] is False
    assert payload["claim_boundary"]["robustness_claim"] is False
    assert payload["claim_boundary"]["contact_calibration_claim"] is False
    assert payload["claim_boundary"]["hardware_readiness"] is False
    assert payload["claim_boundary"]["robot_motion_authorized"] is False


def test_audit_remaining_blocker_prioritization_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "remaining_blocker_prioritization"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_remaining_blocker_prioritization.py",
            "--output-dir",
            str(out_dir),
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
    assert metrics["summary"]["remaining_blocker_count"] == 6
    assert metrics["summary"]["completion_claim_allowed_count"] == 0
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
