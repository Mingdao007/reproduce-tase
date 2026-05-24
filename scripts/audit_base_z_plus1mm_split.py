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
CASE_NAME = "delta_p1p000mm"
VARIANT = "contact_point"

DEFAULT_EXECUTION_AUDIT = (
    "runs/failed_diagnostic_robustness_experiment_audit/20260525T061328/metrics.yaml"
)
DEFAULT_EXACT_METRICS = (
    "runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/"
    "experiments/base_z_plus1mm/metrics.yaml"
)
DEFAULT_START_METRICS = "runs/positive_base_z_start_contact/20260524T170350/metrics.yaml"
DEFAULT_TERMINAL_METRICS = "runs/positive_terminal_orientation/20260524T171705/metrics.yaml"
DEFAULT_RELAXED_METRICS = "runs/positive_relaxed_orientation_recovery/20260524T172909/metrics.yaml"


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_git_state(out_dir: pathlib.Path, *, command: list[str]) -> None:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
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


def case_by_name(metrics: dict[str, Any], case_name: str) -> dict[str, Any]:
    for case in metrics["cases"]:
        if case["case"] == case_name:
            return case
    raise KeyError(case_name)


def terminal_case(metrics: dict[str, Any], case_name: str, variant: str) -> dict[str, Any]:
    for case in metrics["cases"]:
        if case["case"] == case_name and case["variant"] == variant:
            return case
    raise KeyError(f"{variant}/{case_name}")


def execution_cell(execution_audit: dict[str, Any], cell_id: str) -> dict[str, Any]:
    for cell in execution_audit["cell_results"]:
        if cell["cell_id"] == cell_id:
            return cell
    raise KeyError(cell_id)


def gate_margin(value: float, gate: float) -> float:
    return float(gate) - float(value)


def handoff_count(row: dict[str, Any]) -> str:
    return f"{int(row['handoff_pass_count'])}/{int(row['handoff_trajectory_count'])}"


def classify_split(facts: dict[str, Any]) -> dict[str, Any]:
    exact_gate = float(facts["exact_orientation_gate_rad"])
    relaxed_gate = float(facts["relaxed_gate_rad"])
    orientation = float(facts["terminal_orientation_error_rad"])
    start_contact_is_local_seed_limited = (
        not bool(facts["exact_start_passed"]) and bool(facts["broader_start_search_passed"])
    )
    terminal_path_are_gate_limited = (
        bool(facts["terminal_force_xy_contact_passed"])
        and not bool(facts["terminal_diagnostic_passed"])
        and orientation > exact_gate
        and bool(facts["relaxed_terminal_passed"])
        and orientation <= relaxed_gate
        and bool(facts["relaxed_path_passed"])
    )
    stage_a_path_recovered_under_relaxed_gate = (
        bool(facts["broader_start_search_passed"])
        and bool(facts["relaxed_terminal_passed"])
        and bool(facts["relaxed_path_passed"])
    )
    stage_b_handoff_remains_blocked = (
        stage_a_path_recovered_under_relaxed_gate and not bool(facts["relaxed_stitched_recovered"])
    )
    return {
        "classification": "start_seed_terminal_gate_limited_stage_a_with_stage_b_handoff_unresolved",
        "start_contact_is_local_seed_limited": start_contact_is_local_seed_limited,
        "terminal_path_are_gate_limited": terminal_path_are_gate_limited,
        "stage_a_path_recovered_under_relaxed_gate": stage_a_path_recovered_under_relaxed_gate,
        "stage_b_handoff_remains_blocked": stage_b_handoff_remains_blocked,
        "failed_cell_closed": False,
        "canonical_orientation_gate_change_accepted": False,
        "canonical_config_change_accepted": False,
        "robustness_claim": False,
    }


