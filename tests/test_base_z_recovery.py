from __future__ import annotations

from tase_repro.base_z_recovery import (
    aggregate_base_z_bracket,
    aggregate_positive_start_contact,
    aggregate_base_z_recovery,
    base_z_delta_label,
    summarize_base_z_recovery_case,
)


def start_metrics(*, passed: bool) -> dict:
    return {
        "best_candidate": {
            "passed": passed,
            "force_error_N": 0.01 if passed else 1.0,
            "tangential_error_m": 0.001,
            "target_contact_count": 1 if passed else 0,
            "force_normal_orientation_error_rad": 0.17,
            "failed_criteria": [] if passed else ["target_contact_count"],
        }
    }


def terminal_metrics(*, passed: bool) -> dict:
    return {
        "pass_count": 1 if passed else 0,
        "candidate_count": 3,
        "best_candidate": {
            "passed": passed,
            "seed_label": "random_000",
            "failed_criteria": [] if passed else ["orientation_error_rad"],
            "force_error_N": 0.01,
            "tangential_error_m": 0.002,
            "orientation_error_rad": 0.04 if passed else 0.12,
            "max_gate_ratio": 0.5 if passed else 1.5,
        },
    }


def path_metrics(*, passed: bool) -> dict:
    return {
        "path_gate": {"passed": passed},
        "terminal_gate": {"passed": True},
        "timing": {"min_duration_s": 12.0, "max_abs_qdot_rad_s": 0.1},
        "evaluation": {
            "target_contact_present_fraction": 1.0,
            "max_force_error_N": 0.02,
            "max_scheduled_xy_error_m": 0.001,
            "max_scheduled_orientation_error_rad": 0.03,
        },
    }


def stitched_metrics(*, passed: bool) -> dict:
    return {
        "stitched_gate": {
            "passed": passed,
            "stage_a_passed": True,
            "handoff_pass_count": 4 if passed else 3,
            "handoff_trajectory_count": 4,
        },
        "stage_a": {
            "tracking": {"max_abs_qdot_rad_s": 0.12},
            "evaluation": {
                "terminal_force_error_N": 0.01,
                "terminal_reference_xy_error_m": 0.002,
                "terminal_force_normal_orientation_error_rad": 0.04,
            },
        },
    }


def test_base_z_recovery_case_stops_at_terminal_failure() -> None:
    case = summarize_base_z_recovery_case(
        case_name="base_z_plus_1mm",
        base_z_offset_delta_m=0.001,
        stage_a_duration_s=15.0,
        start_metrics=start_metrics(passed=True),
        terminal_metrics=terminal_metrics(passed=False),
    )

    assert case["status"] == "terminal_target_not_found"
    assert case["recovered"] is False
    assert case["path"] is None


def test_base_z_recovery_aggregate_counts_recovered_cases() -> None:
    recovered = summarize_base_z_recovery_case(
        case_name="base_z_minus_1mm",
        base_z_offset_delta_m=-0.001,
        stage_a_duration_s=15.0,
        start_metrics=start_metrics(passed=True),
        terminal_metrics=terminal_metrics(passed=True),
        path_metrics=path_metrics(passed=True),
        stitched_metrics=stitched_metrics(passed=True),
    )
    unresolved = summarize_base_z_recovery_case(
        case_name="base_z_plus_1mm",
        base_z_offset_delta_m=0.001,
        stage_a_duration_s=15.0,
        start_metrics=start_metrics(passed=True),
        terminal_metrics=terminal_metrics(passed=False),
    )

    aggregate = aggregate_base_z_recovery([recovered, unresolved])

    assert aggregate["case_count"] == 2
    assert aggregate["start_pass_cases"] == ["base_z_minus_1mm", "base_z_plus_1mm"]
    assert aggregate["terminal_pass_cases"] == ["base_z_minus_1mm"]
    assert aggregate["recovered_cases"] == ["base_z_minus_1mm"]
    assert aggregate["unresolved_cases"] == ["base_z_plus_1mm"]


def test_base_z_delta_label_is_file_safe() -> None:
    assert base_z_delta_label(-0.001) == "delta_m1p000mm"
    assert base_z_delta_label(0.00025) == "delta_p0p250mm"


def test_base_z_bracket_aggregate_counts_duration_recovery() -> None:
    cases = [
        {
            "case": "delta_p0p250mm",
            "base_z_offset_delta_m": 0.00025,
            "start": {"passed": True},
            "terminal": {"passed": True},
            "path": {"path_gate_passed": True},
            "durations": [
                {"stage_a_duration_s": 15.0, "stitched_passed": False},
                {"stage_a_duration_s": 16.0, "stitched_passed": True},
            ],
        },
        {
            "case": "delta_p1p000mm",
            "base_z_offset_delta_m": 0.001,
            "start": {"passed": False},
            "terminal": {"passed": False},
            "path": None,
            "durations": [],
        },
    ]

    aggregate = aggregate_base_z_bracket(cases)

    assert aggregate["terminal_pass_cases"] == ["delta_p0p250mm"]
    assert aggregate["duration_recovered_cases"] == ["delta_p0p250mm@16.0"]
    assert aggregate["max_positive_terminal_pass_delta_mm"] == 0.25
    assert aggregate["max_positive_recovered_delta_mm"] == 0.25


def test_positive_start_contact_aggregate_distinguishes_contact_from_gate_pass() -> None:
    cases = [
        {
            "case": "delta_p0p500mm",
            "base_z_offset_delta_mm": 0.5,
            "start_search": {"passed": True, "best_target_contact_count": 1},
            "terminal": {"passed": False},
        },
        {
            "case": "delta_p1p000mm",
            "base_z_offset_delta_mm": 1.0,
            "start_search": {"passed": False, "best_target_contact_count": 1},
            "terminal": {"passed": False},
        },
    ]

    aggregate = aggregate_positive_start_contact(cases)

    assert aggregate["start_pass_cases"] == ["delta_p0p500mm"]
    assert aggregate["terminal_pass_cases"] == []
    assert aggregate["contact_without_start_pass_cases"] == ["delta_p1p000mm"]
    assert aggregate["max_start_pass_delta_mm"] == 0.5
