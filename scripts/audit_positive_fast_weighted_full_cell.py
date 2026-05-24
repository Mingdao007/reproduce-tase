#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from audit_stage_a_base_z_recovery import run_child, write_git_state
from tase_repro.base_z_recovery import base_z_delta_label


TRAJECTORY_ORDER = ["e1-cycloid", "e2-figure-eight", "e3-circle", "e4-cardioid"]

SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "linear_kp0_normal1",
        "orientation_priority_mode": "linear_primary",
        "orientation_kp": 0.0,
        "normal_axis_weight": 1.0,
        "description": "v101/v105 linear-primary failed-cell baseline.",
    },
    {
        "name": "weighted_kp0_normal1",
        "orientation_priority_mode": "weighted",
        "orientation_kp": 0.0,
        "normal_axis_weight": 1.0,
        "description": "v82/v106 weighted zero-angular-command candidate.",
    },
    {
        "name": "weighted_kp0_normal30",
        "orientation_priority_mode": "weighted",
        "orientation_kp": 0.0,
        "normal_axis_weight": 30.0,
        "description": "v82/v106 weighted candidate with normal weight 30.",
    },
]


def full_cell_command(
    *,
    out_dir: pathlib.Path,
    source_run: pathlib.Path,
    delta_m: float,
    stage_a_duration_s: float,
    paper_time_scale: float,
    qdot_limit_rad_s: float,
    max_orientation_error_rad: float,
    scenario: dict[str, Any],
) -> list[str]:
    case_name = base_z_delta_label(delta_m)
    return [
        sys.executable,
        str(ROOT / "scripts" / "evaluate_stitched_stage_a_handoff.py"),
        "--output-dir",
        str(out_dir),
        "--stage-a-target-config",
        str(source_run / "relaxed_stage_a_target_config.yaml"),
        "--source-path-csv",
        str(source_run / "cases" / case_name / "path" / "path.csv"),
        "--base-z-offset-delta-m",
        f"{float(delta_m):.17g}",
        "--stage-a-duration-s",
        f"{float(stage_a_duration_s):.17g}",
        "--paper-time-scale",
        f"{float(paper_time_scale):.17g}",
        "--qdot-limit-rad-s",
        f"{float(qdot_limit_rad_s):.17g}",
        "--max-orientation-error-rad",
        f"{float(max_orientation_error_rad):.17g}",
        "--orientation-priority-mode",
        str(scenario["orientation_priority_mode"]),
        "--orientation-kp",
        f"{float(scenario['orientation_kp']):.17g}",
        "--normal-axis-weight",
        f"{float(scenario['normal_axis_weight']):.17g}",
        "--trajectories",
        ",".join(TRAJECTORY_ORDER),
    ]


def summarize_row(row: dict[str, Any]) -> dict[str, Any]:
    gate = row["feasibility_gate"]
    metrics = row["target_pair_metrics"]
    return {
        "trajectory": str(row["trajectory"]),
        "passed": bool(gate["feasibility_pass"]),
        "failed_criteria": list(gate["failed_criteria"]),
        "orientation_error_rad": float(metrics["max_orientation_error_rad"]),
        "qdot_saturation_fraction": float(metrics["qdot_saturation_fraction"]),
        "tail_max_qdot_utilization": float(metrics["tail_max_qdot_utilization"]),
        "max_qdot_utilization": float(metrics["max_qdot_utilization"]),
        "max_abs_qdot_rad_s": float(metrics["max_abs_qdot_rad_s"]),
        "tail_mean_abs_force_error_N": float(metrics["tail_mean_abs_force_error_N"]),
        "max_tangential_position_error_m": float(metrics["max_tangential_position_error_m"]),
        "max_abs_normal_velocity_slack_m_s": float(metrics["max_abs_normal_velocity_slack_m_s"]),
        "max_angular_velocity_slack_rad_s": float(metrics["max_angular_velocity_slack_rad_s"]),
        "contact_present_fraction": float(metrics["contact_present_fraction"]),
    }


