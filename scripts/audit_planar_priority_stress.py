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

PLANAR_SCENARIOS: list[dict[str, Any]] = [
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
]

FULL_DELTA_STRESSES: list[dict[str, Any]] = [
    {
        "name": "timing_0p0075_gate0p11995",
        "paper_time_scale": 0.0075,
        "orientation_gate_rad": 0.11995,
        "description": "v73 faster-timing failure face with the v80 tightened gate.",
    },
    {
        "name": "orientation_gate0p119_time0p005",
        "paper_time_scale": 0.005,
        "orientation_gate_rad": 0.119,
        "description": "v73 tightened-orientation failure face with v80 timing.",
    },
]


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
    config["v81_planar_priority_stress_scope"] = {
        "source_config": str(source_config),
        "max_terminal_orientation_error_rad": float(orientation_gate_rad),
        "claim_scope": "run-local planar-priority timing/orientation stress config only",
    }
    if "v70_relaxed_orientation_scope" in config:
        config["v70_relaxed_orientation_scope"]["max_terminal_orientation_error_rad"] = float(
            orientation_gate_rad
        )

    config_dir = out_dir / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    gate_config = config_dir / (
        f"{value_label('orientation_gate', orientation_gate_rad)}_stage_a_target_config.yaml"
    )
    with gate_config.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)
    return gate_config


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


def label_dir(*parts: str) -> str:
    return "_".join(part.replace(".", "p").replace("-", "m") for part in parts)


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
        }
    )
    return case


