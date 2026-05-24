from __future__ import annotations

import pytest

from tase_repro.stitched_sensitivity import aggregate_stitched_sensitivity, summarize_stitched_case


def _metrics(*, stitched: bool = True, stage_a: bool = True, handoff_pass_count: int = 2) -> dict:
    return {
        "stage_a": {
            "tracking": {
                "max_abs_qdot_rad_s": 0.1,
                "qdot_saturation_fraction": 0.0,
                "final_tracking_error_norm_rad": 0.0,
            },
            "evaluation": {
                "max_force_error_N": 0.2,
                "terminal_force_error_N": 0.01,
                "terminal_reference_xy_error_m": 0.002,
                "terminal_force_normal_orientation_error_rad": 0.07,
            },
            "terminal_gate": {"passed": stage_a},
            "stage_a_gate": {"passed": stage_a},
        },
        "stage_b": {
            "handoff_pass_count": handoff_pass_count,
            "trajectory_count": 2,
            "rows": [
                {
                    "trajectory": "a",
                    "target_pair_metrics": {
                        "tail_mean_abs_force_error_N": 0.01,
                        "max_tangential_position_error_m": 1e-6,
                        "max_orientation_error_rad": 0.07,
                        "qdot_saturation_fraction": 0.0,
                        "contact_present_fraction": 1.0,
                    },
                    "feasibility_gate": {"feasibility_pass": True, "failed_criteria": []},
                },
                {
                    "trajectory": "b",
                    "target_pair_metrics": {
                        "tail_mean_abs_force_error_N": 0.04,
                        "max_tangential_position_error_m": 2e-6,
                        "max_orientation_error_rad": 0.08,
                        "qdot_saturation_fraction": 0.2,
                        "contact_present_fraction": 0.9,
                    },
                    "feasibility_gate": {
                        "feasibility_pass": handoff_pass_count == 2,
                        "failed_criteria": [] if handoff_pass_count == 2 else ["contact_present_fraction"],
                    },
                },
            ],
        },
        "stitched_gate": {"passed": stitched},
    }


def test_summarize_stitched_case_extracts_stage_b_worst_metrics() -> None:
    summary = summarize_stitched_case(case_name="nominal", parameters={}, metrics=_metrics())

    assert summary["stitched_passed"] is True
    assert summary["stage_a_passed"] is True
    assert summary["stage_b_pass_count"] == 2
    assert summary["stage_b_worst"]["trajectory"] == "b"
    assert summary["stage_b_worst"]["max_tail_force_error_N"] == pytest.approx(0.04)
    assert summary["stage_b_worst"]["min_contact_present_fraction"] == pytest.approx(0.9)


def test_summarize_stitched_case_records_failed_stage_b_rows() -> None:
    summary = summarize_stitched_case(case_name="contact_loss", parameters={}, metrics=_metrics(stitched=False, handoff_pass_count=1))

    assert summary["stitched_passed"] is False
    assert summary["stage_b_failed_rows"] == [
        {"trajectory": "b", "failed_criteria": ["contact_present_fraction"]}
    ]


def test_aggregate_stitched_sensitivity_separates_passing_and_failing_cases() -> None:
    rows = [
        summarize_stitched_case(case_name="pass", parameters={}, metrics=_metrics(stitched=True)),
        summarize_stitched_case(case_name="fail", parameters={}, metrics=_metrics(stitched=False)),
    ]

    aggregate = aggregate_stitched_sensitivity(rows)

    assert aggregate["case_count"] == 2
    assert aggregate["stitched_pass_count"] == 1
    assert aggregate["stitched_pass_fraction"] == pytest.approx(0.5)
    assert aggregate["passing_cases"] == ["pass"]
    assert aggregate["failing_cases"] == ["fail"]
    assert aggregate["all_cases_passed"] is False
