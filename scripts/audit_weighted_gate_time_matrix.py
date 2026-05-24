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

from audit_stage_a_base_z_bracket import parse_float_list
from audit_stage_a_base_z_recovery import write_git_state
from audit_weighted_timing_recovery import (
    aggregate_cases,
    failed_rows_text,
    run_case,
    value_label,
)


TRAJECTORY_ORDER = ["e1-cycloid", "e2-figure-eight", "e3-circle", "e4-cardioid"]

WEIGHTED_SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "weighted_kp0_normal1",
        "orientation_priority_mode": "weighted",
        "orientation_kp": 0.0,
        "normal_axis_weight": 1.0,
        "description": "v82 weighted zero-angular-command candidate.",
    },
    {
        "name": "weighted_kp0_normal30",
        "orientation_priority_mode": "weighted",
        "orientation_kp": 0.0,
        "normal_axis_weight": 30.0,
        "description": "v82 weighted zero-angular-command candidate with the v80 normal-axis weight.",
    },
]

FULL_MATRIX_GROUPS: list[dict[str, Any]] = [
    {
        "name": "time0p01_gate0p11995",
        "paper_time_scale": 0.01,
        "orientation_gate_rad": 0.11995,
        "description": "full positive-delta weighted matrix at the original v71 timing scale under the v82 gate",
    },
    {
        "name": "time0p0075_gate0p119",
        "paper_time_scale": 0.0075,
        "orientation_gate_rad": 0.119,
        "description": "full positive-delta weighted matrix on the tightened 0.119 rad gate at the v82 recovered timing",
    },
    {
        "name": "time0p01_gate0p119",
        "paper_time_scale": 0.01,
        "orientation_gate_rad": 0.119,
        "description": "full positive-delta weighted matrix on the tightened 0.119 rad gate at the original v71 timing scale",
    },
]


def write_stage_a_config(
    *,
    out_dir: pathlib.Path,
    source_config: pathlib.Path,
    orientation_gate_rad: float,
) -> pathlib.Path:
    config = yaml.safe_load(source_config.read_text(encoding="utf-8"))
    target = config["selected_stage_a_target"]
    target["diagnostic_gate"]["max_terminal_orientation_error_rad"] = float(orientation_gate_rad)
    config["v83_weighted_gate_time_matrix_scope"] = {
        "source_config": str(source_config),
        "max_terminal_orientation_error_rad": float(orientation_gate_rad),
        "claim_scope": "run-local weighted-priority gate/time matrix only",
    }
    if "v70_relaxed_orientation_scope" in config:
        config["v70_relaxed_orientation_scope"]["max_terminal_orientation_error_rad"] = float(
            orientation_gate_rad
        )

    config_dir = out_dir / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    target_config = config_dir / (
        f"{value_label('orientation_gate', orientation_gate_rad)}_stage_a_target_config.yaml"
    )
    with target_config.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)
    return target_config


def stage_a_config_for_gate(
    *,
    cache: dict[float, pathlib.Path],
    out_dir: pathlib.Path,
    source_config: pathlib.Path,
    orientation_gate_rad: float,
) -> pathlib.Path:
    key = float(orientation_gate_rad)
    if key not in cache:
        cache[key] = write_stage_a_config(
            out_dir=out_dir,
            source_config=source_config,
            orientation_gate_rad=key,
        )
    return cache[key]


def case_id(case: dict[str, Any], suffix: str) -> str:
    return (
        f"{case['scenario']}:{suffix}:delta{case['base_z_offset_delta_mm']:.3f}mm"
        .replace(".", "p")
        .replace("-", "m")
    )


