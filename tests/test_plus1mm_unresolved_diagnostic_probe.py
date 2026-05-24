from __future__ import annotations

import math
import pathlib

from scripts.audit_plus1mm_unresolved_diagnostic_probe import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_plus1mm_probe_classifies_all_v103_unresolved_cells() -> None:
    payload = build_payload(
        execution_audit_path=ROOT
        / "runs"
        / "failed_diagnostic_robustness_experiment_audit"
        / "20260525T061328"
        / "metrics.yaml",
        experiment_root=ROOT
        / "runs"
        / "failed_diagnostic_robustness_experiment_matrix"
        / "20260525T053909"
        / "experiments",
    )

    summary = payload["summary"]
    assert summary["planned_failed_cell_count"] == 4
    assert summary["executed_cell_count"] == 4
    assert summary["closed_cell_count"] == 0
    assert summary["not_executed_cell_count"] == 0
    assert summary["unresolved_cell_ids"] == [
        "base_z_plus1mm",
        "positive_fast_timing_0p0075",
        "positive_orientation_gate_0p119",
        "weighted_plus1mm_0p119_gate",
    ]
    assert summary["qdot_limited_cell_ids"] == ["positive_fast_timing_0p0075"]
    assert summary["probe_closes_failed_cells"] is False


def test_plus1mm_probe_preserves_orientation_gate_boundary() -> None:
    payload = build_payload(
        execution_audit_path=ROOT
        / "runs"
        / "failed_diagnostic_robustness_experiment_audit"
        / "20260525T061328"
        / "metrics.yaml",
        experiment_root=ROOT
        / "runs"
        / "failed_diagnostic_robustness_experiment_matrix"
        / "20260525T053909"
        / "experiments",
    )
    rows = {row["cell_id"]: row for row in payload["cell_rows"]}

    positive_gate = rows["positive_orientation_gate_0p119"]
    assert positive_gate["min_passing_orientation_gate_rad"] == 0.11998
    assert positive_gate["max_failing_orientation_gate_rad"] == 0.11997
    assert math.isclose(
        positive_gate["stage_b_orientation_excess_over_current_gate_rad"],
        0.0009788204275829022,
    )

    weighted = rows["weighted_plus1mm_0p119_gate"]
    assert weighted["current_gate_case_count"] == 4
    assert weighted["current_gate_failed_count"] == 4
    assert weighted["diagnostic_min_passing_gates_rad"] == [0.11955, 0.1196]
    assert weighted["current_gate_max_qdot_saturation_fraction"] == 0.0
    assert math.isclose(
        weighted["current_gate_stage_b_orientation_excess_over_current_gate_rad"],
        0.0005664520369604714,
    )

    assert payload["claim_boundary"]["orientation_gate_acceptance"] is False
    assert payload["claim_boundary"]["do_not_mark_goal_complete"] is True
