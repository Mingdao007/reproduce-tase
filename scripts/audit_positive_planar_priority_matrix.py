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
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from audit_positive_stitched_sensitivity import summarize_case
from audit_stage_a_base_z_bracket import parse_float_list
from audit_stage_a_base_z_recovery import run_child, write_git_state
from audit_stage_b_priority_recovery import (
    handoff_posture_text,
    stage_b_rows,
    stitched_command,
    write_stage_a_config,
)


TRAJECTORY_ORDER = ["e1-cycloid", "e2-figure-eight", "e3-circle", "e4-cardioid"]

SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "planar_normal30_kp0p001",
        "orientation_priority_mode": "planar_primary",
        "orientation_kp": 0.001,
        "normal_axis_weight": 30.0,
        "description": "v79 lower-gain passing planar-primary recovery candidate.",
    },
    {
        "name": "planar_normal30_kp0p002",
        "orientation_priority_mode": "planar_primary",
        "orientation_kp": 0.002,
        "normal_axis_weight": 30.0,
        "description": "v79 higher-gain passing planar-primary recovery candidate.",
    },
]


def aggregate_scenario_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    passed = [case for case in cases if case["stitched_passed"]]
    failed = [case for case in cases if not case["stitched_passed"]]
    passed_deltas = [case["base_z_offset_delta_mm"] for case in passed]
    return {
        "case_count": len(cases),
        "stitched_pass_count": len(passed),
        "stitched_fail_count": len(failed),
        "all_cases_passed": len(passed) == len(cases) and bool(cases),
        "passing_cases": [case["case"] for case in passed],
        "failing_cases": [case["case"] for case in failed],
        "max_positive_stitched_pass_delta_mm": max(passed_deltas) if passed_deltas else None,
        "stage_a_all_passed": all(case["stage_a_passed"] for case in cases),
        "max_stage_b_orientation_error_rad": max(case["stage_b_max_orientation_error_rad"] for case in cases),
        "max_stage_b_qdot_saturation_fraction": max(
            case["stage_b_max_qdot_saturation_fraction"] for case in cases
        ),
        "max_stage_b_tail_qdot_utilization": max(case["stage_b_max_tail_qdot_utilization"] for case in cases),
        "max_stage_b_tail_force_error_N": max(case["stage_b_max_tail_force_error_N"] for case in cases),
        "max_stage_b_xy_error_m": max(case["stage_b_max_xy_error_m"] for case in cases),
        "max_stage_a_terminal_orientation_error_rad": max(
            case["stage_a_terminal_orientation_error_rad"] for case in cases
        ),
    }