def summarize_case(
    *,
    delta_m: float,
    scenario: dict[str, Any],
    metrics: dict[str, Any],
    orientation_gate_rad: float,
) -> dict[str, Any]:
    rows = [summarize_row(row) for row in metrics["stage_b"]["rows"]]
    if [row["trajectory"] for row in rows] != TRAJECTORY_ORDER:
        raise ValueError("unexpected Stage B trajectory order")
    failed_rows = [row for row in rows if not row["passed"]]
    return {
        "scenario": str(scenario["name"]),
        "description": str(scenario["description"]),
        "base_z_offset_delta_m": float(delta_m),
        "base_z_offset_delta_mm": 1000.0 * float(delta_m),
        "orientation_priority_mode": str(scenario["orientation_priority_mode"]),
        "orientation_kp": float(scenario["orientation_kp"]),
        "normal_axis_weight": float(scenario["normal_axis_weight"]),
        "paper_time_scale": float(metrics["paper_time_scale"]),
        "qdot_limit_rad_s": float(metrics["qdot_limit_rad_s"]),
        "stage_a_duration_s": float(metrics["stage_a_duration_s"]),
        "orientation_gate_rad": float(orientation_gate_rad),
        "stage_a_passed": bool(metrics["stage_a"]["stage_a_gate"]["passed"]),
        "stitched_passed": bool(metrics["stitched_gate"]["passed"]),
        "handoff_pass_count": int(metrics["stage_b"]["handoff_pass_count"]),
        "handoff_trajectory_count": int(metrics["stage_b"]["trajectory_count"]),
        "failed_trajectories": [row["trajectory"] for row in failed_rows],
        "failed_criteria_by_trajectory": {
            row["trajectory"]: list(row["failed_criteria"]) for row in failed_rows
        },
        "stage_a_terminal_orientation_error_rad": float(
            metrics["stage_a"]["evaluation"]["terminal_force_normal_orientation_error_rad"]
        ),
        "stage_a_max_qdot_rad_s": float(metrics["stage_a"]["tracking"]["max_abs_qdot_rad_s"]),
        "stage_a_qdot_saturation_fraction": float(metrics["stage_a"]["tracking"]["qdot_saturation_fraction"]),
        "max_stage_b_orientation_error_rad": max(row["orientation_error_rad"] for row in rows),
        "max_stage_b_orientation_excess_over_gate_rad": max(
            row["orientation_error_rad"] - float(orientation_gate_rad) for row in rows
        ),
        "max_stage_b_qdot_saturation_fraction": max(row["qdot_saturation_fraction"] for row in rows),
        "max_stage_b_tail_qdot_utilization": max(row["tail_max_qdot_utilization"] for row in rows),
        "max_stage_b_tail_force_error_N": max(row["tail_mean_abs_force_error_N"] for row in rows),
        "max_stage_b_xy_error_m": max(row["max_tangential_position_error_m"] for row in rows),
        "stage_b_rows": rows,
        "source_path_csv": str(metrics["source_path_csv"]),
    }


def aggregate_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    passing = [case for case in cases if case["stage_a_passed"] and case["stitched_passed"]]
    weighted = [case for case in cases if case["orientation_priority_mode"] == "weighted"]
    weighted_passing = [case for case in weighted if case["stage_a_passed"] and case["stitched_passed"]]
    best_orientation = min(cases, key=lambda case: case["max_stage_b_orientation_error_rad"])
    return {
        "scenario_count": len(cases),
        "passing_scenario_count": len(passing),
        "passing_scenarios": [case["scenario"] for case in passing],
        "failing_scenarios": [case["scenario"] for case in cases if case not in passing],
        "weighted_scenario_count": len(weighted),
        "weighted_passing_count": len(weighted_passing),
        "weighted_passing_scenarios": [case["scenario"] for case in weighted_passing],
        "weighted_candidate_recovered": bool(weighted_passing),
        "all_weighted_candidates_recovered": len(weighted_passing) == len(weighted) and bool(weighted),
        "best_orientation_scenario": best_orientation["scenario"],
        "min_max_stage_b_orientation_error_rad": best_orientation["max_stage_b_orientation_error_rad"],
        "max_stage_b_orientation_error_rad": max(case["max_stage_b_orientation_error_rad"] for case in cases),
        "min_stage_b_qdot_saturation_fraction": min(
            case["max_stage_b_qdot_saturation_fraction"] for case in cases
        ),
        "max_stage_b_qdot_saturation_fraction": max(
            case["max_stage_b_qdot_saturation_fraction"] for case in cases
        ),
        "max_stage_b_tail_qdot_utilization": max(
            case["max_stage_b_tail_qdot_utilization"] for case in cases
        ),
        "min_stage_b_tail_force_error_N": min(case["max_stage_b_tail_force_error_N"] for case in cases),
        "max_stage_b_tail_force_error_N": max(case["max_stage_b_tail_force_error_N"] for case in cases),
        "candidate_closure_boundary": {
            "weighted_full_e1_e4_candidate_recovered": bool(weighted_passing),
            "original_failed_cell_closed": False,
            "canonical_controller_change_accepted": False,
            "reason": (
                "Weighted priority is a diagnostic candidate in this audit; the original "
                "linear-primary failed-cell command remains the canonical v99 execution."
            ),
        },
    }


