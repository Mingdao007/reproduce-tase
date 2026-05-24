#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

OFFLINE_BLOCKERS_METRICS = ROOT / "runs" / "offline_completion_blockers" / "20260525T020734" / "metrics.yaml"
STRICT_BLOCKERS_METRICS = ROOT / "runs" / "strict_feasibility_blockers" / "20260525T051640" / "metrics.yaml"
STITCHED_SENSITIVITY_METRICS = (
    ROOT / "runs" / "stitched_stage_a_handoff_sensitivity" / "20260524T161111" / "metrics.yaml"
)
TIMING_MARGIN_METRICS = (
    ROOT / "runs" / "stitched_stage_a_handoff_timing_margin" / "20260524T162005" / "metrics.yaml"
)
BASE_Z_RECOVERY_METRICS = ROOT / "runs" / "stage_a_base_z_recovery" / "20260524T163746" / "metrics.yaml"
BASE_Z_BRACKET_METRICS = ROOT / "runs" / "stage_a_base_z_bracket" / "20260524T165411" / "metrics.yaml"
POSITIVE_SENSITIVITY_METRICS = (
    ROOT / "runs" / "positive_stitched_sensitivity" / "20260524T193845" / "metrics.yaml"
)
QDOT012_POSITIVE_METRICS = (
    ROOT / "runs" / "positive_full_stitched_recovery" / "20260524T195501" / "metrics.yaml"
)
WEIGHTED_ORIENTATION_SENSITIVITY_METRICS = (
    ROOT / "runs" / "weighted_orientation_model_sensitivity" / "20260524T233945" / "metrics.yaml"
)
CONTACT_MARGIN_METRICS = (
    ROOT / "runs" / "contact_orientation_calibration_margin" / "20260524T235723" / "metrics.yaml"
)


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)