def aggregate_all(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "scenario_count": len(scenarios),
        "case_count": sum(scenario["aggregate"]["case_count"] for scenario in scenarios),
        "stitched_pass_count": sum(scenario["aggregate"]["stitched_pass_count"] for scenario in scenarios),
        "stitched_fail_count": sum(scenario["aggregate"]["stitched_fail_count"] for scenario in scenarios),
        "all_scenarios_all_cases_passed": all(scenario["aggregate"]["all_cases_passed"] for scenario in scenarios),
        "passing_scenarios": [
            scenario["name"] for scenario in scenarios if scenario["aggregate"]["all_cases_passed"]
        ],
    }


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], scenarios: list[dict[str, Any]]) -> None:
    lines = [
        "# Positive Planar-Priority Matrix Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Scenario count: `{aggregate['scenario_count']}`",
        f"- Total case count: `{aggregate['case_count']}`",
        f"- Total stitched pass count: `{aggregate['stitched_pass_count']} / {aggregate['case_count']}`",
        f"- All scenarios pass all cases: `{aggregate['all_scenarios_all_cases_passed']}`",
        f"- Passing scenarios: `{', '.join(aggregate['passing_scenarios']) or 'none'}`",
        "",
        "## Scenario Aggregates",
        "",
        "| scenario | stitched pass | max pass delta mm | Stage A all pass | max orientation | max qdot sat | max tail qdot | max force err |",
        "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for scenario in scenarios:
        scenario_agg = scenario["aggregate"]
        lines.append(
            "| `{name}` | `{passed}/{count}` | `{delta}` | `{stage_a}` | `{orientation}` | `{qdot}` | `{tail_qdot}` | `{force}` |".format(
                name=scenario["name"],
                passed=scenario_agg["stitched_pass_count"],
                count=scenario_agg["case_count"],
                delta=scenario_agg["max_positive_stitched_pass_delta_mm"],
                stage_a=scenario_agg["stage_a_all_passed"],
                orientation=scenario_agg["max_stage_b_orientation_error_rad"],
                qdot=scenario_agg["max_stage_b_qdot_saturation_fraction"],
                tail_qdot=scenario_agg["max_stage_b_tail_qdot_utilization"],
                force=scenario_agg["max_stage_b_tail_force_error_N"],
            )
        )
    lines.extend(["", "## Case Matrix", ""])
    for scenario in scenarios:
        lines.extend(
            [
                f"### `{scenario['name']}`",
                "",
                "| delta mm | stitched | Stage B pass | max orientation | max qdot sat | max tail qdot | max force err | failed rows |",
                "| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for case in scenario["cases"]:
            failed_rows = [
                f"{row['trajectory']}:{','.join(row['failed_criteria'])}"
                for row in case["stage_b_rows"]
                if row["failed_criteria"]
            ]
            lines.append(
                "| `{delta}` | `{stitched}` | `{handoff}/{count}` | `{orientation}` | `{qdot}` | `{tail_qdot}` | `{force}` | `{failed}` |".format(
                    delta=case["base_z_offset_delta_mm"],
                    stitched=case["stitched_passed"],
                    handoff=case["handoff_pass_count"],
                    count=case["handoff_trajectory_count"],
                    orientation=case["stage_b_max_orientation_error_rad"],
                    qdot=case["stage_b_max_qdot_saturation_fraction"],
                    tail_qdot=case["stage_b_max_tail_qdot_utilization"],
                    force=case["stage_b_max_tail_force_error_N"],
                    failed="; ".join(failed_rows) or "none",
                )
            )
        lines.append("")
    lines.extend(
        [
            "Interpretation:",
            "",
            "- The v79 planar-primary priority recovery is tested here across the full positive-delta matrix rather than only the `+1.0 mm` row.",
            "- The claim remains tied to a run-local `0.11995 rad` orientation gate and the diagnostic staged setup.",
            "- This is not strict paper-equivalent, robustness, contact calibration, or hardware evidence.",
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
    parser.add_argument("--base-z-deltas-mm", default="0.05,0.1,0.15,0.2,0.25,0.5,0.75,1.0")
    parser.add_argument("--stage-a-duration-s", type=float, default=15.0)
    parser.add_argument("--paper-time-scale", type=float, default=0.005)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--orientation-gate-rad", type=float, default=0.11995)
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    source_config = source_run / "relaxed_stage_a_target_config.yaml"
    deltas_m = [value / 1000.0 for value in parse_float_list(args.base_z_deltas_mm)]
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "positive_planar_priority_matrix" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    stage_a_target_config = write_stage_a_config(
        out_dir=out_dir,
        source_config=source_config,
        orientation_gate_rad=args.orientation_gate_rad,
    )

    scenario_payloads = []
    for scenario in SCENARIOS:
        cases = []
        for delta_m in deltas_m:
            posture_target_q = handoff_posture_text(source_run, delta_m)
            case_dir = out_dir / "scenarios" / scenario["name"] / f"delta_{delta_m * 1000.0:.3f}mm".replace(".", "p")
            case_dir.mkdir(parents=True, exist_ok=True)
            metrics = run_child(
                stitched_command(
                    out_dir=case_dir,
                    source_run=source_run,
                    stage_a_target_config=stage_a_target_config,
                    delta_m=delta_m,
                    stage_a_duration_s=args.stage_a_duration_s,
                    paper_time_scale=args.paper_time_scale,
                    qdot_limit_rad_s=args.qdot_limit_rad_s,
                    max_orientation_error_rad=args.orientation_gate_rad,
                    scenario=scenario,
                    posture_target_q=posture_target_q,
                ),
                out_dir=case_dir,
            )
            case = summarize_case(delta_m, metrics)
            rows = stage_b_rows(metrics)
            case.update(
                {
                    "scenario": scenario["name"],
                    "stage_b_rows": rows,
                    "stage_b_max_orientation_error_rad": max(row["orientation_error_rad"] for row in rows),
                    "stage_b_max_qdot_saturation_fraction": max(
                        row["qdot_saturation_fraction"] for row in rows
                    ),
                    "stage_b_max_tail_qdot_utilization": max(
                        row["tail_max_qdot_utilization"] for row in rows
                    ),
                    "stage_b_max_tail_force_error_N": max(
                        row["tail_mean_abs_force_error_N"] for row in rows
                    ),
                    "stage_b_max_xy_error_m": max(row["max_tangential_position_error_m"] for row in rows),
                }
            )
            cases.append(case)
        scenario_payloads.append(
            {
                "name": scenario["name"],
                "description": scenario["description"],
                "parameters": {
                    "orientation_priority_mode": scenario["orientation_priority_mode"],
                    "orientation_kp": float(scenario["orientation_kp"]),
                    "normal_axis_weight": float(scenario["normal_axis_weight"]),
                },
                "aggregate": aggregate_scenario_cases(cases),
                "cases": cases,
            }
        )

    aggregate = aggregate_all(scenario_payloads)
    payload = {
        "run_id": run_id,
        "source": "v80 full positive-delta planar-primary Stage B priority matrix",
        "source_run": str(source_run),
        "source_stage_a_target_config": str(source_config),
        "stage_a_target_config": str(stage_a_target_config),
        "base_z_deltas_mm": [float(value * 1000.0) for value in deltas_m],
        "stage_a_duration_s": float(args.stage_a_duration_s),
        "paper_time_scale": float(args.paper_time_scale),
        "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
        "orientation_gate_rad": float(args.orientation_gate_rad),
        "trajectories": TRAJECTORY_ORDER,
        "aggregate": aggregate,
        "scenarios": scenario_payloads,
        "warnings": [
            "diagnostic-label full positive planar-priority matrix only",
            "uses run-local copied Stage A target config",
            "not a canonical config change",
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
    write_summary(out_dir, aggregate, scenario_payloads)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
