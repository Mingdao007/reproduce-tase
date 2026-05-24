from __future__ import annotations

from scripts.audit_positive_fast_e2_orientation_margin import aggregate_cases


def test_aggregate_cases_identifies_passing_and_best_orientation() -> None:
    cases = [
        {
            "scenario": "baseline",
            "stage_a_passed": True,
            "e2_passed": False,
            "orientation_error_rad": 0.1202,
            "orientation_excess_over_gate_rad": 0.0002,
            "qdot_saturation_fraction": 0.999,
            "tail_max_qdot_utilization": 1.0,
            "tail_mean_abs_force_error_N": 0.006,
        },
        {
            "scenario": "weighted",
            "stage_a_passed": True,
            "e2_passed": True,
            "orientation_error_rad": 0.11955,
            "orientation_excess_over_gate_rad": -0.00045,
            "qdot_saturation_fraction": 0.0,
            "tail_max_qdot_utilization": 0.52,
            "tail_mean_abs_force_error_N": 0.001,
        },
    ]

    aggregate = aggregate_cases(cases, orientation_gate_rad=0.12)

    assert aggregate["scenario_count"] == 2
    assert aggregate["e2_pass_count"] == 1
    assert aggregate["passing_scenarios"] == ["weighted"]
    assert aggregate["orientation_clear_scenarios"] == ["weighted"]
    assert aggregate["qdot_clear_scenarios"] == ["weighted"]
    assert aggregate["tail_qdot_clear_scenarios"] == ["weighted"]
    assert aggregate["best_orientation_scenario"] == "weighted"
    assert aggregate["min_orientation_error_rad"] == 0.11955
    assert aggregate["max_qdot_saturation_fraction"] == 0.999
