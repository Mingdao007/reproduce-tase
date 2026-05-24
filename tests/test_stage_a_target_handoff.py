from __future__ import annotations

import numpy as np
import pytest

from tase_repro.stage_a_target_handoff import (
    metrics_with_target_pair_force,
    selected_stage_a_target,
    summarize_target_pair_force,
)


def test_selected_stage_a_target_rejects_claim_scope_drift() -> None:
    with pytest.raises(ValueError, match="claim scope"):
        selected_stage_a_target(
            {
                "selected_stage_a_target": {
                    "label": "ur10e_adapted_terminal_setup_diagnostic",
                    "claim_scope": "paper_equivalent",
                }
            }
        )


def test_summarize_target_pair_force_reports_tail_error_and_contact_fraction() -> None:
    summary = summarize_target_pair_force(
        np.array([4.9, 5.1, 5.0, 5.05]),
        np.array([1, 1, 0, 1]),
        target_force_N=5.0,
        tail_fraction=0.5,
    )

    assert summary["target_pair_initial_force_N"] == 4.9
    assert summary["target_pair_final_force_N"] == 5.05
    assert summary["target_pair_tail_mean_abs_force_error_N"] == pytest.approx(0.025)
    assert summary["target_contact_present_fraction"] == 0.75
    assert summary["target_contact_min_count"] == 0
    assert summary["target_contact_max_count"] == 1


def test_metrics_with_target_pair_force_overrides_gate_force_and_contact_fields() -> None:
    metrics = metrics_with_target_pair_force(
        {
            "initial_force_N": 99.0,
            "final_force_N": 99.0,
            "tail_mean_force_N": 99.0,
            "tail_mean_abs_force_error_N": 99.0,
            "max_abs_force_error_N": 99.0,
            "contact_present_fraction": 0.0,
            "max_tangential_position_error_m": 0.001,
        },
        {
            "target_pair_initial_force_N": 4.9,
            "target_pair_final_force_N": 5.0,
            "target_pair_tail_mean_force_N": 5.0,
            "target_pair_tail_mean_abs_force_error_N": 0.0,
            "target_pair_max_abs_force_error_N": 0.1,
            "target_contact_present_fraction": 1.0,
        },
    )

    assert metrics["initial_force_N"] == 4.9
    assert metrics["tail_mean_abs_force_error_N"] == 0.0
    assert metrics["contact_present_fraction"] == 1.0
    assert metrics["max_tangential_position_error_m"] == 0.001
