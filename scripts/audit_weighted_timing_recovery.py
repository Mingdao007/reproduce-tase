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
)


TRAJECTORY_ORDER = ["e1-cycloid", "e2-figure-eight", "e3-circle", "e4-cardioid"]

SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "linear_kp0_normal1",
        "orientation_priority_mode": "linear_primary",
        "orientation_kp": 0.0,
        "normal_axis_weight": 1.0,
        "description": "v72/v76 linear-primary baseline with no Stage B orientation feedback.",
    },
    {
        "name": "planar_normal30_kp0p001",
        "orientation_priority_mode": "planar_primary",
        "orientation_kp": 0.001,
        "normal_axis_weight": 30.0,
        "description": "v80 lower-gain planar-primary candidate.",
    },
    {
        "name": "planar_normal30_kp0p002",
        "orientation_priority_mode": "planar_primary",
        "orientation_kp": 0.002,
        "normal_axis_weight": 30.0,
        "description": "v80 higher-gain planar-primary candidate.",
    },
    {
        "name": "weighted_kp0_normal1",
        "orientation_priority_mode": "weighted",
        "orientation_kp": 0.0,
        "normal_axis_weight": 1.0,
        "description": "weighted zero-angular-command candidate surfaced by the v82 throwaway probe.",
    },
    {
        "name": "weighted_kp0_normal30",
        "orientation_priority_mode": "weighted",
        "orientation_kp": 0.0,
        "normal_axis_weight": 30.0,
        "description": "weighted zero-angular-command control with the v80 normal-axis weight.",
    },
]

TIMING_SWEEP_SCENARIO = "weighted_kp0_normal1"


def value_label(prefix: str, value: float) -> str:
    text = f"{float(value):.6f}".rstrip("0").rstrip(".").replace("-", "m").replace(".", "p")
    return f"{prefix}_{text}"