def aggregate_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    passing = [case for case in cases if case["stitched_passed"]]
    failing = [case for case in cases if not case["stitched_passed"]]
    return {
        "case_count": len(cases),
        "stitched_pass_count": len(passing),
        "stitched_fail_count": len(failing),
        "all_cases_passed": len(passing) == len(cases) and bool(cases),
        "passing_cases": [case["case_id"] for case in passing],
        "failing_cases": [case["case_id"] for case in failing],
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


def aggregate_timing_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
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


def aggregate_gate_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
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


def aggregate_all(groups: list[dict[str, Any]]) -> dict[str, Any]:
    case_count = sum(group["aggregate"]["case_count"] for group in groups)
    pass_count = sum(group["aggregate"]["stitched_pass_count"] for group in groups)
    return {
        "group_count": len(groups),
        "case_count": case_count,
        "stitched_pass_count": pass_count,
        "stitched_fail_count": case_count - pass_count,
        "all_groups_all_cases_passed": all(group["aggregate"]["all_cases_passed"] for group in groups),
        "failing_groups": [group["name"] for group in groups if not group["aggregate"]["all_cases_passed"]],
    }


def add_case_id(case: dict[str, Any], *, suffix: str) -> dict[str, Any]:
    case["case_id"] = (
        f"{case['scenario']}:{suffix}:delta{case['base_z_offset_delta_mm']:.3f}mm"
        .replace(".", "p")
        .replace("-", "m")
    )
    return case


def failed_rows_text(case: dict[str, Any]) -> str:
    failed = [
        f"{row['trajectory']}:{','.join(row['failed_criteria'])}"
        for row in case["stage_b_rows"]
        if row["failed_criteria"]
    ]
    return "; ".join(failed) or "none"


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], groups: list[dict[str, Any]]) -> None:
    lines = [
        "# Planar-Priority Stress Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Group count: `{aggregate['group_count']}`",
        f"- Total case count: `{aggregate['case_count']}`",
        f"- Total stitched pass count: `{aggregate['stitched_pass_count']} / {aggregate['case_count']}`",
        f"- All groups pass all cases: `{aggregate['all_groups_all_cases_passed']}`",
        f"- Failing groups: `{', '.join(aggregate['failing_groups']) or 'none'}`",
        "",
        "## Group Aggregates",
        "",
        "| group | scenario | pass count | Stage A all pass | max orientation | max qdot sat | max tail qdot | max force err | boundary |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for group in groups:
        group_agg = group["aggregate"]
        boundary_parts = []
        if "max_passing_paper_time_scale" in group_agg:
            boundary_parts.append(f"max pass scale={group_agg['max_passing_paper_time_scale']}")
            boundary_parts.append(f"min fail scale={group_agg['min_failing_paper_time_scale']}")
        if "min_passing_orientation_gate_rad" in group_agg:
            boundary_parts.append(f"min pass gate={group_agg['min_passing_orientation_gate_rad']}")
            boundary_parts.append(f"max fail gate={group_agg['max_failing_orientation_gate_rad']}")
        lines.append(
            "| `{name}` | `{scenario}` | `{passed}/{count}` | `{stage_a}` | `{orientation}` | `{qdot}` | `{tail_qdot}` | `{force}` | `{boundary}` |".format(
                name=group["name"],
                scenario=group["scenario"],
                passed=group_agg["stitched_pass_count"],
                count=group_agg["case_count"],
                stage_a=group_agg["stage_a_all_passed"],
                orientation=group_agg["max_stage_b_orientation_error_rad"],
                qdot=group_agg["max_stage_b_qdot_saturation_fraction"],
                tail_qdot=group_agg["max_stage_b_tail_qdot_utilization"],
                force=group_agg["max_stage_b_tail_force_error_N"],
                boundary=", ".join(boundary_parts) or "n/a",
            )
        )

    lines.extend(["", "## Failed Case Detail", ""])
    lines.extend(
        [
            "| group | case | stitched | Stage A | Stage B pass | time scale | gate | delta mm | E2 orientation | E2 qdot sat | failed rows |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    any_failure = False
    for group in groups:
        for case in group["cases"]:
            if case["stitched_passed"]:
                continue
            any_failure = True
            lines.append(
                "| `{group}` | `{case}` | `{stitched}` | `{stage_a}` | `{handoff}/{count}` | `{scale}` | `{gate}` | `{delta}` | `{orientation}` | `{qdot}` | `{failed}` |".format(
                    group=group["name"],
                    case=case["case_id"],
                    stitched=case["stitched_passed"],
                    stage_a=case["stage_a_passed"],
                    handoff=case["handoff_pass_count"],
                    count=case["handoff_trajectory_count"],
                    scale=case["paper_time_scale"],
                    gate=case["orientation_gate_rad"],
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
            "- This stress audit reuses the v80 planar-primary Stage B candidates without changing canonical defaults.",
            "- The timing boundary rows isolate whether planar priority moves the old v76 `+1.0 mm` faster-timing limit.",
            "- The orientation-gate rows isolate whether planar priority moves the old v77 `+1.0 mm` tightened-gate limit.",
            "- The full-delta stress rows test the old v73 failing scenario faces across all positive base-z deltas.",
            "- This remains diagnostic-label simulation evidence, not strict paper-equivalent, robustness, contact calibration, or hardware readiness.",
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
        "--paper-time-scales",
        default="0.005,0.0052,0.0054,0.0056,0.0058,0.006,0.0065,0.007,0.0075",
    )
    parser.add_argument(
        "--orientation-gates",
        default="0.119,0.11925,0.1195,0.1196,0.1197,0.1198,0.1199,0.11995",
    )
    parser.add_argument("--stage-a-duration-s", type=float, default=15.0)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--timing-orientation-gate-rad", type=float, default=0.11995)
    parser.add_argument("--gate-paper-time-scale", type=float, default=0.005)
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    source_config = source_run / "relaxed_stage_a_target_config.yaml"
    deltas_m = [value / 1000.0 for value in parse_float_list(args.base_z_deltas_mm)]
    boundary_delta_m = float(args.boundary_base_z_delta_mm) / 1000.0
    paper_time_scales = parse_float_list(args.paper_time_scales)
    orientation_gates = parse_float_list(args.orientation_gates)
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "planar_priority_stress" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    stage_a_config_cache: dict[float, pathlib.Path] = {}

    groups: list[dict[str, Any]] = []
    for scenario in PLANAR_SCENARIOS:
        timing_cases = []
        timing_gate_config = stage_a_config_for_gate(
            cache=stage_a_config_cache,
            out_dir=out_dir,
            source_config=source_config,
            orientation_gate_rad=args.timing_orientation_gate_rad,
        )
        for paper_time_scale in paper_time_scales:
            case_dir = (
                out_dir
                / "groups"
                / "timing_boundary_plus1mm"
                / scenario["name"]
                / value_label("paper_time_scale", paper_time_scale)
            )
            case_dir.mkdir(parents=True, exist_ok=True)
            case = run_case(
                out_dir=case_dir,
                source_run=source_run,
                stage_a_target_config=timing_gate_config,
                group="timing_boundary_plus1mm",
                scenario=scenario,
                delta_m=boundary_delta_m,
                stage_a_duration_s=args.stage_a_duration_s,
                paper_time_scale=paper_time_scale,
                qdot_limit_rad_s=args.qdot_limit_rad_s,
                orientation_gate_rad=args.timing_orientation_gate_rad,
            )
            add_case_id(case, suffix=value_label("time", paper_time_scale))
            timing_cases.append(case)
        groups.append(
            {
                "name": "timing_boundary_plus1mm",
                "scenario": scenario["name"],
                "description": "Focused +1.0 mm faster-timing boundary under the v80 tightened gate.",
                "aggregate": aggregate_timing_cases(timing_cases),
                "cases": timing_cases,
            }
        )

        gate_cases = []
        for orientation_gate_rad in orientation_gates:
            gate_config = stage_a_config_for_gate(
                cache=stage_a_config_cache,
                out_dir=out_dir,
                source_config=source_config,
                orientation_gate_rad=orientation_gate_rad,
            )
            case_dir = (
                out_dir
                / "groups"
                / "orientation_gate_boundary_plus1mm"
                / scenario["name"]
                / value_label("orientation_gate", orientation_gate_rad)
            )
            case_dir.mkdir(parents=True, exist_ok=True)
            case = run_case(
                out_dir=case_dir,
                source_run=source_run,
                stage_a_target_config=gate_config,
                group="orientation_gate_boundary_plus1mm",
                scenario=scenario,
                delta_m=boundary_delta_m,
                stage_a_duration_s=args.stage_a_duration_s,
                paper_time_scale=args.gate_paper_time_scale,
                qdot_limit_rad_s=args.qdot_limit_rad_s,
                orientation_gate_rad=orientation_gate_rad,
            )
            add_case_id(case, suffix=value_label("gate", orientation_gate_rad))
            gate_cases.append(case)
        groups.append(
            {
                "name": "orientation_gate_boundary_plus1mm",
                "scenario": scenario["name"],
                "description": "Focused +1.0 mm tightened-gate boundary under the v80 timing.",
                "aggregate": aggregate_gate_cases(gate_cases),
                "cases": gate_cases,
            }
        )

        for stress in FULL_DELTA_STRESSES:
            stress_cases = []
            stress_config = stage_a_config_for_gate(
                cache=stage_a_config_cache,
                out_dir=out_dir,
                source_config=source_config,
                orientation_gate_rad=stress["orientation_gate_rad"],
            )
            for delta_m in deltas_m:
                case_dir = (
                    out_dir
                    / "groups"
                    / str(stress["name"])
                    / scenario["name"]
                    / label_dir(f"delta_{delta_m * 1000.0:.3f}mm")
                )
                case_dir.mkdir(parents=True, exist_ok=True)
                case = run_case(
                    out_dir=case_dir,
                    source_run=source_run,
                    stage_a_target_config=stress_config,
                    group=str(stress["name"]),
                    scenario=scenario,
                    delta_m=delta_m,
                    stage_a_duration_s=args.stage_a_duration_s,
                    paper_time_scale=stress["paper_time_scale"],
                    qdot_limit_rad_s=args.qdot_limit_rad_s,
                    orientation_gate_rad=stress["orientation_gate_rad"],
                )
                add_case_id(case, suffix=str(stress["name"]))
                stress_cases.append(case)
            groups.append(
                {
                    "name": str(stress["name"]),
                    "scenario": scenario["name"],
                    "description": stress["description"],
                    "aggregate": aggregate_cases(stress_cases),
                    "cases": stress_cases,
                }
            )

    aggregate = aggregate_all(groups)
    payload = {
        "run_id": run_id,
        "source": "v81 planar-primary Stage B priority timing and orientation stress audit",
        "source_run": str(source_run),
        "source_stage_a_target_config": str(source_config),
        "base_z_deltas_mm": [float(value * 1000.0) for value in deltas_m],
        "boundary_base_z_delta_mm": float(args.boundary_base_z_delta_mm),
        "paper_time_scales": paper_time_scales,
        "orientation_gates_rad": orientation_gates,
        "stage_a_duration_s": float(args.stage_a_duration_s),
        "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
        "timing_orientation_gate_rad": float(args.timing_orientation_gate_rad),
        "gate_paper_time_scale": float(args.gate_paper_time_scale),
        "planar_scenarios": PLANAR_SCENARIOS,
        "full_delta_stresses": FULL_DELTA_STRESSES,
        "trajectories": TRAJECTORY_ORDER,
        "aggregate": aggregate,
        "groups": groups,
        "warnings": [
            "diagnostic-label planar-priority stress audit only",
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
    write_summary(out_dir, aggregate, groups)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
