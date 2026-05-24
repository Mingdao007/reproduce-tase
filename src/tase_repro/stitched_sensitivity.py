from __future__ import annotations

from typing import Any


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _worst_stage_b_row(stage_b: dict[str, Any]) -> dict[str, Any]:
    rows = stage_b.get("rows", [])
    if not rows:
        return {
            "trajectory": None,
            "max_tail_force_error_N": None,
            "max_xy_error_m": None,
            "max_orientation_error_rad": None,
            "max_qdot_saturation_fraction": None,
            "min_contact_present_fraction": None,
        }

    max_force = -1.0
    max_xy = -1.0
    max_orientation = -1.0
    max_qdot = -1.0
    min_contact = float("inf")
    force_trajectory = None
    for row in rows:
        metrics = row.get("target_pair_metrics", {})
        force = _as_float(metrics.get("tail_mean_abs_force_error_N"))
        xy = _as_float(metrics.get("max_tangential_position_error_m"))
        orientation = _as_float(metrics.get("max_orientation_error_rad"))
        qdot = _as_float(metrics.get("qdot_saturation_fraction"))
        contact = _as_float(metrics.get("contact_present_fraction"))
        if force is not None and force > max_force:
            max_force = force
            force_trajectory = row.get("trajectory")
        if xy is not None:
            max_xy = max(max_xy, xy)
        if orientation is not None:
            max_orientation = max(max_orientation, orientation)
        if qdot is not None:
            max_qdot = max(max_qdot, qdot)
        if contact is not None:
            min_contact = min(min_contact, contact)

    return {
        "trajectory": force_trajectory,
        "max_tail_force_error_N": max_force if max_force >= 0.0 else None,
        "max_xy_error_m": max_xy if max_xy >= 0.0 else None,
        "max_orientation_error_rad": max_orientation if max_orientation >= 0.0 else None,
        "max_qdot_saturation_fraction": max_qdot if max_qdot >= 0.0 else None,
        "min_contact_present_fraction": min_contact if min_contact != float("inf") else None,
    }


def summarize_stitched_case(
    *,
    case_name: str,
    parameters: dict[str, Any],
    metrics: dict[str, Any],
) -> dict[str, Any]:
    stage_a = metrics.get("stage_a", {})
    stage_b = metrics.get("stage_b", {})
    stitched_gate = metrics.get("stitched_gate", {})
    tracking = stage_a.get("tracking", {})
    evaluation = stage_a.get("evaluation", {})
    terminal_gate = stage_a.get("terminal_gate", {})
    stage_a_gate = stage_a.get("stage_a_gate", {})
    handoff_pass_count = int(stage_b.get("handoff_pass_count", 0))
    trajectory_count = int(stage_b.get("trajectory_count", 0))
    stage_b_failed = [
        {
            "trajectory": row.get("trajectory"),
            "failed_criteria": row.get("feasibility_gate", {}).get("failed_criteria", []),
        }
        for row in stage_b.get("rows", [])
        if not row.get("feasibility_gate", {}).get("feasibility_pass", False)
    ]
    return {
        "case": case_name,
        "parameters": parameters,
        "stitched_passed": bool(stitched_gate.get("passed", False)),
        "stage_a_passed": bool(stage_a_gate.get("passed", False)),
        "stage_b_pass_count": handoff_pass_count,
        "stage_b_trajectory_count": trajectory_count,
        "stage_a_max_qdot_rad_s": _as_float(tracking.get("max_abs_qdot_rad_s")),
        "stage_a_qdot_saturation_fraction": _as_float(tracking.get("qdot_saturation_fraction")),
        "stage_a_final_tracking_error_norm_rad": _as_float(tracking.get("final_tracking_error_norm_rad")),
        "stage_a_max_force_error_N": _as_float(evaluation.get("max_force_error_N")),
        "stage_a_terminal_force_error_N": _as_float(evaluation.get("terminal_force_error_N")),
        "stage_a_terminal_xy_error_m": _as_float(evaluation.get("terminal_reference_xy_error_m")),
        "stage_a_terminal_orientation_error_rad": _as_float(
            evaluation.get("terminal_force_normal_orientation_error_rad")
        ),
        "stage_a_terminal_gate_passed": bool(terminal_gate.get("passed", False)),
        "stage_b_failed_rows": stage_b_failed,
        "stage_b_worst": _worst_stage_b_row(stage_b),
    }


def aggregate_stitched_sensitivity(case_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    case_count = len(case_summaries)
    passing_cases = [row["case"] for row in case_summaries if row["stitched_passed"]]
    failing_cases = [row["case"] for row in case_summaries if not row["stitched_passed"]]
    pass_count = len(passing_cases)
    return {
        "case_count": case_count,
        "stitched_pass_count": pass_count,
        "stitched_fail_count": len(failing_cases),
        "stitched_pass_fraction": float(pass_count / case_count) if case_count else 0.0,
        "passing_cases": passing_cases,
        "failing_cases": failing_cases,
        "all_cases_passed": pass_count == case_count and case_count > 0,
        "claim_scope": "diagnostic_label_sensitivity_audit_not_robustness_or_hardware_claim",
    }