def write_stage_a_config(
    *,
    out_dir: pathlib.Path,
    source_config: pathlib.Path,
    orientation_gate_rad: float,
) -> pathlib.Path:
    config = yaml.safe_load(source_config.read_text(encoding="utf-8"))
    target = config["selected_stage_a_target"]
    target["diagnostic_gate"]["max_terminal_orientation_error_rad"] = float(orientation_gate_rad)
    config["v82_weighted_timing_recovery_scope"] = {
        "source_config": str(source_config),
        "max_terminal_orientation_error_rad": float(orientation_gate_rad),
        "claim_scope": "run-local weighted-priority faster-timing recovery probe only",
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


def run_case(
    *,
    out_dir: pathlib.Path,
    source_run: pathlib.Path,
    stage_a_target_config: pathlib.Path,
    group: str,
    scenario: dict[str, Any],
    delta_m: float,
    stage_a_duration_s: float,
    paper_time_scale: float,
    qdot_limit_rad_s: float,
    orientation_gate_rad: float,
) -> dict[str, Any]:
    posture_target_q = handoff_posture_text(source_run, delta_m)
    metrics = run_child(
        stitched_command(
            out_dir=out_dir,
            source_run=source_run,
            stage_a_target_config=stage_a_target_config,
            delta_m=delta_m,
            stage_a_duration_s=stage_a_duration_s,
            paper_time_scale=paper_time_scale,
            qdot_limit_rad_s=qdot_limit_rad_s,
            max_orientation_error_rad=orientation_gate_rad,
            scenario=scenario,
            posture_target_q=posture_target_q,
        ),
        out_dir=out_dir,
    )
    rows = stage_b_rows(metrics)
    case = summarize_case(delta_m, metrics)
    e2 = next(row for row in rows if row["trajectory"] == "e2-figure-eight")
    case.update(
        {
            "group": group,
            "scenario": scenario["name"],
            "orientation_priority_mode": scenario["orientation_priority_mode"],
            "orientation_kp": float(scenario["orientation_kp"]),
            "normal_axis_weight": float(scenario["normal_axis_weight"]),
            "stage_a_target_config": str(stage_a_target_config),
            "stage_a_duration_s": float(stage_a_duration_s),
            "paper_time_scale": float(paper_time_scale),
            "qdot_limit_rad_s": float(qdot_limit_rad_s),
            "orientation_gate_rad": float(orientation_gate_rad),
            "stage_b_rows": rows,
            "stage_b_max_orientation_error_rad": max(row["orientation_error_rad"] for row in rows),
            "stage_b_max_qdot_saturation_fraction": max(row["qdot_saturation_fraction"] for row in rows),
            "stage_b_max_tail_qdot_utilization": max(row["tail_max_qdot_utilization"] for row in rows),
            "stage_b_max_tail_force_error_N": max(row["tail_mean_abs_force_error_N"] for row in rows),
            "stage_b_max_xy_error_m": max(row["max_tangential_position_error_m"] for row in rows),
            "e2_passed": bool(e2["passed"]),
            "e2_failed_criteria": e2["failed_criteria"],
            "e2_orientation_error_rad": e2["orientation_error_rad"],
            "e2_qdot_saturation_fraction": e2["qdot_saturation_fraction"],
            "e2_tail_qdot_utilization": e2["tail_max_qdot_utilization"],
            "e2_tail_force_error_N": e2["tail_mean_abs_force_error_N"],
        }
    )
    return case


def case_id(case: dict[str, Any], suffix: str) -> str:
    return (
        f"{case['scenario']}:{suffix}:delta{case['base_z_offset_delta_mm']:.3f}mm"
        .replace(".", "p")
        .replace("-", "m")
    )


def aggregate_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    passing = [case for case in cases if case["stitched_passed"]]
    failed = [case for case in cases if not case["stitched_passed"]]
    passed_deltas = [case["base_z_offset_delta_mm"] for case in passing]
    return {
        "case_count": len(cases),
        "stitched_pass_count": len(passing),
        "stitched_fail_count": len(failed),
        "all_cases_passed": len(passing) == len(cases) and bool(cases),
        "passing_cases": [case["case_id"] for case in passing],
        "failing_cases": [case["case_id"] for case in failed],
        "max_positive_stitched_pass_delta_mm": max(passed_deltas) if passed_deltas else None,
        "stage_a_all_passed": all(case["stage_a_passed"] for case in cases),
        "max_stage_a_terminal_orientation_error_rad": max(
            case["stage_a_terminal_orientation_error_rad"] for case in cases
        ),
        "max_stage_b_orientation_error_rad": max(case["stage_b_max_orientation_error_rad"] for case in cases),
        "max_stage_b_qdot_saturation_fraction": max(
            case["stage_b_max_qdot_saturation_fraction"] for case in cases
        ),
        "max_stage_b_tail_qdot_utilization": max(case["stage_b_max_tail_qdot_utilization"] for case in cases),
        "max_stage_b_tail_force_error_N": max(case["stage_b_max_tail_force_error_N"] for case in cases),
    }


def aggregate_timing(cases: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate = aggregate_cases(cases)
    passing = [case for case in cases if case["stitched_passed"]]
    failing = [case for case in cases if not case["stitched_passed"]]
    aggregate.update(
        {
            "max_passing_paper_time_scale": max(
                (case["paper_time_scale"] for case in passing),
                default=None,
            ),
            "min_failing_paper_time_scale": min(
                (case["paper_time_scale"] for case in failing),
                default=None,
            ),
        }
    )
    return aggregate


def aggregate_all(full_delta_scenarios: list[dict[str, Any]], timing_sweep: dict[str, Any]) -> dict[str, Any]:
    full_case_count = sum(scenario["aggregate"]["case_count"] for scenario in full_delta_scenarios)
    full_pass_count = sum(scenario["aggregate"]["stitched_pass_count"] for scenario in full_delta_scenarios)
    return {
        "full_delta_scenario_count": len(full_delta_scenarios),
        "full_delta_case_count": full_case_count,
        "full_delta_stitched_pass_count": full_pass_count,
        "full_delta_stitched_fail_count": full_case_count - full_pass_count,
        "full_delta_all_pass_scenarios": [
            scenario["name"]
            for scenario in full_delta_scenarios
            if scenario["aggregate"]["all_cases_passed"]
        ],
        "timing_sweep_case_count": timing_sweep["aggregate"]["case_count"],
        "timing_sweep_stitched_pass_count": timing_sweep["aggregate"]["stitched_pass_count"],
    }


def failed_rows_text(case: dict[str, Any]) -> str:
    failed = [
        f"{row['trajectory']}:{','.join(row['failed_criteria'])}"
        for row in case["stage_b_rows"]
        if row["failed_criteria"]
    ]
    return "; ".join(failed) or "none"


def write_summary(
    out_dir: pathlib.Path,
    aggregate: dict[str, Any],
    full_delta_scenarios: list[dict[str, Any]],
    timing_sweep: dict[str, Any],
) -> None:
    lines = [
        "# Weighted Timing Recovery Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Full-delta scenario count: `{aggregate['full_delta_scenario_count']}`",
        f"- Full-delta stitched pass count: `{aggregate['full_delta_stitched_pass_count']} / {aggregate['full_delta_case_count']}`",
        f"- Full-delta all-pass scenarios: `{', '.join(aggregate['full_delta_all_pass_scenarios']) or 'none'}`",
        f"- Timing sweep stitched pass count: `{aggregate['timing_sweep_stitched_pass_count']} / {aggregate['timing_sweep_case_count']}`",
        f"- Timing sweep max passing scale: `{timing_sweep['aggregate']['max_passing_paper_time_scale']}`",
        f"- Timing sweep min failing scale: `{timing_sweep['aggregate']['min_failing_paper_time_scale']}`",
        "",
        "## Full Positive-Delta Stress",
        "",
        "| scenario | priority | normal weight | pass count | max pass delta mm | max orientation | max qdot sat | max tail qdot | max force err |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for scenario in full_delta_scenarios:
        scenario_agg = scenario["aggregate"]
        parameters = scenario["parameters"]
        lines.append(
            "| `{name}` | `{priority}` | `{normal}` | `{passed}/{count}` | `{delta}` | `{orientation}` | `{qdot}` | `{tail_qdot}` | `{force}` |".format(
                name=scenario["name"],
                priority=parameters["orientation_priority_mode"],
                normal=parameters["normal_axis_weight"],
                passed=scenario_agg["stitched_pass_count"],
                count=scenario_agg["case_count"],
                delta=scenario_agg["max_positive_stitched_pass_delta_mm"],
                orientation=scenario_agg["max_stage_b_orientation_error_rad"],
                qdot=scenario_agg["max_stage_b_qdot_saturation_fraction"],
                tail_qdot=scenario_agg["max_stage_b_tail_qdot_utilization"],
                force=scenario_agg["max_stage_b_tail_force_error_N"],
            )
        )

    lines.extend(
        [
            "",
            "## Timing Sweep",
            "",
            "| paper_time_scale | stitched | Stage B pass | E2 orientation | E2 qdot sat | E2 tail qdot | E2 force err | failed rows |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for case in timing_sweep["cases"]:
        lines.append(
            "| `{scale}` | `{stitched}` | `{handoff}/{count}` | `{orientation}` | `{qdot}` | `{tail_qdot}` | `{force}` | `{failed}` |".format(
                scale=case["paper_time_scale"],
                stitched=case["stitched_passed"],
                handoff=case["handoff_pass_count"],
                count=case["handoff_trajectory_count"],
                orientation=case["e2_orientation_error_rad"],
                qdot=case["e2_qdot_saturation_fraction"],
                tail_qdot=case["e2_tail_qdot_utilization"],
                force=case["e2_tail_force_error_N"],
                failed=failed_rows_text(case),
            )
        )

    lines.extend(
        [
            "",
            "## Failed Case Detail",
            "",
            "| group | case | stitched | Stage A | Stage B pass | E2 orientation | E2 qdot sat | failed rows |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    any_failure = False
    for scenario in full_delta_scenarios:
        for case in scenario["cases"]:
            if case["stitched_passed"]:
                continue
            any_failure = True
            lines.append(
                "| `full_delta` | `{case}` | `{stitched}` | `{stage_a}` | `{handoff}/{count}` | `{orientation}` | `{qdot}` | `{failed}` |".format(
                    case=case["case_id"],
                    stitched=case["stitched_passed"],
                    stage_a=case["stage_a_passed"],
                    handoff=case["handoff_pass_count"],
                    count=case["handoff_trajectory_count"],
                    orientation=case["e2_orientation_error_rad"],
                    qdot=case["e2_qdot_saturation_fraction"],
                    failed=failed_rows_text(case),
                )
            )
    for case in timing_sweep["cases"]:
        if case["stitched_passed"]:
            continue
        any_failure = True
        lines.append(
            "| `timing_sweep` | `{case}` | `{stitched}` | `{stage_a}` | `{handoff}/{count}` | `{orientation}` | `{qdot}` | `{failed}` |".format(
                case=case["case_id"],
                stitched=case["stitched_passed"],
                stage_a=case["stage_a_passed"],
                handoff=case["handoff_pass_count"],
                count=case["handoff_trajectory_count"],
                orientation=case["e2_orientation_error_rad"],
                qdot=case["e2_qdot_saturation_fraction"],
                failed=failed_rows_text(case),
            )
        )
    if not any_failure:
        lines.append("| `none` | `none` | `True` | `True` | `n/a` | `n/a` | `n/a` | `none` |")

    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The weighted zero-angular-command candidate is tested as a faster-timing recovery, not as a new canonical controller default.",
            "- Full-delta rows compare it against the v72 linear-primary baseline and the v80 planar-primary candidates on the same `0.0075` timing face.",
            "- The timing sweep localizes the `+1.0 mm` faster-timing boundary for the weighted candidate.",
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
    parser.add_argument("--stage-a-duration-s", type=float, default=15.0)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--orientation-gate-rad", type=float, default=0.11995)
    parser.add_argument("--full-delta-paper-time-scale", type=float, default=0.0075)
    parser.add_argument(
        "--timing-sweep-paper-time-scales",
        default="0.005,0.006,0.0065,0.007,0.0075,0.008,0.0085,0.009,0.0095,0.01",
    )
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    source_config = source_run / "relaxed_stage_a_target_config.yaml"
    deltas_m = [value / 1000.0 for value in parse_float_list(args.base_z_deltas_mm)]
    boundary_delta_m = float(args.boundary_base_z_delta_mm) / 1000.0
    timing_scales = parse_float_list(args.timing_sweep_paper_time_scales)
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "weighted_timing_recovery" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    stage_a_target_config = write_stage_a_config(
        out_dir=out_dir,
        source_config=source_config,
        orientation_gate_rad=args.orientation_gate_rad,
    )

    full_delta_scenarios = []
    for scenario in SCENARIOS:
        cases = []
        for delta_m in deltas_m:
            case_dir = (
                out_dir
                / "full_delta"
                / scenario["name"]
                / f"delta_{delta_m * 1000.0:.3f}mm".replace(".", "p")
            )
            case_dir.mkdir(parents=True, exist_ok=True)
            case = run_case(
                out_dir=case_dir,
                source_run=source_run,
                stage_a_target_config=stage_a_target_config,
                group="full_delta",
                scenario=scenario,
                delta_m=delta_m,
                stage_a_duration_s=args.stage_a_duration_s,
                paper_time_scale=args.full_delta_paper_time_scale,
                qdot_limit_rad_s=args.qdot_limit_rad_s,
                orientation_gate_rad=args.orientation_gate_rad,
            )
            case["case_id"] = case_id(case, f"time_{args.full_delta_paper_time_scale}")
            cases.append(case)
        full_delta_scenarios.append(
            {
                "name": scenario["name"],
                "description": scenario["description"],
                "parameters": {
                    "orientation_priority_mode": scenario["orientation_priority_mode"],
                    "orientation_kp": float(scenario["orientation_kp"]),
                    "normal_axis_weight": float(scenario["normal_axis_weight"]),
                },
                "aggregate": aggregate_cases(cases),
                "cases": cases,
            }
        )

    timing_scenario = next(scenario for scenario in SCENARIOS if scenario["name"] == TIMING_SWEEP_SCENARIO)
    timing_cases = []
    for paper_time_scale in timing_scales:
        case_dir = out_dir / "timing_sweep" / value_label("paper_time_scale", paper_time_scale)
        case_dir.mkdir(parents=True, exist_ok=True)
        case = run_case(
            out_dir=case_dir,
            source_run=source_run,
            stage_a_target_config=stage_a_target_config,
            group="timing_sweep",
            scenario=timing_scenario,
            delta_m=boundary_delta_m,
            stage_a_duration_s=args.stage_a_duration_s,
            paper_time_scale=paper_time_scale,
            qdot_limit_rad_s=args.qdot_limit_rad_s,
            orientation_gate_rad=args.orientation_gate_rad,
        )
        case["case_id"] = case_id(case, value_label("time", paper_time_scale))
        timing_cases.append(case)
    timing_sweep = {
        "name": "weighted_kp0_normal1_timing_sweep",
        "description": "focused +1.0 mm timing boundary for weighted_kp0_normal1",
        "parameters": {
            "orientation_priority_mode": timing_scenario["orientation_priority_mode"],
            "orientation_kp": float(timing_scenario["orientation_kp"]),
            "normal_axis_weight": float(timing_scenario["normal_axis_weight"]),
        },
        "aggregate": aggregate_timing(timing_cases),
        "cases": timing_cases,
    }

    aggregate = aggregate_all(full_delta_scenarios, timing_sweep)
    payload = {
        "run_id": run_id,
        "source": "v82 weighted zero-angular-command faster-timing recovery audit",
        "source_run": str(source_run),
        "source_stage_a_target_config": str(source_config),
        "stage_a_target_config": str(stage_a_target_config),
        "base_z_deltas_mm": [float(value * 1000.0) for value in deltas_m],
        "boundary_base_z_delta_mm": float(args.boundary_base_z_delta_mm),
        "stage_a_duration_s": float(args.stage_a_duration_s),
        "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
        "orientation_gate_rad": float(args.orientation_gate_rad),
        "full_delta_paper_time_scale": float(args.full_delta_paper_time_scale),
        "timing_sweep_paper_time_scales": timing_scales,
        "scenarios": SCENARIOS,
        "timing_sweep_scenario": TIMING_SWEEP_SCENARIO,
        "trajectories": TRAJECTORY_ORDER,
        "aggregate": aggregate,
        "full_delta_scenarios": full_delta_scenarios,
        "timing_sweep": timing_sweep,
        "warnings": [
            "diagnostic-label weighted-priority faster-timing recovery audit only",
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
    write_summary(out_dir, aggregate, full_delta_scenarios, timing_sweep)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
