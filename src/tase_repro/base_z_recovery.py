from __future__ import annotations

from typing import Any


def base_z_delta_label(delta_m: float) -> str:
    milli = float(delta_m) * 1000.0
    sign = "p" if milli >= 0.0 else "m"
    text = f"{abs(milli):.3f}".replace(".", "p")
    return f"delta_{sign}{text}mm"


def summarize_base_z_recovery_case(
    *,
    case_name: str,
    base_z_offset_delta_m: float,
    stage_a_duration_s: float,
    start_metrics: dict[str, Any],
    terminal_metrics: dict[str, Any],
    path_metrics: dict[str, Any] | None = None,
    stitched_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    start_best = start_metrics["best_candidate"]
    start_passed = bool(start_best["passed"])
    terminal_best = terminal_metrics["best_candidate"]
    terminal_passed = bool(terminal_best["passed"])
    path_passed = bool(path_metrics["path_gate"]["passed"]) if path_metrics is not None else False
    stitched_passed = bool(stitched_metrics["stitched_gate"]["passed"]) if stitched_metrics is not None else False
    if not start_passed and not terminal_passed:
        status = "start_and_terminal_not_found"
    elif not start_passed:
        status = "start_contact_not_found"
    elif not terminal_passed:
        status = "terminal_target_not_found"
    elif path_metrics is None:
        status = "path_audit_not_run"
    elif not path_passed:
        status = "path_gate_failed"
    elif stitched_metrics is None:
        status = "stitched_audit_not_run"
    elif not stitched_passed:
        status = "stitched_gate_failed"
    else:
        status = "recovered"

    path_summary = None
    if path_metrics is not None:
        path_summary = {
            "path_gate_passed": path_passed,
            "terminal_gate_passed": bool(path_metrics["terminal_gate"]["passed"]),
            "min_duration_s": float(path_metrics["timing"]["min_duration_s"]),
            "max_abs_qdot_rad_s": float(path_metrics["timing"]["max_abs_qdot_rad_s"]),
            "target_contact_present_fraction": float(
                path_metrics["evaluation"]["target_contact_present_fraction"]
            ),
            "max_force_error_N": float(path_metrics["evaluation"]["max_force_error_N"]),
            "max_scheduled_xy_error_m": float(path_metrics["evaluation"]["max_scheduled_xy_error_m"]),
            "max_scheduled_orientation_error_rad": float(
                path_metrics["evaluation"]["max_scheduled_orientation_error_rad"]
            ),
        }

    stitched_summary = None
    if stitched_metrics is not None:
        stitched_gate = stitched_metrics["stitched_gate"]
        stage_a = stitched_metrics["stage_a"]
        stitched_summary = {
            "stitched_gate_passed": stitched_passed,
            "stage_a_passed": bool(stitched_gate["stage_a_passed"]),
            "handoff_pass_count": int(stitched_gate["handoff_pass_count"]),
            "handoff_trajectory_count": int(stitched_gate["handoff_trajectory_count"]),
            "stage_a_max_qdot_rad_s": float(stage_a["tracking"]["max_abs_qdot_rad_s"]),
            "stage_a_terminal_force_error_N": float(stage_a["evaluation"]["terminal_force_error_N"]),
            "stage_a_terminal_xy_error_m": float(stage_a["evaluation"]["terminal_reference_xy_error_m"]),
            "stage_a_terminal_orientation_error_rad": float(
                stage_a["evaluation"]["terminal_force_normal_orientation_error_rad"]
            ),
        }

    return {
        "case": str(case_name),
        "base_z_offset_delta_m": float(base_z_offset_delta_m),
        "stage_a_duration_s": float(stage_a_duration_s),
        "status": status,
        "recovered": status == "recovered",
        "start": {
            "passed": start_passed,
            "force_error_N": float(start_best["force_error_N"]),
            "tangential_error_m": float(start_best["tangential_error_m"]),
            "target_contact_count": int(start_best["target_contact_count"]),
            "force_normal_orientation_error_rad": float(
                start_best["force_normal_orientation_error_rad"]
            ),
            "failed_criteria": list(start_best["failed_criteria"]),
        },
        "terminal": {
            "pass_count": int(terminal_metrics["pass_count"]),
            "candidate_count": int(terminal_metrics["candidate_count"]),
            "best_passed": terminal_passed,
            "best_seed": str(terminal_best["seed_label"]),
            "best_failed_criteria": list(terminal_best["failed_criteria"]),
            "best_force_error_N": float(terminal_best["force_error_N"]),
            "best_tangential_error_m": float(terminal_best["tangential_error_m"]),
            "best_orientation_error_rad": float(terminal_best["orientation_error_rad"]),
            "best_max_gate_ratio": float(terminal_best["max_gate_ratio"]),
        },
        "path": path_summary,
        "stitched": stitched_summary,
    }


def aggregate_base_z_recovery(cases: list[dict[str, Any]]) -> dict[str, Any]:
    recovered_cases = [case["case"] for case in cases if case["recovered"]]
    start_cases = [case["case"] for case in cases if case["start"]["passed"]]
    terminal_cases = [case["case"] for case in cases if case["terminal"]["best_passed"]]
    path_cases = [case["case"] for case in cases if case["path"] and case["path"]["path_gate_passed"]]
    stitched_cases = [
        case["case"]
        for case in cases
        if case["stitched"] and case["stitched"]["stitched_gate_passed"]
    ]
    unresolved_cases = [case["case"] for case in cases if not case["recovered"]]
    return {
        "case_count": len(cases),
        "start_pass_count": len(start_cases),
        "terminal_pass_count": len(terminal_cases),
        "path_pass_count": len(path_cases),
        "stitched_pass_count": len(stitched_cases),
        "recovered_count": len(recovered_cases),
        "start_pass_cases": start_cases,
        "terminal_pass_cases": terminal_cases,
        "path_pass_cases": path_cases,
        "stitched_pass_cases": stitched_cases,
        "recovered_cases": recovered_cases,
        "unresolved_cases": unresolved_cases,
    }


def aggregate_base_z_bracket(cases: list[dict[str, Any]]) -> dict[str, Any]:
    start_cases = [case["case"] for case in cases if case["start"]["passed"]]
    terminal_cases = [case["case"] for case in cases if case["terminal"]["passed"]]
    path_cases = [case["case"] for case in cases if case["path"] and case["path"]["path_gate_passed"]]
    recovered = []
    for case in cases:
        for duration in case["durations"]:
            if duration["stitched_passed"]:
                recovered.append(f"{case['case']}@{duration['stage_a_duration_s']}")
    positive_cases = [case for case in cases if case["base_z_offset_delta_m"] > 0.0]
    positive_terminal_pass_mm = [
        1000.0 * float(case["base_z_offset_delta_m"])
        for case in positive_cases
        if case["terminal"]["passed"]
    ]
    positive_recovered_mm = [
        1000.0 * float(case["base_z_offset_delta_m"])
        for case in positive_cases
        if any(duration["stitched_passed"] for duration in case["durations"])
    ]
    return {
        "case_count": len(cases),
        "start_pass_count": len(start_cases),
        "terminal_pass_count": len(terminal_cases),
        "path_geometry_pass_count": len(path_cases),
        "duration_recovered_count": len(recovered),
        "start_pass_cases": start_cases,
        "terminal_pass_cases": terminal_cases,
        "path_geometry_pass_cases": path_cases,
        "duration_recovered_cases": recovered,
        "max_positive_terminal_pass_delta_mm": max(positive_terminal_pass_mm) if positive_terminal_pass_mm else None,
        "max_positive_recovered_delta_mm": max(positive_recovered_mm) if positive_recovered_mm else None,
    }


def aggregate_positive_start_contact(cases: list[dict[str, Any]]) -> dict[str, Any]:
    start_pass_cases = [case["case"] for case in cases if case["start_search"]["passed"]]
    terminal_pass_cases = [case["case"] for case in cases if case["terminal"]["passed"]]
    contact_without_start_pass_cases = [
        case["case"]
        for case in cases
        if not case["start_search"]["passed"] and case["start_search"]["best_target_contact_count"] >= 1
    ]
    start_pass_delta_mm = [
        float(case["base_z_offset_delta_mm"])
        for case in cases
        if case["start_search"]["passed"]
    ]
    terminal_pass_delta_mm = [
        float(case["base_z_offset_delta_mm"])
        for case in cases
        if case["terminal"]["passed"]
    ]
    return {
        "case_count": len(cases),
        "start_pass_count": len(start_pass_cases),
        "terminal_pass_count": len(terminal_pass_cases),
        "contact_without_start_pass_count": len(contact_without_start_pass_cases),
        "start_pass_cases": start_pass_cases,
        "terminal_pass_cases": terminal_pass_cases,
        "contact_without_start_pass_cases": contact_without_start_pass_cases,
        "max_start_pass_delta_mm": max(start_pass_delta_mm) if start_pass_delta_mm else None,
        "max_terminal_pass_delta_mm": max(terminal_pass_delta_mm) if terminal_pass_delta_mm else None,
    }


def aggregate_positive_terminal_orientation(cases: list[dict[str, Any]]) -> dict[str, Any]:
    variants: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        variants.setdefault(str(case["variant"]), []).append(case)

    by_variant: dict[str, dict[str, Any]] = {}
    for variant, variant_cases in sorted(variants.items()):
        diagnostic_pass_cases = [case["case"] for case in variant_cases if case["diagnostic_passed"]]
        force_xy_contact_cases = [
            case["case"] for case in variant_cases if case["force_xy_contact_passed"]
        ]
        force_normal_only_cases = [
            case["case"] for case in variant_cases if case["force_normal_only_passed"]
        ]
        force_xy_deltas = [
            float(case["base_z_offset_delta_mm"])
            for case in variant_cases
            if case["force_xy_contact_passed"]
        ]
        diagnostic_deltas = [
            float(case["base_z_offset_delta_mm"])
            for case in variant_cases
            if case["diagnostic_passed"]
        ]
        force_xy_errors = [
            float(case["full_rotation_error_rad"])
            for case in variant_cases
            if case["force_xy_contact_passed"]
        ]
        all_full_errors = [float(case["full_rotation_error_rad"]) for case in variant_cases]
        all_force_normal_errors = [
            float(case["force_normal_only_error_rad"]) for case in variant_cases
        ]
        yaw_gap_errors = [
            abs(float(case["full_rotation_error_rad"]) - float(case["force_normal_only_error_rad"]))
            for case in variant_cases
        ]
        by_variant[variant] = {
            "case_count": len(variant_cases),
            "diagnostic_pass_count": len(diagnostic_pass_cases),
            "force_xy_contact_pass_count": len(force_xy_contact_cases),
            "force_normal_only_pass_count": len(force_normal_only_cases),
            "diagnostic_pass_cases": diagnostic_pass_cases,
            "force_xy_contact_cases": force_xy_contact_cases,
            "force_normal_only_pass_cases": force_normal_only_cases,
            "max_force_xy_contact_delta_mm": max(force_xy_deltas) if force_xy_deltas else None,
            "max_diagnostic_pass_delta_mm": max(diagnostic_deltas) if diagnostic_deltas else None,
            "min_full_rotation_threshold_for_force_xy_contact_cases_rad": (
                max(force_xy_errors) if force_xy_errors else None
            ),
            "max_full_rotation_error_rad": max(all_full_errors) if all_full_errors else None,
            "max_force_normal_only_error_rad": (
                max(all_force_normal_errors) if all_force_normal_errors else None
            ),
            "max_full_minus_force_normal_abs_rad": max(yaw_gap_errors) if yaw_gap_errors else None,
        }

    return {
        "case_count": len(cases),
        "variant_count": len(variants),
        "variants": by_variant,
    }