def build_payload(
    *,
    execution_audit_path: pathlib.Path,
    exact_metrics_path: pathlib.Path,
    start_metrics_path: pathlib.Path,
    terminal_metrics_path: pathlib.Path,
    relaxed_metrics_path: pathlib.Path,
) -> dict[str, Any]:
    execution_audit = load_yaml(execution_audit_path)
    exact_metrics = load_yaml(exact_metrics_path)
    start_metrics = load_yaml(start_metrics_path)
    terminal_metrics = load_yaml(terminal_metrics_path)
    relaxed_metrics = load_yaml(relaxed_metrics_path)

    cell = execution_cell(execution_audit, "base_z_plus1mm")
    exact_case = case_by_name(exact_metrics, CASE_NAME)
    start_case = case_by_name(start_metrics, CASE_NAME)
    terminal = terminal_case(terminal_metrics, CASE_NAME, VARIANT)
    relaxed_case = case_by_name(relaxed_metrics, CASE_NAME)

    exact_gate = float(exact_metrics["diagnostic_gate"]["max_terminal_orientation_error_rad"])
    relaxed_gate = float(relaxed_metrics["diagnostic_gate"]["max_terminal_orientation_error_rad"])
    orientation = float(terminal["full_rotation_error_rad"])
    relaxed_durations = list(relaxed_case["durations"])
    relaxed_stitched_recovered = any(bool(row["stitched_passed"]) for row in relaxed_durations)
    handoff_counts = [handoff_count(row) for row in relaxed_durations]

    facts = {
        "exact_orientation_gate_rad": exact_gate,
        "relaxed_gate_rad": relaxed_gate,
        "terminal_orientation_error_rad": orientation,
        "exact_start_passed": bool(exact_case["start"]["passed"]),
        "broader_start_search_passed": bool(start_case["start_search"]["passed"]),
        "terminal_force_xy_contact_passed": bool(terminal["force_xy_contact_passed"]),
        "terminal_diagnostic_passed": bool(terminal["diagnostic_passed"]),
        "relaxed_terminal_passed": bool(relaxed_case["terminal"]["passed"]),
        "relaxed_path_passed": bool(relaxed_case["path"]["path_gate_passed"]),
        "relaxed_stitched_recovered": relaxed_stitched_recovered,
    }
    split = classify_split(facts)

    payload = {
        "run_source": "v108 base_z_plus1mm start-contact terminal-orientation split",
        "source_files": {
            "execution_audit": str(execution_audit_path),
            "exact_base_z_plus1mm": str(exact_metrics_path),
            "positive_base_z_start_contact": str(start_metrics_path),
            "positive_terminal_orientation": str(terminal_metrics_path),
            "positive_relaxed_orientation_recovery": str(relaxed_metrics_path),
        },
        "case": CASE_NAME,
        "variant": VARIANT,
        "base_z_offset_delta_m": float(exact_case["base_z_offset_delta_m"]),
        "base_z_offset_delta_mm": float(exact_case["base_z_offset_delta_mm"]),
        "exact_planned_cell": {
            "status": cell["status"],
            "closure_passed": bool(cell["closure_passed"]),
            "observed_status": cell["observed_status"],
            "planned_parameters_match": bool(
                cell["closure_checks"]["planned_parameters_match"]["all_matched"]
            ),
            "start_passed": bool(exact_case["start"]["passed"]),
            "start_failed_criteria": list(exact_case["start"]["failed_criteria"]),
            "terminal_passed": bool(exact_case["terminal"]["passed"]),
            "terminal_failed_criteria": list(exact_case["terminal"]["failed_criteria"]),
            "path_recovered": exact_case["path"] is not None,
            "duration_recovered_count": len(exact_case["durations"]),
            "diagnostic_orientation_gate_rad": exact_gate,
        },
        "broader_start_search": {
            "passed": bool(start_case["start_search"]["passed"]),
            "pass_count": int(start_case["start_search"]["pass_count"]),
            "candidate_count": int(start_case["start_search"]["candidate_count"]),
            "contact_candidate_count": int(start_case["start_search"]["contact_candidate_count"]),
            "best_seed": start_case["start_search"]["best_seed"],
            "force_error_N": float(start_case["start_search"]["best_force_error_N"]),
            "tangential_error_m": float(start_case["start_search"]["best_tangential_error_m"]),
            "target_contact_count": int(start_case["start_search"]["best_target_contact_count"]),
            "failed_criteria": list(start_case["start_search"]["best_failed_criteria"]),
        },
        "terminal_orientation": {
            "force_xy_contact_passed": bool(terminal["force_xy_contact_passed"]),
            "diagnostic_passed": bool(terminal["diagnostic_passed"]),
            "force_normal_only_passed": bool(terminal["force_normal_only_passed"]),
            "full_rotation_error_rad": orientation,
            "force_normal_only_error_rad": float(terminal["force_normal_only_error_rad"]),
            "full_minus_force_normal_abs_rad": float(terminal["full_minus_force_normal_abs_rad"]),
            "orientation_excess_over_exact_gate_rad": orientation - exact_gate,
            "orientation_margin_to_relaxed_gate_rad": gate_margin(orientation, relaxed_gate),
            "threshold_eval": terminal["threshold_eval"],
        },
        "relaxed_gate_recovery": {
            "relaxed_gate_rad": relaxed_gate,
            "terminal_solver_orientation_threshold_rad": float(
                relaxed_metrics["terminal_solver_orientation_threshold_rad"]
            ),
            "start_passed": bool(relaxed_case["start"]["passed"]),
            "terminal_passed": bool(relaxed_case["terminal"]["passed"]),
            "path_passed": bool(relaxed_case["path"]["path_gate_passed"]),
            "path_min_duration_s": float(relaxed_case["path"]["min_duration_s"]),
            "path_max_abs_qdot_rad_s": float(relaxed_case["path"]["max_abs_qdot_rad_s"]),
            "path_target_contact_present_fraction": float(
                relaxed_case["path"]["target_contact_present_fraction"]
            ),
            "path_max_force_error_N": float(relaxed_case["path"]["max_force_error_N"]),
            "path_max_scheduled_xy_error_m": float(
                relaxed_case["path"]["max_scheduled_xy_error_m"]
            ),
            "path_max_scheduled_orientation_error_rad": float(
                relaxed_case["path"]["max_scheduled_orientation_error_rad"]
            ),
            "stitched_recovered": relaxed_stitched_recovered,
            "duration_rows": [
                {
                    "stage_a_duration_s": float(row["stage_a_duration_s"]),
                    "stitched_ran": bool(row["stitched_ran"]),
                    "stitched_passed": bool(row["stitched_passed"]),
                    "stage_a_passed": bool(row["stage_a_passed"]),
                    "handoff_pass_count": int(row["handoff_pass_count"]),
                    "handoff_trajectory_count": int(row["handoff_trajectory_count"]),
                    "handoff_count": handoff_count(row),
                    "stage_a_max_qdot_rad_s": float(row["stage_a_max_qdot_rad_s"]),
                    "stage_a_terminal_force_error_N": float(
                        row["stage_a_terminal_force_error_N"]
                    ),
                }
                for row in relaxed_durations
            ],
        },
        "summary": {
            "base_z_offset_delta_mm": float(exact_case["base_z_offset_delta_mm"]),
            "exact_planned_cell_status": cell["status"],
            "exact_observed_status": cell["observed_status"],
            "exact_closure_passed": bool(cell["closure_passed"]),
            "exact_start_passed": bool(exact_case["start"]["passed"]),
            "broader_start_search_passed": bool(start_case["start_search"]["passed"]),
            "start_contact_is_local_seed_limited": split[
                "start_contact_is_local_seed_limited"
            ],
            "terminal_force_xy_contact_passed": bool(terminal["force_xy_contact_passed"]),
            "terminal_diagnostic_passed": bool(terminal["diagnostic_passed"]),
            "terminal_orientation_error_rad": orientation,
            "exact_orientation_gate_rad": exact_gate,
            "orientation_excess_over_exact_gate_rad": orientation - exact_gate,
            "relaxed_gate_rad": relaxed_gate,
            "relaxed_gate_margin_rad": gate_margin(orientation, relaxed_gate),
            "relaxed_terminal_passed": bool(relaxed_case["terminal"]["passed"]),
            "relaxed_path_passed": bool(relaxed_case["path"]["path_gate_passed"]),
            "relaxed_path_min_duration_s": float(relaxed_case["path"]["min_duration_s"]),
            "relaxed_stitched_recovered": relaxed_stitched_recovered,
            "relaxed_stage_b_handoff_pass_counts": handoff_counts,
            "split_classification": split["classification"],
            "terminal_path_are_gate_limited": split["terminal_path_are_gate_limited"],
            "stage_a_path_recovered_under_relaxed_gate": split[
                "stage_a_path_recovered_under_relaxed_gate"
            ],
            "stage_b_handoff_remains_blocked": split["stage_b_handoff_remains_blocked"],
            "failed_cell_closed": split["failed_cell_closed"],
            "canonical_orientation_gate_change_accepted": split[
                "canonical_orientation_gate_change_accepted"
            ],
        },
        "claim_boundary": {
            "post_hoc_offline_audit_only": True,
            "failed_cell_closed": False,
            "canonical_orientation_gate_change": False,
            "canonical_config_change": False,
            "robustness_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "contact_calibration_claim": False,
            "hardware_readiness": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
        },
        "next_offline_actions": [
            "Do not mark base_z_plus1mm closed from this split audit.",
            "Keep the 0.12 rad orientation envelope run-local unless a separate gate acceptance decision exists.",
            "Treat the start-contact miss as local seed-limited, not a fundamental positive base-z contact impossibility.",
            "Treat terminal/path recovery as orientation-gate limited under the current contact-point model.",
            "Treat stitched recovery as still blocked by Stage B handoff timing/qdot margin.",
        ],
        "warnings": [
            "post-hoc offline audit of existing metrics only",
            "does not rerun MuJoCo or change controller defaults",
            "does not accept a replacement orientation gate",
            "does not change canonical configs",
            "does not calibrate contact geometry or force frames",
            "not strict paper-equivalent feasibility",
            "not a robustness proof",
            "not hardware-ready",
        ],
    }
    return payload


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Base-Z Plus1mm Split Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Exact planned cell status: `{summary['exact_planned_cell_status']}`",
        f"- Exact closure passed: `{summary['exact_closure_passed']}`",
        f"- Broader start search passed: `{summary['broader_start_search_passed']}`",
        f"- Terminal force/x-y/contact passed: `{summary['terminal_force_xy_contact_passed']}`",
        f"- Terminal diagnostic orientation passed: `{summary['terminal_diagnostic_passed']}`",
        f"- Terminal orientation: `{summary['terminal_orientation_error_rad']}` rad",
        f"- Exact gate: `{summary['exact_orientation_gate_rad']}` rad",
        f"- Relaxed gate margin: `{summary['relaxed_gate_margin_rad']}` rad",
        f"- Relaxed path passed: `{summary['relaxed_path_passed']}`",
        f"- Relaxed stitched recovered: `{summary['relaxed_stitched_recovered']}`",
        f"- Failed cell closed: `{summary['failed_cell_closed']}`",
        "",
        "| evidence slice | pass | key value | interpretation |",
        "| --- | --- | ---: | --- |",
        (
            f"| exact start | `{summary['exact_start_passed']}` | "
            f"`{payload['exact_planned_cell']['start_failed_criteria']}` | "
            "`planned seed misses contact` |"
        ),
        (
            f"| broader start | `{summary['broader_start_search_passed']}` | "
            f"`{payload['broader_start_search']['force_error_N']}` N | "
            "`start contact is local seed-limited` |"
        ),
        (
            f"| terminal force/x-y/contact | `{summary['terminal_force_xy_contact_passed']}` | "
            f"`{payload['terminal_orientation']['full_minus_force_normal_abs_rad']}` rad yaw gap | "
            "`not a force/x-y/contact failure` |"
        ),
        (
            f"| terminal orientation gate | `{summary['terminal_diagnostic_passed']}` | "
            f"`{summary['orientation_excess_over_exact_gate_rad']}` rad excess | "
            "`0.08 rad gate blocks terminal/path` |"
        ),
        (
            f"| relaxed Stage A/path | `{summary['stage_a_path_recovered_under_relaxed_gate']}` | "
            f"`{summary['relaxed_path_min_duration_s']}` s | "
            "`run-local 0.12 rad gate recovers endpoint/path` |"
        ),
        (
            f"| relaxed stitched | `{summary['relaxed_stitched_recovered']}` | "
            f"`{', '.join(summary['relaxed_stage_b_handoff_pass_counts'])}` | "
            "`Stage B handoff remains blocked` |"
        ),
        "",
        "Interpretation:",
        "",
        "- The exact v99 `base_z_plus1mm` command remains executed-unresolved.",
        "- The start-contact miss is not fundamental for `+1.0 mm`; broader seeds recover a 5 N target-pair contact.",
        "- The terminal/path blocker is the current `0.08 rad` orientation gate under the contact-point model, not force, x/y, contact count, or yaw handling.",
        "- The run-local `0.12 rad` gate recovers Stage A endpoint/path evidence, but stitched Stage B still fails, so no failed cell is closed.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution-audit", default=DEFAULT_EXECUTION_AUDIT)
    parser.add_argument("--exact-metrics", default=DEFAULT_EXACT_METRICS)
    parser.add_argument("--start-metrics", default=DEFAULT_START_METRICS)
    parser.add_argument("--terminal-metrics", default=DEFAULT_TERMINAL_METRICS)
    parser.add_argument("--relaxed-metrics", default=DEFAULT_RELAXED_METRICS)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "base_z_plus1mm_split" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(
        execution_audit_path=(ROOT / args.execution_audit).resolve(),
        exact_metrics_path=(ROOT / args.exact_metrics).resolve(),
        start_metrics_path=(ROOT / args.start_metrics).resolve(),
        terminal_metrics_path=(ROOT / args.terminal_metrics).resolve(),
        relaxed_metrics_path=(ROOT / args.relaxed_metrics).resolve(),
    )
    payload["run_id"] = run_id
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