def failed_rows_text(case: dict[str, Any]) -> str:
    parts = []
    for trajectory, criteria in case["failed_criteria_by_trajectory"].items():
        parts.append(f"{trajectory}:{','.join(criteria)}")
    return "; ".join(parts) or "none"


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    lines = [
        "# Positive Fast Weighted Full-Cell Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Scenario count: `{aggregate['scenario_count']}`",
        f"- Passing scenarios: `{', '.join(aggregate['passing_scenarios']) or 'none'}`",
        f"- Weighted candidate recovered: `{aggregate['weighted_candidate_recovered']}`",
        f"- Original failed cell closed: `{aggregate['candidate_closure_boundary']['original_failed_cell_closed']}`",
        f"- Best orientation scenario: `{aggregate['best_orientation_scenario']}`",
        f"- Minimum max Stage B orientation: `{aggregate['min_max_stage_b_orientation_error_rad']}`",
        "",
        "| scenario | priority | normal weight | stitched | Stage B pass | failed rows | max orientation | qdot sat | tail qdot | force err |",
        "| --- | --- | ---: | --- | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for case in cases:
        lines.append(
            "| `{scenario}` | `{priority}` | `{normal}` | `{stitched}` | `{handoff}/{count}` | `{failed}` | `{orientation}` | `{qdot}` | `{tail_qdot}` | `{force}` |".format(
                scenario=case["scenario"],
                priority=case["orientation_priority_mode"],
                normal=case["normal_axis_weight"],
                stitched=case["stitched_passed"],
                handoff=case["handoff_pass_count"],
                count=case["handoff_trajectory_count"],
                failed=failed_rows_text(case),
                orientation=case["max_stage_b_orientation_error_rad"],
                qdot=case["max_stage_b_qdot_saturation_fraction"],
                tail_qdot=case["max_stage_b_tail_qdot_utilization"],
                force=case["max_stage_b_tail_force_error_N"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- This probe keeps `paper_time_scale = 0.0075`, `qdot_limit = 0.15 rad/s`, and the run-local `0.12 rad` orientation gate fixed.",
            "- Passing weighted rows are full E1-E4 diagnostic recovery candidates for the `+1.0 mm` fast-timing face.",
            "- The original v99 failed cell is not marked closed because this audit does not accept a canonical controller change.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-run",
        default="runs/positive_relaxed_orientation_recovery/20260524T172909",
    )
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--base-z-delta-mm", type=float, default=1.0)
    parser.add_argument("--stage-a-duration-s", type=float, default=15.0)
    parser.add_argument("--paper-time-scale", type=float, default=0.0075)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--max-orientation-error-rad", type=float, default=0.12)
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    delta_m = float(args.base_z_delta_mm) / 1000.0
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "positive_fast_weighted_full_cell" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = []
    for scenario in SCENARIOS:
        scenario_name = str(scenario["name"])
        case_dir = out_dir / "scenarios" / scenario_name
        case_dir.mkdir(parents=True, exist_ok=True)
        metrics = run_child(
            full_cell_command(
                out_dir=case_dir,
                source_run=source_run,
                delta_m=delta_m,
                stage_a_duration_s=args.stage_a_duration_s,
                paper_time_scale=args.paper_time_scale,
                qdot_limit_rad_s=args.qdot_limit_rad_s,
                max_orientation_error_rad=args.max_orientation_error_rad,
                scenario=scenario,
            ),
            out_dir=case_dir,
        )
        cases.append(
            summarize_case(
                delta_m=delta_m,
                scenario=scenario,
                metrics=metrics,
                orientation_gate_rad=args.max_orientation_error_rad,
            )
        )

    aggregate = aggregate_cases(cases)
    payload = {
        "run_id": run_id,
        "source": "v107 positive fast-timing weighted full-cell probe",
        "source_run": str(source_run),
        "relaxed_stage_a_target_config": str(source_run / "relaxed_stage_a_target_config.yaml"),
        "base_z_offset_delta_m": delta_m,
        "base_z_offset_delta_mm": float(args.base_z_delta_mm),
        "stage_a_duration_s": float(args.stage_a_duration_s),
        "stage_b_trajectories": list(TRAJECTORY_ORDER),
        "paper_time_scale": float(args.paper_time_scale),
        "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
        "orientation_gate_rad": float(args.max_orientation_error_rad),
        "scenarios": [dict(scenario) for scenario in SCENARIOS],
        "aggregate": aggregate,
        "cases": cases,
        "claim_boundary": {
            "full_e1_e4_probe": True,
            "weighted_candidate_recovered": bool(aggregate["weighted_candidate_recovered"]),
            "failed_cell_closed": False,
            "canonical_controller_change": False,
            "orientation_gate_relaxed": False,
            "robustness_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "hardware_readiness": False,
        },
        "warnings": [
            "diagnostic-label weighted-priority full-cell probe",
            "does not make weighted priority a canonical controller default",
            "does not change the original v99 executed failed-cell status",
            "not strict paper-equivalent feasibility",
            "not a formal robustness proof",
            "not contact-model calibration",
            "not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    write_summary(out_dir, aggregate, cases)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
