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

PLAN_METRICS = (
    ROOT
    / "runs"
    / "failed_diagnostic_robustness_experiment_matrix"
    / "20260525T053909"
    / "metrics.yaml"
)
EXPERIMENT_ROOT = PLAN_METRICS.parent / "experiments"


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


def command_arg(command: list[str], name: str) -> str | None:
    try:
        return command[command.index(name) + 1]
    except (ValueError, IndexError):
        return None


def parse_float_list(text: str | None) -> list[float] | None:
    if text is None:
        return None
    return [float(part.strip()) for part in text.split(",") if part.strip()]


def parse_str_list(text: str | None) -> list[str] | None:
    if text is None:
        return None
    return [part.strip() for part in text.split(",") if part.strip()]


def planned_base_z_args_match(plan: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    command = list(plan["command"])
    expected_deltas = parse_float_list(command_arg(command, "--base-z-deltas-mm"))
    expected_durations = parse_float_list(command_arg(command, "--stage-a-durations-s"))
    observed_deltas = [float(value) for value in metrics.get("base_z_deltas_mm", [])]
    observed_durations = [float(value) for value in metrics.get("stage_a_durations_s", [])]
    return {
        "base_z_deltas_mm": {
            "planned": expected_deltas,
            "observed": observed_deltas,
            "matched": expected_deltas == observed_deltas,
        },
        "stage_a_durations_s": {
            "planned": expected_durations,
            "observed": observed_durations,
            "matched": expected_durations == observed_durations,
        },
        "all_matched": expected_deltas == observed_deltas
        and expected_durations == observed_durations,
    }


def planned_positive_sensitivity_args_match(
    plan: dict[str, Any],
    metrics: dict[str, Any],
) -> dict[str, Any]:
    command = list(plan["command"])
    expected_deltas = parse_float_list(command_arg(command, "--base-z-deltas-mm"))
    expected_scenarios = parse_str_list(command_arg(command, "--scenarios"))
    observed_deltas = sorted(
        {
            float(case["base_z_offset_delta_mm"])
            for scenario in metrics.get("scenarios", [])
            for case in scenario.get("cases", [])
        }
    )
    observed_scenarios = [str(item["scenario"]) for item in metrics.get("scenarios", [])]
    return {
        "base_z_deltas_mm": {
            "planned": expected_deltas,
            "observed": observed_deltas,
            "matched": expected_deltas == observed_deltas,
        },
        "scenarios": {
            "planned": expected_scenarios,
            "observed": observed_scenarios,
            "matched": expected_scenarios == observed_scenarios,
        },
        "all_matched": expected_deltas == observed_deltas
        and expected_scenarios == observed_scenarios,
    }


def evaluate_base_z_plus1mm(plan: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    aggregate = metrics["aggregate"]
    cases = metrics["cases"]
    case = next(item for item in cases if item["case"] == "delta_p1p000mm")
    start_passed = bool(case["start"]["passed"])
    terminal_passed = bool(case["terminal"]["passed"])
    path_passed = bool(case["path"] and case["path"]["path_gate_passed"])
    duration_recovered = any(item["stitched_passed"] for item in case["durations"])
    closure_checks = {
        "planned_parameters_match": planned_base_z_args_match(plan, metrics),
        "source_delta_present": {
            "passed": case["base_z_offset_delta_mm"] == 1.0,
            "observed_base_z_offset_delta_mm": case["base_z_offset_delta_mm"],
        },
        "start_contact_recovered": {
            "passed": start_passed,
            "failed_criteria": list(case["start"]["failed_criteria"]),
        },
        "terminal_target_recovered": {
            "passed": terminal_passed,
            "failed_criteria": list(case["terminal"]["failed_criteria"]),
            "orientation_error_rad": float(case["terminal"]["orientation_error_rad"]),
        },
        "path_geometry_recovered": {
            "passed": path_passed,
            "path_summary": case["path"],
        },
        "duration_recovered": {
            "passed": duration_recovered,
            "tested_stage_a_durations_s": list(metrics["stage_a_durations_s"]),
            "duration_rows": list(case["durations"]),
        },
    }
    closure_passed = all(
        [
            closure_checks["planned_parameters_match"]["all_matched"],
            closure_checks["source_delta_present"]["passed"],
            start_passed,
            terminal_passed,
            path_passed,
            duration_recovered,
        ]
    )
    return {
        "cell_id": "base_z_plus1mm",
        "status": "executed_closed" if closure_passed else "executed_unresolved",
        "closure_passed": closure_passed,
        "closure_checks": closure_checks,
        "observed_status": case["status"],
        "aggregate": {
            "case_count": int(aggregate["case_count"]),
            "start_pass_count": int(aggregate["start_pass_count"]),
            "terminal_pass_count": int(aggregate["terminal_pass_count"]),
            "path_geometry_pass_count": int(aggregate["path_geometry_pass_count"]),
            "duration_recovered_count": int(aggregate["duration_recovered_count"]),
            "max_positive_terminal_pass_delta_mm": aggregate["max_positive_terminal_pass_delta_mm"],
            "max_positive_recovered_delta_mm": aggregate["max_positive_recovered_delta_mm"],
        },
        "interpretation": (
            "The +1.0 mm base-z failed cell remains unresolved because the exact "
            "planned command did not recover start contact, terminal feasibility, "
            "path geometry, or any tested Stage A duration."
        ),
    }


def evaluate_positive_fast_timing_0p0075(
    plan: dict[str, Any],
    metrics: dict[str, Any],
) -> dict[str, Any]:
    aggregate = metrics["aggregate"]
    scenario = next(
        item for item in metrics["scenarios"] if item["scenario"] == "paper_time_scale_0p0075"
    )
    case = next(item for item in scenario["cases"] if item["case"] == "delta_p1p000mm")
    failed_rows = list(case["stage_b_failed_rows"])
    stitched_passed = bool(case["stitched_passed"])
    handoff_all_passed = int(case["handoff_pass_count"]) == int(case["handoff_trajectory_count"])
    no_stage_b_failures = not failed_rows
    qdot_saturation_clear = float(case["stage_b_max_qdot_saturation_fraction"]) == 0.0
    tail_qdot_clear = float(case["stage_b_max_tail_qdot_utilization"]) <= 1.0 and no_stage_b_failures
    orientation_clear = float(case["stage_b_max_orientation_error_rad"]) <= float(
        scenario["parameters"]["max_orientation_error_rad"]
    )
    closure_checks = {
        "planned_parameters_match": planned_positive_sensitivity_args_match(plan, metrics),
        "source_delta_present": {
            "passed": case["base_z_offset_delta_mm"] == 1.0,
            "observed_base_z_offset_delta_mm": case["base_z_offset_delta_mm"],
        },
        "scenario_present": {
            "passed": scenario["scenario"] == "paper_time_scale_0p0075",
            "observed_scenario": scenario["scenario"],
        },
        "stage_a_recovered": {
            "passed": bool(case["stage_a_passed"]) and not case["stage_a_failed_criteria"],
            "stage_a_passed": bool(case["stage_a_passed"]),
            "stage_a_failed_criteria": list(case["stage_a_failed_criteria"]),
        },
        "stitched_recovered": {
            "passed": stitched_passed,
            "handoff_pass_count": int(case["handoff_pass_count"]),
            "handoff_trajectory_count": int(case["handoff_trajectory_count"]),
        },
        "stage_b_all_rows_passed": {
            "passed": handoff_all_passed and no_stage_b_failures,
            "failed_rows": failed_rows,
        },
        "qdot_saturation_clear": {
            "passed": qdot_saturation_clear,
            "stage_b_max_qdot_saturation_fraction": float(
                case["stage_b_max_qdot_saturation_fraction"]
            ),
        },
        "tail_qdot_utilization_clear": {
            "passed": tail_qdot_clear,
            "stage_b_max_tail_qdot_utilization": float(case["stage_b_max_tail_qdot_utilization"]),
        },
        "orientation_gate_clear": {
            "passed": orientation_clear,
            "stage_b_max_orientation_error_rad": float(case["stage_b_max_orientation_error_rad"]),
            "max_orientation_error_rad": float(scenario["parameters"]["max_orientation_error_rad"]),
        },
    }
    closure_passed = all(
        [
            closure_checks["planned_parameters_match"]["all_matched"],
            closure_checks["source_delta_present"]["passed"],
            closure_checks["scenario_present"]["passed"],
            closure_checks["stage_a_recovered"]["passed"],
            closure_checks["stitched_recovered"]["passed"],
            closure_checks["stage_b_all_rows_passed"]["passed"],
            closure_checks["qdot_saturation_clear"]["passed"],
            closure_checks["tail_qdot_utilization_clear"]["passed"],
            closure_checks["orientation_gate_clear"]["passed"],
        ]
    )
    return {
        "cell_id": "positive_fast_timing_0p0075",
        "status": "executed_closed" if closure_passed else "executed_unresolved",
        "closure_passed": closure_passed,
        "closure_checks": closure_checks,
        "observed_status": "stitched_passed" if stitched_passed else "stitched_failed",
        "aggregate": {
            "scenario_count": int(aggregate["scenario_count"]),
            "matrix_case_count": int(aggregate["matrix_case_count"]),
            "matrix_stitched_pass_count": int(aggregate["matrix_stitched_pass_count"]),
            "matrix_stitched_fail_count": int(aggregate["matrix_stitched_fail_count"]),
            "scenario_all_pass_count": int(aggregate["scenario_all_pass_count"]),
            "failing_scenarios": list(aggregate["failing_scenarios"]),
            "all_scenarios_passed": bool(aggregate["all_scenarios_passed"]),
        },
        "interpretation": (
            "The +1.0 mm positive fast-timing cell remains unresolved because "
            "Stage A passes but the stitched Stage B handoff fails E2 on qdot "
            "saturation, tail qdot utilization, and orientation."
        ),
    }


def evaluate_cell(plan: dict[str, Any], experiment_root: pathlib.Path) -> dict[str, Any]:
    cell_id = str(plan["id"])
    metrics_path = experiment_root / cell_id / "metrics.yaml"
    if not metrics_path.exists():
        return {
            "cell_id": cell_id,
            "status": "not_executed",
            "closure_passed": False,
            "experiment_metrics": None,
            "source_failed_cell": dict(plan["source_failed_cell"]),
            "interpretation": "No experiment metrics exist for this planned cell.",
        }

    metrics = load_yaml(metrics_path)
    if cell_id == "base_z_plus1mm":
        result = evaluate_base_z_plus1mm(plan, metrics)
    elif cell_id == "positive_fast_timing_0p0075":
        result = evaluate_positive_fast_timing_0p0075(plan, metrics)
    else:
        result = {
            "cell_id": cell_id,
            "status": "executed_not_evaluated",
            "closure_passed": False,
            "interpretation": "This audit currently evaluates only the base_z_plus1mm cell.",
        }
    result["experiment_metrics"] = relative(metrics_path)
    result["source_failed_cell"] = dict(plan["source_failed_cell"])
    return result


def build_audit(
    *,
    run_id: str,
    plan_metrics_path: pathlib.Path,
    experiment_root: pathlib.Path,
) -> dict[str, Any]:
    plan_metrics = load_yaml(plan_metrics_path)
    cell_results = [
        evaluate_cell(item, experiment_root)
        for item in plan_metrics["experiments"]
    ]
    status_counts: dict[str, int] = {}
    for result in cell_results:
        status_counts[result["status"]] = status_counts.get(result["status"], 0) + 1
    closed = [item["cell_id"] for item in cell_results if item["closure_passed"]]
    unresolved = [
        item["cell_id"]
        for item in cell_results
        if item["status"] in {"executed_unresolved", "executed_not_evaluated"}
    ]
    not_executed = [item["cell_id"] for item in cell_results if item["status"] == "not_executed"]
    return {
        "audit_source": "v101 failed diagnostic robustness experiment execution audit",
        "run_id": run_id,
        "status": "completed",
        "source_files": {
            "planned_experiment_matrix": relative(plan_metrics_path),
            "experiment_root": relative(experiment_root),
        },
        "cell_results": cell_results,
        "summary": {
            "cell_count": len(cell_results),
            "status_counts": status_counts,
            "closed_cell_ids": closed,
            "unresolved_executed_cell_ids": unresolved,
            "not_executed_cell_ids": not_executed,
            "executed_cell_count": sum(
                1 for item in cell_results if item["status"] != "not_executed"
            ),
            "closed_cell_count": len(closed),
            "not_executed_cell_count": len(not_executed),
            "all_failed_cells_closed": len(closed) == len(cell_results),
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
            "Do not upgrade the base_z_plus1mm cell; it remains unresolved under the executed command.",
            "Do not upgrade the positive_fast_timing_0p0075 cell; it remains unresolved under the executed command.",
            "If continuing offline, run one of the remaining planned commands or design narrower probes for the unresolved +1.0 mm rows.",
            "Keep contact-model and gate interpretations blocked until approved read-only evidence exists.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Failed Diagnostic Robustness Experiment Execution Audit",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Status: `{payload['status']}`",
        f"- Executed cell count: `{summary['executed_cell_count']}`",
        f"- Closed cell count: `{summary['closed_cell_count']}`",
        f"- Not-executed cell count: `{summary['not_executed_cell_count']}`",
        f"- All failed cells closed: `{summary['all_failed_cells_closed']}`",
        "",
        "| cell | status | closure passed | metrics |",
        "| --- | --- | --- | --- |",
    ]
    for item in payload["cell_results"]:
        lines.append(
            f"| `{item['cell_id']}` | `{item['status']}` | "
            f"`{item['closure_passed']}` | `{item['experiment_metrics']}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- This audit compares offline experiment output to the v99 failed-cell closure criteria.",
            "- It does not prove robustness, accept a gate, calibrate contact geometry,",
            "  authorize hardware, or mark the goal complete.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan-metrics", default=str(PLAN_METRICS))
    parser.add_argument("--experiment-root", default=str(EXPERIMENT_ROOT))
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "failed_diagnostic_robustness_experiment_audit" / run_id
    )
    if out_dir.exists():
        raise FileExistsError(out_dir)
    out_dir.mkdir(parents=True)

    payload = build_audit(
        run_id=run_id,
        plan_metrics_path=pathlib.Path(args.plan_metrics),
        experiment_root=pathlib.Path(args.experiment_root),
    )
    payload["audit_root"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