def git_value(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def write_git_state(out_dir: pathlib.Path, *, command: list[str]) -> None:
    branch = git_value(["branch", "--show-current"])
    commit = git_value(["rev-parse", "HEAD"])
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
    lines = [
        "# Git State",
        "",
        f"- Branch: `{branch}`",
        f"- Commit: `{commit}`",
        f"- Dirty tree: `{bool(status)}`",
        "- Status:",
        "",
        "```text",
        status,
        "```",
        "",
        "- Command:",
        "",
        "```bash",
        " ".join(command),
        "```",
        "",
    ]
    (out_dir / "git_state.md").write_text("\n".join(lines), encoding="utf-8")


def relative(path: pathlib.Path) -> str:
    return str(path.relative_to(ROOT))


def fraction(numerator: int | None, denominator: int | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def count_stage_b_failed_criteria(cases: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for case in cases:
        for row in case.get("stage_b_failed_rows", []):
            for criterion in row.get("failed_criteria", []):
                counts[criterion] = counts.get(criterion, 0) + 1
    return dict(sorted(counts.items()))


def case_index(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {row[key]: row for row in rows}


def summarize_baseline_sensitivity(metrics: dict[str, Any]) -> dict[str, Any]:
    aggregate = metrics["aggregate"]
    failing_cases = [case for case in metrics["cases"] if not case.get("stitched_passed")]
    return {
        "path": relative(STITCHED_SENSITIVITY_METRICS),
        "case_count": aggregate["case_count"],
        "stitched_pass_count": aggregate["stitched_pass_count"],
        "stitched_fail_count": aggregate["stitched_fail_count"],
        "stitched_pass_fraction": aggregate["stitched_pass_fraction"],
        "all_cases_passed": aggregate["all_cases_passed"],
        "passing_cases": list(aggregate["passing_cases"]),
        "failing_cases": list(aggregate["failing_cases"]),
        "stage_a_failed_cases": [case["case"] for case in failing_cases if not case.get("stage_a_passed")],
        "stage_b_failed_criteria_counts": count_stage_b_failed_criteria(failing_cases),
        "worst_case_snapshots": [
            {
                "case": case["case"],
                "stage_a_passed": case.get("stage_a_passed"),
                "stage_b_pass_count": case.get("stage_b_pass_count"),
                "stage_b_trajectory_count": case.get("stage_b_trajectory_count"),
                "stage_a_terminal_gate_passed": case.get("stage_a_terminal_gate_passed"),
                "stage_a_terminal_force_error_N": case.get("stage_a_terminal_force_error_N"),
                "stage_a_terminal_xy_error_m": case.get("stage_a_terminal_xy_error_m"),
                "stage_b_worst": case.get("stage_b_worst"),
            }
            for case in failing_cases
        ],
    }


def summarize_timing_margin(metrics: dict[str, Any]) -> dict[str, Any]:
    aggregate = metrics["aggregate"]
    return {
        "path": relative(TIMING_MARGIN_METRICS),
        "case_count": aggregate["case_count"],
        "stitched_pass_count": aggregate["stitched_pass_count"],
        "stitched_fail_count": aggregate["stitched_fail_count"],
        "all_cases_passed": aggregate["all_cases_passed"],
        "passing_cases": list(aggregate["passing_cases"]),
        "failing_cases": list(aggregate["failing_cases"]),
        "recovered_boundaries": {
            "stage_a_duration_s": {
                "last_failing_tested": 14.0,
                "first_passing_tested": 14.5,
            },
            "qdot012_stage_a_duration_s": {
                "last_failing_tested": 17.5,
                "first_passing_tested": 18.0,
            },
            "paper_time_scale": {
                "last_passing_tested": 0.012,
                "first_failing_tested": 0.0125,
            },
        },
        "claim_scope": aggregate.get("claim_scope"),
    }


def summarize_base_z_recovery(metrics: dict[str, Any]) -> dict[str, Any]:
    aggregate = metrics["aggregate"]
    return {
        "path": relative(BASE_Z_RECOVERY_METRICS),
        "case_count": aggregate["case_count"],
        "recovered_count": aggregate["recovered_count"],
        "recovered_cases": list(aggregate["recovered_cases"]),
        "unresolved_cases": list(aggregate["unresolved_cases"]),
        "status_by_case": {
            case["case"]: {
                "status": case["status"],
                "recovered": case["recovered"],
                "base_z_offset_delta_m": case["base_z_offset_delta_m"],
                "stage_a_duration_s": case["stage_a_duration_s"],
            }
            for case in metrics["cases"]
        },
    }


def summarize_base_z_bracket(metrics: dict[str, Any]) -> dict[str, Any]:
    aggregate = metrics["aggregate"]
    unresolved_cases = [
        case["case"]
        for case in metrics["cases"]
        if case.get("status") not in {"recovered_at_tested_duration"}
    ]
    status_counts: dict[str, int] = {}
    for case in metrics["cases"]:
        status = case.get("status")
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "path": relative(BASE_Z_BRACKET_METRICS),
        "case_count": aggregate["case_count"],
        "start_pass_count": aggregate["start_pass_count"],
        "terminal_pass_count": aggregate["terminal_pass_count"],
        "path_geometry_pass_count": aggregate["path_geometry_pass_count"],
        "duration_recovered_count": aggregate["duration_recovered_count"],
        "duration_recovered_cases": list(aggregate["duration_recovered_cases"]),
        "max_positive_terminal_pass_delta_mm": aggregate["max_positive_terminal_pass_delta_mm"],
        "max_positive_recovered_delta_mm": aggregate["max_positive_recovered_delta_mm"],
        "unresolved_cases": unresolved_cases,
        "status_counts": dict(sorted(status_counts.items())),
    }


def summarize_positive_sensitivity(metrics: dict[str, Any]) -> dict[str, Any]:
    aggregate = metrics["aggregate"]
    scenarios = case_index(metrics["scenarios"], "scenario")
    failing_scenarios = list(aggregate["failing_scenarios"])
    return {
        "path": relative(POSITIVE_SENSITIVITY_METRICS),
        "scenario_count": aggregate["scenario_count"],
        "matrix_case_count": aggregate["matrix_case_count"],
        "matrix_stitched_pass_count": aggregate["matrix_stitched_pass_count"],
        "matrix_stitched_fail_count": aggregate["matrix_stitched_fail_count"],
        "matrix_stitched_pass_fraction": fraction(
            aggregate["matrix_stitched_pass_count"], aggregate["matrix_case_count"]
        ),
        "all_scenarios_passed": aggregate["all_scenarios_passed"],
        "failing_scenarios": failing_scenarios,
        "failing_scenario_details": {
            name: {
                "stitched_pass_count": scenarios[name]["aggregate"]["stitched_pass_count"],
                "case_count": scenarios[name]["aggregate"]["case_count"],
                "failing_cases": list(scenarios[name]["aggregate"]["failing_cases"]),
                "max_positive_stitched_pass_delta_mm": scenarios[name]["aggregate"].get(
                    "max_positive_stitched_pass_delta_mm"
                ),
                "max_stage_b_qdot_saturation_fraction": scenarios[name]["aggregate"].get(
                    "max_stage_b_qdot_saturation_fraction"
                ),
                "max_stage_b_tail_qdot_utilization": scenarios[name]["aggregate"].get(
                    "max_stage_b_tail_qdot_utilization"
                ),
                "max_stage_b_orientation_error_rad": scenarios[name]["aggregate"].get(
                    "max_stage_b_orientation_error_rad"
                ),
            }
            for name in failing_scenarios
        },
    }


def summarize_qdot012_positive_recovery(metrics: dict[str, Any]) -> dict[str, Any]:
    aggregate = metrics["aggregate"]
    return {
        "path": relative(QDOT012_POSITIVE_METRICS),
        "stage_a_duration_s": metrics["stage_a_duration_s"],
        "qdot_limit_rad_s": metrics["qdot_limit_rad_s"],
        "paper_time_scale": metrics["paper_time_scale"],
        "max_orientation_error_rad": metrics["max_orientation_error_rad"],
        "case_count": aggregate["case_count"],
        "stitched_pass_count": aggregate["stitched_pass_count"],
        "all_cases_passed": aggregate["all_cases_passed"],
        "max_positive_stitched_pass_delta_mm": aggregate["max_positive_stitched_pass_delta_mm"],
        "max_stage_b_qdot_saturation_fraction": aggregate["max_stage_b_qdot_saturation_fraction"],
        "claim_scope": "diagnostic_positive_recovery_not_formal_robustness",
    }


def summarize_orientation_sensitivity(metrics: dict[str, Any]) -> dict[str, Any]:
    critical_rows = metrics["critical_full_rows"]
    max_excess_row = max(critical_rows, key=lambda row: row["stage_b_excess_over_gate_rad"])
    return {
        "path": relative(WEIGHTED_ORIENTATION_SENSITIVITY_METRICS),
        "orientation_gate_rad": metrics["orientation_gate_rad"],
        "critical_row_count": len(critical_rows),
        "all_critical_rows_fail_plus1mm_gate": all(row["stitched_pass_count"] == 7 for row in critical_rows),
        "max_stage_b_excess_over_gate_rad": max_excess_row["stage_b_excess_over_gate_rad"],
        "max_stage_b_excess_over_gate_deg": max_excess_row["stage_b_excess_over_gate_deg"],
        "max_excess_group": max_excess_row["group"],
        "failing_cases": [case for row in critical_rows for case in row.get("failing_cases", [])],
        "terminal_model_sensitivity": dict(metrics["terminal_model_sensitivity"]),
    }


def summarize_contact_margin(metrics: dict[str, Any]) -> dict[str, Any]:
    critical_rows = metrics.get("critical_rows", [])
    corrections = metrics.get("equivalent_corrections", {})
    return {
        "path": relative(CONTACT_MARGIN_METRICS),
        "critical_row_count": len(critical_rows),
        "accepted_replacement_gate": False,
        "contact_calibration_claim": False,
        "hardest_row": metrics.get("hardest_row"),
        "required_normal_rotation_rad": corrections.get("required_normal_rotation_rad"),
        "required_normal_rotation_deg": corrections.get("required_normal_rotation_deg"),
        "equivalent_base_z_or_contact_point_um": corrections.get(
            "equivalent_base_z_or_contact_point_um"
        ),
        "continuous_required_gate_rad": corrections.get("continuous_required_gate_rad"),
    }


def build_audit() -> dict[str, Any]:
    offline_blockers = load_yaml(OFFLINE_BLOCKERS_METRICS)
    strict_blockers = load_yaml(STRICT_BLOCKERS_METRICS)
    baseline = load_yaml(STITCHED_SENSITIVITY_METRICS)
    timing_margin = load_yaml(TIMING_MARGIN_METRICS)
    base_z_recovery = load_yaml(BASE_Z_RECOVERY_METRICS)
    base_z_bracket = load_yaml(BASE_Z_BRACKET_METRICS)
    positive_sensitivity = load_yaml(POSITIVE_SENSITIVITY_METRICS)
    qdot012_positive = load_yaml(QDOT012_POSITIVE_METRICS)
    orientation_sensitivity = load_yaml(WEIGHTED_ORIENTATION_SENSITIVITY_METRICS)
    contact_margin = load_yaml(CONTACT_MARGIN_METRICS)

    baseline_summary = summarize_baseline_sensitivity(baseline)
    timing_summary = summarize_timing_margin(timing_margin)
    base_z_recovery_summary = summarize_base_z_recovery(base_z_recovery)
    base_z_bracket_summary = summarize_base_z_bracket(base_z_bracket)
    positive_summary = summarize_positive_sensitivity(positive_sensitivity)
    qdot012_summary = summarize_qdot012_positive_recovery(qdot012_positive)
    orientation_summary = summarize_orientation_sensitivity(orientation_sensitivity)
    contact_margin_summary = summarize_contact_margin(contact_margin)

    robustness_complete = baseline["aggregate"]["all_cases_passed"] is True
    robustness_offline_actionable = "robustness_to_contact_model_perturbations" in offline_blockers.get(
        "offline_actionable_nonfinal_requirement_ids", []
    )
    unresolved_blockers = [
        "base_z_plus_1mm_contact_or_terminal_orientation",
        "base_z_minus_path_duration_or_geometry_margin",
        "faster_timing_qdot_tail_utilization",
        "tightened_orientation_gate_plus1mm",
        "contact_model_calibration_missing",
    ]
    recovered_nonfinal = [
        "nominal_diagnostic_stitched_policy",
        "stage_a_16s_minus1mm_recovery",
        "timing_margin_stage_a_14p5",
        "timing_margin_qdot012_stage_a_18p0",
        "positive_relaxed_full_matrix_qdot012_18p035",
    ]

    return {
        "audit_source": "v97 robustness blockers",
        "overall_goal_complete": False,
        "robustness_complete": robustness_complete,
        "completion_claim_allowed": False,
        "offline_actionable_from_v95": robustness_offline_actionable,
        "strict_feasibility_complete_from_v96": strict_blockers.get("strict_feasibility_complete"),
        "source_files": {
            "offline_blockers_metrics": relative(OFFLINE_BLOCKERS_METRICS),
            "strict_blockers_metrics": relative(STRICT_BLOCKERS_METRICS),
            "stitched_sensitivity_metrics": relative(STITCHED_SENSITIVITY_METRICS),
            "timing_margin_metrics": relative(TIMING_MARGIN_METRICS),
            "base_z_recovery_metrics": relative(BASE_Z_RECOVERY_METRICS),
            "base_z_bracket_metrics": relative(BASE_Z_BRACKET_METRICS),
            "positive_sensitivity_metrics": relative(POSITIVE_SENSITIVITY_METRICS),
            "qdot012_positive_metrics": relative(QDOT012_POSITIVE_METRICS),
            "weighted_orientation_sensitivity_metrics": relative(
                WEIGHTED_ORIENTATION_SENSITIVITY_METRICS
            ),
            "contact_margin_metrics": relative(CONTACT_MARGIN_METRICS),
        },
        "baseline_sensitivity": baseline_summary,
        "timing_margin": timing_summary,
        "base_z_recovery": base_z_recovery_summary,
        "base_z_bracket": base_z_bracket_summary,
        "positive_stitched_sensitivity": positive_summary,
        "qdot012_positive_recovery": qdot012_summary,
        "weighted_orientation_model_sensitivity": orientation_summary,
        "contact_orientation_margin": contact_margin_summary,
        "blocker_summary": {
            "primary_blocker": "accepted_model_robustness_not_closed",
            "unresolved_blocker_ids": unresolved_blockers,
            "recovered_nonfinal_ids": recovered_nonfinal,
            "baseline_stitched_pass_count": baseline_summary["stitched_pass_count"],
            "baseline_case_count": baseline_summary["case_count"],
            "positive_matrix_pass_count": positive_summary["matrix_stitched_pass_count"],
            "positive_matrix_case_count": positive_summary["matrix_case_count"],
            "base_z_unresolved_cases": list(base_z_recovery_summary["unresolved_cases"]),
            "positive_failing_scenarios": list(positive_summary["failing_scenarios"]),
        },
        "claim_boundary": {
            "do_not_mark_goal_complete": True,
            "robustness_claim": False,
            "paper_equivalent_feasibility": False,
            "contact_calibration_claim": False,
            "orientation_gate_acceptance": False,
            "hardware_readiness": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "hardware_readiness_claim": False,
        },
        "next_offline_actions": [
            "Choose an accepted robustness matrix tied to the current claim scope before upgrading diagnostic recoveries.",
            "Resolve the positive +1.0 mm tightened-orientation margin only through calibrated contact/gate evidence or a separately accepted model update.",
            "Continue base-z perturbation work only as diagnostic simulation unless contact geometry is calibrated.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    blockers = payload["blocker_summary"]
    lines = [
        "# Robustness Blockers Audit",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Robustness complete: `{payload['robustness_complete']}`",
        f"- Completion claim allowed: `{payload['completion_claim_allowed']}`",
        f"- Offline-actionable from v95: `{payload['offline_actionable_from_v95']}`",
        f"- Baseline stitched pass count: `{blockers['baseline_stitched_pass_count']} / {blockers['baseline_case_count']}`",
        f"- Positive matrix pass count: `{blockers['positive_matrix_pass_count']} / {blockers['positive_matrix_case_count']}`",
        f"- Primary blocker: `{blockers['primary_blocker']}`",
        f"- Unresolved blockers: `{blockers['unresolved_blocker_ids']}`",
        "",
        "## Claim Boundary",
        "",
        "- This audit is offline simulation bookkeeping only.",
        "- It does not prove robustness, strict paper-equivalent feasibility,",
        "  contact calibration, gate acceptance, or hardware readiness.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "robustness_blockers" / run_id
    )
    if out_dir.exists():
        raise FileExistsError(out_dir)
    out_dir.mkdir(parents=True)

    payload = build_audit()
    payload["audit_run_id"] = run_id
    payload["audit_root"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
