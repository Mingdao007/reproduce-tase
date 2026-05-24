from __future__ import annotations

from scripts.audit_stage_b_priority_recovery import stage_b_rows


def test_stage_b_rows_copies_failed_criteria_lists() -> None:
    failed_criteria = ["max_orientation_error_rad"]
    metrics = {
        "stage_b": {
            "rows": [
                {
                    "trajectory": "e2-figure-eight",
                    "target_pair_metrics": {
                        "max_orientation_error_rad": 0.11955,
                        "qdot_saturation_fraction": 0.0,
                        "tail_max_qdot_utilization": 0.52,
                        "tail_mean_abs_force_error_N": 0.0008,
                        "max_tangential_position_error_m": 8.2e-05,
                        "max_abs_normal_velocity_slack_m_s": 1.3e-06,
                        "max_angular_velocity_slack_rad_s": 0.00013,
                    },
                    "feasibility_gate": {
                        "feasibility_pass": False,
                        "failed_criteria": failed_criteria,
                    },
                }
            ]
        }
    }

    rows = stage_b_rows(metrics)

    assert rows == [
        {
            "trajectory": "e2-figure-eight",
            "passed": False,
            "failed_criteria": ["max_orientation_error_rad"],
            "orientation_error_rad": 0.11955,
            "qdot_saturation_fraction": 0.0,
            "tail_max_qdot_utilization": 0.52,
            "tail_mean_abs_force_error_N": 0.0008,
            "max_tangential_position_error_m": 8.2e-05,
            "max_abs_normal_velocity_slack_m_s": 1.3e-06,
            "max_angular_velocity_slack_rad_s": 0.00013,
        }
    ]
    assert rows[0]["failed_criteria"] is not failed_criteria
