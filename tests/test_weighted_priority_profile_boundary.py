from __future__ import annotations

import pathlib

from scripts.audit_weighted_priority_profile_boundary import (
    build_payload,
    evaluate_profile_boundary,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]


def _face(
    *,
    face_id: str,
    weighted_all_passed: bool = True,
    baseline_failing_count: int = 1,
    failed_cell_closed: bool = False,
) -> dict:
    return {
        "face_id": face_id,
        "base_z_offset_delta_mm": 1.0,
        "qdot_limit_rad_s": 0.15,
        "orientation_gate_rad": 0.12,
        "paper_time_scale": 0.01,
        "stage_a_durations_s": [15.0],
        "weighted_all_passed": weighted_all_passed,
        "baseline_failing_count": baseline_failing_count,
        "source_boundary_preserved": {
            "failed_cell_closed": failed_cell_closed,
            "canonical_controller_change": False,
            "canonical_orientation_gate_change": False,
            "robustness_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "hardware_readiness": False,
        },
    }


def test_profile_boundary_supports_diagnostic_name_only() -> None:
    boundary = evaluate_profile_boundary(
        [
            _face(face_id="positive_fast_timing_full_e1e4"),
            _face(face_id="relaxed_base_z_plus1mm_handoff"),
        ]
    )

    assert boundary["diagnostic_profile_naming_supported"] is True
    assert boundary["profile_name"] == "weighted_zero_angular_stage_b_diagnostic"
    assert boundary["weighted_all_faces_recovered"] is True
    assert boundary["baseline_failure_reproduced_all_faces"] is True
    assert boundary["claim_boundary"]["can_name_diagnostic_profile"] is True
    assert boundary["claim_boundary"]["canonical_controller_change"] is False
    assert boundary["claim_boundary"]["canonical_orientation_gate_change"] is False
    assert boundary["claim_boundary"]["failed_cell_closed"] is False
    assert boundary["claim_boundary"]["robustness_claim"] is False
    assert boundary["claim_boundary"]["hardware_readiness"] is False


def test_profile_boundary_rejects_missing_evidence_or_boundary_drift() -> None:
    missing_weighted = evaluate_profile_boundary(
        [
            _face(face_id="positive_fast_timing_full_e1e4", weighted_all_passed=False),
            _face(face_id="relaxed_base_z_plus1mm_handoff"),
        ]
    )
    assert missing_weighted["diagnostic_profile_naming_supported"] is False

    no_baseline_failure = evaluate_profile_boundary(
        [
            _face(face_id="positive_fast_timing_full_e1e4", baseline_failing_count=0),
            _face(face_id="relaxed_base_z_plus1mm_handoff"),
        ]
    )
    assert no_baseline_failure["diagnostic_profile_naming_supported"] is False

    boundary_drift = evaluate_profile_boundary(
        [
            _face(face_id="positive_fast_timing_full_e1e4", failed_cell_closed=True),
            _face(face_id="relaxed_base_z_plus1mm_handoff"),
        ]
    )
    assert boundary_drift["diagnostic_profile_naming_supported"] is False


def test_build_payload_uses_v107_and_v109_evidence_without_closing_cells() -> None:
    payload = build_payload(
        fast_metrics_path=ROOT
        / "runs"
        / "positive_fast_weighted_full_cell"
        / "20260525T064719"
        / "metrics.yaml",
        base_z_metrics_path=ROOT
        / "runs"
        / "relaxed_base_z_weighted_handoff"
        / "20260525T073012"
        / "metrics.yaml",
    )

    summary = payload["summary"]
    boundary = payload["profile_boundary"]
    assert summary["profile_name"] == "weighted_zero_angular_stage_b_diagnostic"
    assert summary["diagnostic_profile_naming_supported"] is True
    assert summary["evidence_face_count"] == 2
    assert summary["covered_faces"] == [
        "positive_fast_timing_full_e1e4",
        "relaxed_base_z_plus1mm_handoff",
    ]
    assert summary["weighted_all_faces_recovered"] is True
    assert summary["baseline_failure_reproduced_all_faces"] is True
    assert summary["canonical_controller_change"] is False
    assert summary["canonical_orientation_gate_change"] is False
    assert summary["failed_cell_closed"] is False
    assert summary["robustness_claim"] is False
    assert boundary["profile_scope"]["orientation_gate_status"] == "run_local_diagnostic_noncanonical"
    assert boundary["profile_scope"]["normal_axis_weight_values"] == [1.0, 30.0]
    assert payload["evidence_faces"][0]["weighted_passing_count"] == 2
    assert payload["evidence_faces"][1]["weighted_passing_count"] == 4
