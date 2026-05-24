from __future__ import annotations

import pathlib

from scripts.audit_weighted_profile_matrix_restatement import (
    build_payload,
    restate_failed_cell,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_restate_failed_cell_applies_profile_overlay_without_closure() -> None:
    row = restate_failed_cell(
        cell={
            "id": "positive_fast_timing_0p0075",
            "status": "failed",
            "blocker_ids": ["faster_timing_qdot_tail_utilization"],
        },
        profile_summary={
            "diagnostic_profile_naming_supported": True,
            "covered_faces": ["positive_fast_timing_full_e1e4"],
        },
        planned_ids={"positive_fast_timing_0p0075"},
        executed_ids={"positive_fast_timing_0p0075"},
        unresolved_ids={"positive_fast_timing_0p0075"},
    )

    assert row["profile_overlay_supported"] is True
    assert row["profile_overlay_face"] == "positive_fast_timing_full_e1e4"
    assert row["restated_status"] == "failed_with_noncanonical_profile_overlay"
    assert row["failed_cell_closed"] is False
    assert row["canonical_controller_change"] is False
    assert row["canonical_orientation_gate_change"] is False
    assert row["robustness_claim"] is False


def test_restate_failed_cell_keeps_gate_rows_uncovered() -> None:
    row = restate_failed_cell(
        cell={
            "id": "positive_orientation_gate_0p119",
            "status": "failed",
            "blocker_ids": ["tightened_orientation_gate_plus1mm"],
        },
        profile_summary={
            "diagnostic_profile_naming_supported": True,
            "covered_faces": ["positive_fast_timing_full_e1e4"],
        },
        planned_ids={"positive_orientation_gate_0p119"},
        executed_ids={"positive_orientation_gate_0p119"},
        unresolved_ids={"positive_orientation_gate_0p119"},
    )

    assert row["profile_overlay_supported"] is False
    assert row["profile_overlay_face"] is None
    assert row["restated_status"] == "failed_without_profile_overlay"
    assert row["failed_cell_closed"] is False


def test_build_payload_restates_v98_v99_matrix_without_robustness_claim() -> None:
    payload = build_payload(
        v98_matrix_path=ROOT
        / "runs"
        / "diagnostic_robustness_matrix_candidate"
        / "20260525T053101"
        / "metrics.yaml",
        v99_plan_path=ROOT
        / "runs"
        / "failed_diagnostic_robustness_experiment_matrix"
        / "20260525T053909"
        / "metrics.yaml",
        execution_audit_path=ROOT
        / "runs"
        / "failed_diagnostic_robustness_experiment_audit"
        / "20260525T061328"
        / "metrics.yaml",
        profile_boundary_path=ROOT
        / "runs"
        / "weighted_priority_profile_boundary"
        / "20260525T074100"
        / "metrics.yaml",
    )

    summary = payload["summary"]
    assert summary["profile_name"] == "weighted_zero_angular_stage_b_diagnostic"
    assert summary["restatement_supported"] is True
    assert summary["source_cell_count"] == 12
    assert summary["source_failed_cell_count"] == 4
    assert summary["profile_overlay_supported_count"] == 2
    assert summary["profile_overlay_supported_cell_ids"] == [
        "base_z_plus1mm",
        "positive_fast_timing_0p0075",
    ]
    assert summary["closed_cell_count"] == 0
    assert summary["candidate_matrix_complete"] is False
    assert summary["accepted_as_robustness_proof"] is False
    assert summary["all_failed_cells_closed"] is False
    assert summary["canonical_controller_change"] is False
    assert summary["canonical_orientation_gate_change"] is False
    assert summary["robustness_claim"] is False
    assert summary["do_not_mark_goal_complete"] is True
    assert payload["claim_boundary"]["can_restate_matrix_with_named_profile"] is True
    assert payload["claim_boundary"]["hardware_readiness"] is False
