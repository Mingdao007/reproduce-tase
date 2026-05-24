from __future__ import annotations

from scripts.audit_positive_stage_b_e2_margin import aggregate_qdot_probe


def test_aggregate_qdot_probe_records_boundary_and_extrema() -> None:
    rows = [
        {
            "stage_a_passed": True,
            "e2_passed": False,
            "qdot_limit_rad_s": 0.15,
            "qdot_saturation_fraction": 0.999,
            "tail_max_qdot_utilization": 1.0,
            "max_orientation_error_rad": 0.1202,
        },
        {
            "stage_a_passed": True,
            "e2_passed": True,
            "qdot_limit_rad_s": 0.2,
            "qdot_saturation_fraction": 0.0,
            "tail_max_qdot_utilization": 0.76,
            "max_orientation_error_rad": 0.1198,
        },
    ]

    aggregate = aggregate_qdot_probe(rows)

    assert aggregate == {
        "row_count": 2,
        "pass_count": 1,
        "fail_count": 1,
        "min_passing_qdot_limit_rad_s": 0.2,
        "max_failing_qdot_limit_rad_s": 0.15,
        "max_qdot_saturation_fraction": 0.999,
        "min_qdot_saturation_fraction": 0.0,
        "max_tail_qdot_utilization": 1.0,
        "max_orientation_error_rad": 0.1202,
    }
