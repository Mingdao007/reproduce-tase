from __future__ import annotations

from scripts.audit_explicit_stage_a_constraint_probe import (
    qdot_criteria_pass,
    strict_setup_path_gate,
    summarize_rows,
    terminal_constraint_cases,
    terminal_criteria_pass,
)


STRICT_THRESHOLDS = {
    "max_final_tangential_error_m": 0.002,
    "max_final_orientation_error_rad": 0.03,
    "max_tail_mean_abs_force_error_N": 0.25,
    "contact_present_fraction_min": 1.0,
    "max_qdot_violation_rad_s": 1.0e-9,
    "max_joint_limit_violation_rad": 1.0e-9,
    "qdot_saturation_fraction_max": 0.01,
    "tail_max_qdot_utilization_max": 0.98,
}


def _path_summary(*, force: float = 0.1, xy: float = 0.001, orient: float = 0.01) -> dict:
    return {
        "terminal_force_error_N": force,
        "terminal_tangential_error_m": xy,
        "terminal_orientation_error_rad": orient,
        "target_contact_present_fraction": 1.0,
        "max_joint_limit_violation_rad": 0.0,
    }


def _tracking_summary(*, qdot_saturation: float = 0.0, tail_util: float = 0.95) -> dict:
    return {
        "max_abs_qdot_rad_s": 0.1425,
        "qdot_saturation_fraction": qdot_saturation,
        "tail_max_qdot_utilization": tail_util,
    }


def test_terminal_constraint_cases_select_expected_contact_manifold_candidates() -> None:
    def case(name: str, terms: list[str], *, opt_q: list[float], best_q: list[float] | None = None) -> dict:
        return {
            "name": name,
            "optimized_terms": terms,
            "best_optimized_candidate": {"q": opt_q},
            "best_candidate": {"q": best_q or opt_q},
        }

    cases = terminal_constraint_cases(
        {
            "cases": [
                case("xy_force", ["xy", "force"], opt_q=[1.0, 2.0]),
                case("xy_orientation", ["xy", "orientation"], opt_q=[3.0, 4.0]),
                case("force_orientation", ["force", "orientation"], opt_q=[5.0, 6.0]),
                case(
                    "xy_force_orientation",
                    ["xy", "force", "orientation"],
                    opt_q=[7.0, 8.0],
                    best_q=[9.0, 10.0],
                ),
            ]
        }
    )

    assert [item.case_id for item in cases] == [
        "terminal_xy_force_hold",
        "terminal_xy_orientation_hold",
        "terminal_force_orientation_hold",
        "terminal_xy_force_orientation_soft_best",
    ]
    assert cases[2].selected_candidate == "best_optimized_candidate"
    assert cases[2].q_rad.tolist() == [5.0, 6.0]
    assert cases[3].selected_candidate == "best_candidate"
    assert cases[3].q_rad.tolist() == [9.0, 10.0]


def test_strict_setup_path_gate_separates_qdot_pass_from_terminal_failure() -> None:
    gate = strict_setup_path_gate(
        path_summary=_path_summary(xy=0.003),
        tracking_summary=_tracking_summary(),
        strict_thresholds=STRICT_THRESHOLDS,
        qdot_limit_rad_s=0.15,
    )

    assert gate["passed"] is False
    assert gate["failed_criteria"] == ["terminal_tangential_error_m"]
    assert qdot_criteria_pass(gate) is True
    assert terminal_criteria_pass(gate) is False

    qdot_failed = strict_setup_path_gate(
        path_summary=_path_summary(),
        tracking_summary=_tracking_summary(qdot_saturation=0.2, tail_util=1.0),
        strict_thresholds=STRICT_THRESHOLDS,
        qdot_limit_rad_s=0.15,
    )
    assert qdot_criteria_pass(qdot_failed) is False
    assert "setup_qdot_saturation_fraction" in qdot_failed["failed_criteria"]
    assert "setup_tail_max_qdot_utilization" in qdot_failed["failed_criteria"]


def test_summarize_rows_counts_terminal_and_qdot_passes_independently() -> None:
    pass_gate = strict_setup_path_gate(
        path_summary=_path_summary(),
        tracking_summary=_tracking_summary(),
        strict_thresholds=STRICT_THRESHOLDS,
        qdot_limit_rad_s=0.15,
    )
    terminal_fail_gate = strict_setup_path_gate(
        path_summary=_path_summary(orient=0.05),
        tracking_summary=_tracking_summary(),
        strict_thresholds=STRICT_THRESHOLDS,
        qdot_limit_rad_s=0.15,
    )
    qdot_fail_gate = strict_setup_path_gate(
        path_summary=_path_summary(),
        tracking_summary=_tracking_summary(qdot_saturation=0.5),
        strict_thresholds=STRICT_THRESHOLDS,
        qdot_limit_rad_s=0.15,
    )

    rows = [
        {
            "case_id": "pass",
            "strict_setup_path_gate": pass_gate,
            "strict_setup_violation_score": 0.0,
            "path_summary": {
                "terminal_tangential_error_m": 0.001,
                "terminal_orientation_error_rad": 0.01,
            },
        },
        {
            "case_id": "terminal_fail",
            "strict_setup_path_gate": terminal_fail_gate,
            "strict_setup_violation_score": 1.0,
            "path_summary": {
                "terminal_tangential_error_m": 0.001,
                "terminal_orientation_error_rad": 0.05,
            },
        },
        {
            "case_id": "qdot_fail",
            "strict_setup_path_gate": qdot_fail_gate,
            "strict_setup_violation_score": 2.0,
            "path_summary": {
                "terminal_tangential_error_m": 0.001,
                "terminal_orientation_error_rad": 0.01,
            },
        },
    ]

    summary = summarize_rows(rows)

    assert summary["strict_setup_path_pass_count"] == 1
    assert summary["terminal_strict_criteria_pass_count"] == 2
    assert summary["qdot_criteria_pass_count"] == 2
    assert summary["setup_failed_criteria_counts"] == {
        "setup_qdot_saturation_fraction": 1,
        "terminal_orientation_error_rad": 1,
    }
    assert summary["strict_paper_equivalent_feasibility"] is False
    assert summary["explicit_stage_a_constraint_probe_complete"] is False
    assert summary["planned_setup_then_trajectory_pass_count"] == 0
