from __future__ import annotations

from scripts.audit_relaxed_base_z_weighted_handoff import (
    aggregate_cases,
    duration_label,
    failed_rows_text,
    parse_float_list,
)


def _case(
    *,
    scenario: str,
    priority: str,
    duration: float,
    stitched: bool,
    failed: dict[str, list[str]] | None = None,
    orientation: float = 0.1195,
    qdot: float = 0.0,
) -> dict:
    return {
        "scenario": scenario,
        "orientation_priority_mode": priority,
        "stage_a_duration_s": duration,
        "stage_a_passed": True,
        "stitched_passed": stitched,
        "handoff_pass_count": 4 if stitched else 3,
        "handoff_trajectory_count": 4,
        "failed_trajectories": list((failed or {}).keys()),
        "failed_criteria_by_trajectory": failed or {},
        "max_stage_b_orientation_error_rad": orientation,
        "min_stage_b_orientation_margin_to_gate_rad": 0.12 - orientation,
        "max_stage_b_qdot_saturation_fraction": qdot,
        "max_stage_b_tail_qdot_utilization": 1.0 if qdot else 0.52,
        "max_stage_b_tail_force_error_N": 0.001,
    }


def test_aggregate_cases_tracks_weighted_recovery_without_closing_cell() -> None:
    cases = [
        _case(
            scenario="linear_kp0_normal1",
            priority="linear_primary",
            duration=15.0,
            stitched=False,
            failed={"e2-figure-eight": ["qdot_saturation_fraction"]},
            orientation=0.1204,
            qdot=0.997,
        ),
        _case(
            scenario="weighted_kp0_normal1",
            priority="weighted",
            duration=15.0,
            stitched=True,
        ),
        _case(
            scenario="linear_kp0_normal1",
            priority="linear_primary",
            duration=16.0,
            stitched=False,
            failed={"e2-figure-eight": ["qdot_saturation_fraction"]},
            orientation=0.1204,
            qdot=0.997,
        ),
        _case(
            scenario="weighted_kp0_normal1",
            priority="weighted",
            duration=16.0,
            stitched=True,
        ),
    ]

    aggregate = aggregate_cases(cases)

    assert aggregate["case_count"] == 4
    assert aggregate["tested_stage_a_durations_s"] == [15.0, 16.0]
    assert aggregate["baseline_failing_count"] == 2
    assert aggregate["weighted_passing_count"] == 2
    assert aggregate["weighted_candidate_recovered_any_duration"] is True
    assert aggregate["weighted_candidate_recovered_all_durations"] is True
    assert aggregate["all_weighted_cases_recovered"] is True
    assert aggregate["candidate_closure_boundary"]["original_failed_cell_closed"] is False
    assert aggregate["candidate_closure_boundary"]["canonical_orientation_gate_change_accepted"] is False
    assert aggregate["candidate_closure_boundary"]["canonical_controller_change_accepted"] is False


def test_parse_and_labels_are_stable() -> None:
    assert parse_float_list("15.0, 16,18.5") == [15.0, 16.0, 18.5]
    assert duration_label(15.0) == "15s"
    assert duration_label(18.5) == "18p5s"


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
