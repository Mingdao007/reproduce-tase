from __future__ import annotations

from scripts.audit_positive_orientation_gate_boundary import gate_label, stage_b_orientation_rows


def test_gate_label_is_file_safe() -> None:
    assert gate_label(0.119) == "orientation_gate_0p119"
    assert gate_label(0.11998) == "orientation_gate_0p11998"


def test_stage_b_orientation_rows_copies_failed_criteria_lists() -> None:
    failed_criteria = ["max_orientation_error_rad"]
    metrics = {
        "stage_b": {
            "rows": [
                {
                    "trajectory": "e2-figure-eight",
                    "target_pair_metrics": {"max_orientation_error_rad": 0.11998},
                    "feasibility_gate": {
                        "feasibility_pass": False,
                        "failed_criteria": failed_criteria,
                    },
                }
            ]
        }
    }

    rows = stage_b_orientation_rows(metrics)

    assert rows == [
        {
            "trajectory": "e2-figure-eight",
            "passed": False,
            "failed_criteria": ["max_orientation_error_rad"],
            "orientation_error_rad": 0.11998,
        }
    ]
    assert rows[0]["failed_criteria"] is not failed_criteria
