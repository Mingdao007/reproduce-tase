from __future__ import annotations

import math
import pathlib

from scripts.audit_base_z_plus1mm_split import build_payload, classify_split, handoff_count


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_classify_split_keeps_recovery_diagnostic_only() -> None:
    split = classify_split(
        {
            "exact_orientation_gate_rad": 0.08,
            "relaxed_gate_rad": 0.12,
            "terminal_orientation_error_rad": 0.11948560786548146,
            "exact_start_passed": False,
            "broader_start_search_passed": True,
            "terminal_force_xy_contact_passed": True,
            "terminal_diagnostic_passed": False,
            "relaxed_terminal_passed": True,
            "relaxed_path_passed": True,
            "relaxed_stitched_recovered": False,
        }
    )

    assert split["start_contact_is_local_seed_limited"] is True
    assert split["terminal_path_are_gate_limited"] is True
    assert split["stage_a_path_recovered_under_relaxed_gate"] is True
    assert split["stage_b_handoff_remains_blocked"] is True
    assert split["failed_cell_closed"] is False
    assert split["canonical_orientation_gate_change_accepted"] is False
    assert split["canonical_config_change_accepted"] is False
    assert split["robustness_claim"] is False


def test_build_payload_splits_base_z_plus1mm_failure() -> None:
    payload = build_payload(
        execution_audit_path=ROOT
        / "runs"
        / "failed_diagnostic_robustness_experiment_audit"
        / "20260525T061328"
        / "metrics.yaml",
        exact_metrics_path=ROOT
        / "runs"
        / "failed_diagnostic_robustness_experiment_matrix"
        / "20260525T053909"
        / "experiments"
        / "base_z_plus1mm"
        / "metrics.yaml",
        start_metrics_path=ROOT
        / "runs"
        / "positive_base_z_start_contact"
        / "20260524T170350"
        / "metrics.yaml",
        terminal_metrics_path=ROOT
        / "runs"
        / "positive_terminal_orientation"
        / "20260524T171705"
        / "metrics.yaml",
        relaxed_metrics_path=ROOT
        / "runs"
        / "positive_relaxed_orientation_recovery"
        / "20260524T172909"
        / "metrics.yaml",
    )

    summary = payload["summary"]
    assert summary["base_z_offset_delta_mm"] == 1.0
    assert summary["exact_planned_cell_status"] == "executed_unresolved"
    assert summary["exact_closure_passed"] is False
    assert summary["exact_start_passed"] is False
    assert summary["broader_start_search_passed"] is True
    assert summary["start_contact_is_local_seed_limited"] is True
    assert summary["terminal_force_xy_contact_passed"] is True
    assert summary["terminal_diagnostic_passed"] is False
    assert math.isclose(summary["terminal_orientation_error_rad"], 0.11948560786548146)
    assert summary["exact_orientation_gate_rad"] == 0.08
    assert math.isclose(summary["orientation_excess_over_exact_gate_rad"], 0.03948560786548146)
    assert summary["relaxed_gate_rad"] == 0.12
    assert math.isclose(summary["relaxed_gate_margin_rad"], 0.000514392134518534)
    assert summary["relaxed_terminal_passed"] is True
    assert summary["relaxed_path_passed"] is True
    assert math.isclose(summary["relaxed_path_min_duration_s"], 10.018584837157274)
    assert summary["relaxed_stitched_recovered"] is False
    assert summary["relaxed_stage_b_handoff_pass_counts"] == ["3/4", "3/4"]
    assert summary["failed_cell_closed"] is False
    assert payload["claim_boundary"]["canonical_orientation_gate_change"] is False
    assert payload["claim_boundary"]["hardware_readiness"] is False


def test_handoff_count_formats_stage_b_pass_ratio() -> None:
    assert handoff_count({"handoff_pass_count": 3, "handoff_trajectory_count": 4}) == "3/4"