def aggregate_gate_boundary(cases: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate = aggregate_cases(cases)
    passing = [case for case in cases if case["stitched_passed"]]
    failing = [case for case in cases if not case["stitched_passed"]]
    aggregate.update(
        {
            "min_passing_orientation_gate_rad": min(
                (case["orientation_gate_rad"] for case in passing),
                default=None,
            ),
            "max_failing_orientation_gate_rad": max(
                (case["orientation_gate_rad"] for case in failing),
                default=None,
            ),
        }
    )
    return aggregate


def aggregate_all(full_groups: list[dict[str, Any]], boundary_groups: list[dict[str, Any]]) -> dict[str, Any]:
    all_groups = full_groups + boundary_groups
    case_count = sum(group["aggregate"]["case_count"] for group in all_groups)
    pass_count = sum(group["aggregate"]["stitched_pass_count"] for group in all_groups)
    return {
        "group_count": len(all_groups),
        "case_count": case_count,
        "stitched_pass_count": pass_count,
        "stitched_fail_count": case_count - pass_count,
        "all_pass_groups": [
            group["name"] for group in all_groups if group["aggregate"]["all_cases_passed"]
        ],
        "failing_groups": [
            group["name"] for group in all_groups if not group["aggregate"]["all_cases_passed"]
        ],
    }


def write_summary(
    out_dir: pathlib.Path,
    aggregate: dict[str, Any],
    full_groups: list[dict[str, Any]],
    boundary_groups: list[dict[str, Any]],
) -> None:
    lines = [
        "# Weighted Gate/Time Matrix Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Group count: `{aggregate['group_count']}`",
        f"- Total case count: `{aggregate['case_count']}`",
        f"- Total stitched pass count: `{aggregate['stitched_pass_count']} / {aggregate['case_count']}`",
        f"- All-pass groups: `{', '.join(aggregate['all_pass_groups']) or 'none'}`",
        f"- Failing groups: `{', '.join(aggregate['failing_groups']) or 'none'}`",
        "",
        "## Full Matrix Groups",
        "",
        "| group | scenario | time scale | gate | pass count | max pass delta mm | max orientation | max qdot sat | max tail qdot | max force err |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for group in full_groups:
        group_aggregate = group["aggregate"]
        lines.append(
            "| `{group}` | `{scenario}` | `{scale}` | `{gate}` | `{passed}/{count}` | `{delta}` | `{orientation}` | `{qdot}` | `{tail_qdot}` | `{force}` |".format(
                group=group["name"],
                scenario=group["scenario"],
                scale=group["paper_time_scale"],
                gate=group["orientation_gate_rad"],
                passed=group_aggregate["stitched_pass_count"],
                count=group_aggregate["case_count"],
                delta=group_aggregate["max_positive_stitched_pass_delta_mm"],
                orientation=group_aggregate["max_stage_b_orientation_error_rad"],
                qdot=group_aggregate["max_stage_b_qdot_saturation_fraction"],
                tail_qdot=group_aggregate["max_stage_b_tail_qdot_utilization"],
                force=group_aggregate["max_stage_b_tail_force_error_N"],
            )
        )

    lines.extend(
        [
            "",
            "## Gate Boundary Groups",
            "",
            "| group | time scale | pass count | min passing gate | max failing gate | max orientation | max qdot sat |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for group in boundary_groups:
        group_aggregate = group["aggregate"]
        lines.append(
            "| `{group}` | `{scale}` | `{passed}/{count}` | `{min_pass}` | `{max_fail}` | `{orientation}` | `{qdot}` |".format(
                group=group["name"],
                scale=group["paper_time_scale"],
                passed=group_aggregate["stitched_pass_count"],
                count=group_aggregate["case_count"],
                min_pass=group_aggregate["min_passing_orientation_gate_rad"],
                max_fail=group_aggregate["max_failing_orientation_gate_rad"],
                orientation=group_aggregate["max_stage_b_orientation_error_rad"],
                qdot=group_aggregate["max_stage_b_qdot_saturation_fraction"],
            )
        )

    lines.extend(
        [
            "",
            "## Failed Case Detail",
            "",
            "| group | case | stitched | Stage A | Stage B pass | gate | time scale | delta mm | E2 orientation | E2 qdot sat | failed rows |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    any_failure = False
    for group in full_groups + boundary_groups:
        for case in group["cases"]:
            if case["stitched_passed"]:
                continue
            any_failure = True
            lines.append(
                "| `{group}` | `{case}` | `{stitched}` | `{stage_a}` | `{handoff}/{count}` | `{gate}` | `{scale}` | `{delta}` | `{orientation}` | `{qdot}` | `{failed}` |".format(
                    group=group["name"],
                    case=case["case_id"],
                    stitched=case["stitched_passed"],
                    stage_a=case["stage_a_passed"],
                    handoff=case["handoff_pass_count"],
                    count=case["handoff_trajectory_count"],
                    gate=case["orientation_gate_rad"],
                    scale=case["paper_time_scale"],
                    delta=case["base_z_offset_delta_mm"],
                    orientation=case["e2_orientation_error_rad"],
                    qdot=case["e2_qdot_saturation_fraction"],
                    failed=failed_rows_text(case),
                )
            )
    if not any_failure:
        lines.append("| `none` | `none` | `True` | `True` | `n/a` | `n/a` | `n/a` | `n/a` | `n/a` | `n/a` | `none` |")

    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The `0.01` full matrix checks whether the v82 focused timing sweep generalizes across all positive deltas under the `0.11995 rad` gate.",
            "- The `0.119 rad` full matrix checks whether the weighted candidate changes the tightened-gate `+1.0 mm` limit.",
            "- The focused gate-boundary groups bracket the `+1.0 mm` gate needed by weighted zero-angular-command priority.",
            "- This remains diagnostic-label simulation evidence only.",
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
    parser.add_argument("--boundary-base-z-delta-mm", type=float, default=1.0)
    parser.add_argument(
        "--orientation-gates",
        default="0.119,0.11925,0.1194,0.1195,0.11955,0.1196,0.1197,0.11995",
    )
    parser.add_argument("--stage-a-duration-s", type=float, default=15.0)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    source_config = source_run / "relaxed_stage_a_target_config.yaml"
    deltas_m = [value / 1000.0 for value in parse_float_list(args.base_z_deltas_mm)]
    boundary_delta_m = float(args.boundary_base_z_delta_mm) / 1000.0
    orientation_gates = parse_float_list(args.orientation_gates)
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "weighted_gate_time_matrix" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    config_cache: dict[float, pathlib.Path] = {}

    full_groups = []
    for group in FULL_MATRIX_GROUPS:
        stage_a_target_config = stage_a_config_for_gate(
            cache=config_cache,
            out_dir=out_dir,
            source_config=source_config,
            orientation_gate_rad=group["orientation_gate_rad"],
        )
        for scenario in WEIGHTED_SCENARIOS:
            cases = []
            for delta_m in deltas_m:
                case_dir = (
                    out_dir
                    / "full_matrix"
                    / str(group["name"])
                    / scenario["name"]
                    / f"delta_{delta_m * 1000.0:.3f}mm".replace(".", "p")
                )
                case_dir.mkdir(parents=True, exist_ok=True)
                case = run_case(
                    out_dir=case_dir,
                    source_run=source_run,
                    stage_a_target_config=stage_a_target_config,
                    group=str(group["name"]),
                    scenario=scenario,
                    delta_m=delta_m,
                    stage_a_duration_s=args.stage_a_duration_s,
                    paper_time_scale=group["paper_time_scale"],
                    qdot_limit_rad_s=args.qdot_limit_rad_s,
                    orientation_gate_rad=group["orientation_gate_rad"],
                )
                case["case_id"] = case_id(case, f"{group['name']}")
                cases.append(case)
            full_groups.append(
                {
                    "name": f"{group['name']}:{scenario['name']}",
                    "description": group["description"],
                    "scenario": scenario["name"],
                    "parameters": {
                        "orientation_priority_mode": scenario["orientation_priority_mode"],
                        "orientation_kp": float(scenario["orientation_kp"]),
                        "normal_axis_weight": float(scenario["normal_axis_weight"]),
                    },
                    "paper_time_scale": float(group["paper_time_scale"]),
                    "orientation_gate_rad": float(group["orientation_gate_rad"]),
                    "aggregate": aggregate_cases(cases),
                    "cases": cases,
                }
            )

    boundary_groups = []
    boundary_scenario = WEIGHTED_SCENARIOS[0]
    for paper_time_scale in [0.0075, 0.01]:
        cases = []
        for orientation_gate_rad in orientation_gates:
            stage_a_target_config = stage_a_config_for_gate(
                cache=config_cache,
                out_dir=out_dir,
                source_config=source_config,
                orientation_gate_rad=orientation_gate_rad,
            )
            case_dir = (
                out_dir
                / "gate_boundary"
                / value_label("paper_time_scale", paper_time_scale)
                / value_label("orientation_gate", orientation_gate_rad)
            )
            case_dir.mkdir(parents=True, exist_ok=True)
            case = run_case(
                out_dir=case_dir,
                source_run=source_run,
                stage_a_target_config=stage_a_target_config,
                group="gate_boundary",
                scenario=boundary_scenario,
                delta_m=boundary_delta_m,
                stage_a_duration_s=args.stage_a_duration_s,
                paper_time_scale=paper_time_scale,
                qdot_limit_rad_s=args.qdot_limit_rad_s,
                orientation_gate_rad=orientation_gate_rad,
            )
            case["case_id"] = case_id(case, f"time_{paper_time_scale}_gate_{orientation_gate_rad}")
            cases.append(case)
        boundary_groups.append(
            {
                "name": f"gate_boundary_plus1mm_time_{paper_time_scale}".replace(".", "p"),
                "description": f"focused +1.0 mm gate boundary for weighted_kp0_normal1 at paper_time_scale={paper_time_scale}",
                "scenario": boundary_scenario["name"],
                "parameters": {
                    "orientation_priority_mode": boundary_scenario["orientation_priority_mode"],
                    "orientation_kp": float(boundary_scenario["orientation_kp"]),
                    "normal_axis_weight": float(boundary_scenario["normal_axis_weight"]),
                },
                "paper_time_scale": float(paper_time_scale),
                "base_z_offset_delta_mm": float(args.boundary_base_z_delta_mm),
                "aggregate": aggregate_gate_boundary(cases),
                "cases": cases,
            }
        )

    aggregate = aggregate_all(full_groups, boundary_groups)
    payload = {
        "run_id": run_id,
        "source": "v83 weighted zero-angular-command gate/time matrix",
        "source_run": str(source_run),
        "source_stage_a_target_config": str(source_config),
        "base_z_deltas_mm": [float(value * 1000.0) for value in deltas_m],
        "boundary_base_z_delta_mm": float(args.boundary_base_z_delta_mm),
        "orientation_gates_rad": orientation_gates,
        "stage_a_duration_s": float(args.stage_a_duration_s),
        "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
        "weighted_scenarios": WEIGHTED_SCENARIOS,
        "full_matrix_groups": FULL_MATRIX_GROUPS,
        "trajectories": TRAJECTORY_ORDER,
        "aggregate": aggregate,
        "full_groups": full_groups,
        "boundary_groups": boundary_groups,
        "warnings": [
            "diagnostic-label weighted gate/time matrix only",
            "uses run-local copied Stage A target configs",
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
    write_summary(out_dir, aggregate, full_groups, boundary_groups)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
