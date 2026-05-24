from __future__ import annotations

from scripts.audit_positive_fast_weighted_full_cell import aggregate_cases, failed_rows_text


def test_aggregate_cases_tracks_weighted_candidate_without_closing_cell() -> None:
    cases = [
        {
            "scenario": "baseline",
            "orientation_priority_mode": "linear_primary",
            "stage_a_passed": True,
            "stitched_passed": False,
            "max_stage_b_orientation_error_rad": 0.1202,
            "max_stage_b_qdot_saturation_fraction": 0.999,
            "max_stage_b_tail_qdot_utilization": 1.0,
            "max_stage_b_tail_force_error_N": 0.006,
        },
        {
            "scenario": "weighted",
            "orientation_priority_mode": "weighted",
            "stage_a_passed": True,
            "stitched_passed": True,
            "max_stage_b_orientation_error_rad": 0.11955,
            "max_stage_b_qdot_saturation_fraction": 0.0,
            "max_stage_b_tail_qdot_utilization": 0.52,
            "max_stage_b_tail_force_error_N": 0.001,
        },
    ]

    aggregate = aggregate_cases(cases)

    assert aggregate["scenario_count"] == 2
    assert aggregate["passing_scenario_count"] == 1
    assert aggregate["passing_scenarios"] == ["weighted"]
    assert aggregate["failing_scenarios"] == ["baseline"]
    assert aggregate["weighted_candidate_recovered"] is True
    assert aggregate["all_weighted_candidates_recovered"] is True
    assert aggregate["candidate_closure_boundary"]["original_failed_cell_closed"] is False
    assert aggregate["candidate_closure_boundary"]["canonical_controller_change_accepted"] is False
    assert aggregate["best_orientation_scenario"] == "weighted"
    assert aggregate["min_stage_b_qdot_saturation_fraction"] == 0.0


def test_failed_rows_text_reports_none_or_trajectory_criteria() -> None:
    assert failed_rows_text({"failed_criteria_by_trajectory": {}}) == "none"
    assert (
        failed_rows_text(
            {
                "failed_criteria_by_trajectory": {
                    "e2-figure-eight": ["qdot_saturation_fraction", "max_orientation_error_rad"]
                }
            }
        )
        == "e2-figure-eight:qdot_saturation_fraction,max_orientation_error_rad"
    )
