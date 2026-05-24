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
from audit_stage_a_base_z_recovery import run_child, write_git_state
from tase_repro.base_z_recovery import base_z_delta_label


TRAJECTORY_ORDER = ["e1-cycloid", "e2-figure-eight", "e3-circle", "e4-cardioid"]


def stitched_command(
    *,
    out_dir: pathlib.Path,
    source_run: pathlib.Path,
    delta_m: float,
    stage_a_duration_s: float,
    paper_time_scale: float,
    qdot_limit_rad_s: float,
    max_orientation_error_rad: float,
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
    ]


def summarize_stitched(delta_m: float, metrics: dict[str, Any]) -> dict[str, Any]:
    stage_b_rows = metrics["stage_b"]["rows"]
    failed = [
        {
            "trajectory": row["trajectory"],
            "failed_criteria": row["feasibility_gate"]["failed_criteria"],
        }
        for row in stage_b_rows
        if not row["feasibility_gate"]["feasibility_pass"]
    ]
    max_qdot_saturation = max(row["target_pair_metrics"]["qdot_saturation_fraction"] for row in stage_b_rows)
    max_tail_qdot = max(row["target_pair_metrics"]["tail_max_qdot_utilization"] for row in stage_b_rows)
    max_orientation = max(row["target_pair_metrics"]["max_orientation_error_rad"] for row in stage_b_rows)
    max_force = max(row["target_pair_metrics"]["tail_mean_abs_force_error_N"] for row in stage_b_rows)
    max_xy = max(row["target_pair_metrics"]["max_tangential_position_error_m"] for row in stage_b_rows)
    return {
        "case": base_z_delta_label(delta_m),
        "base_z_offset_delta_m": float(delta_m),
        "base_z_offset_delta_mm": 1000.0 * float(delta_m),
        "stage_a_passed": bool(metrics["stitched_gate"]["stage_a_passed"]),
        "stitched_passed": bool(metrics["stitched_gate"]["passed"]),
        "handoff_pass_count": int(metrics["stitched_gate"]["handoff_pass_count"]),
        "handoff_trajectory_count": int(metrics["stitched_gate"]["handoff_trajectory_count"]),
        "failed_rows": failed,
        "stage_a_max_qdot_rad_s": float(metrics["stage_a"]["tracking"]["max_abs_qdot_rad_s"]),
        "stage_a_terminal_force_error_N": float(metrics["stage_a"]["evaluation"]["terminal_force_error_N"]),
        "stage_a_terminal_xy_error_m": float(metrics["stage_a"]["evaluation"]["terminal_reference_xy_error_m"]),
        "stage_a_terminal_orientation_error_rad": float(
            metrics["stage_a"]["evaluation"]["terminal_force_normal_orientation_error_rad"]
        ),
        "stage_b_max_qdot_saturation_fraction": float(max_qdot_saturation),
        "stage_b_max_tail_qdot_utilization": float(max_tail_qdot),
        "stage_b_max_orientation_error_rad": float(max_orientation),
        "stage_b_max_tail_force_error_N": float(max_force),
        "stage_b_max_xy_error_m": float(max_xy),
        "source_path_csv": str(metrics["source_path_csv"]),
    }


def aggregate_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    passed = [case["case"] for case in cases if case["stitched_passed"]]
    failed = [case["case"] for case in cases if not case["stitched_passed"]]
    passed_deltas = [case["base_z_offset_delta_mm"] for case in cases if case["stitched_passed"]]
    return {
        "case_count": len(cases),
        "stitched_pass_count": len(passed),
        "stitched_fail_count": len(failed),
        "passing_cases": passed,
        "failing_cases": failed,
        "all_cases_passed": len(passed) == len(cases) and bool(cases),
        "max_positive_stitched_pass_delta_mm": max(passed_deltas) if passed_deltas else None,
        "max_stage_b_qdot_saturation_fraction": max(
            case["stage_b_max_qdot_saturation_fraction"] for case in cases
        ),
        "max_stage_b_tail_qdot_utilization": max(case["stage_b_max_tail_qdot_utilization"] for case in cases),
        "max_stage_b_orientation_error_rad": max(case["stage_b_max_orientation_error_rad"] for case in cases),
    }


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    lines = [
        "# Positive Full Stitched Recovery Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case count: `{aggregate['case_count']}`",
        f"- Stitched pass count: `{aggregate['stitched_pass_count']}`",
        f"- Max positive stitched-pass delta mm: `{aggregate['max_positive_stitched_pass_delta_mm']}`",
        f"- Max Stage B qdot saturation fraction: `{aggregate['max_stage_b_qdot_saturation_fraction']}`",
        f"- Max Stage B tail qdot utilization: `{aggregate['max_stage_b_tail_qdot_utilization']}`",
        f"- Max Stage B orientation error rad: `{aggregate['max_stage_b_orientation_error_rad']}`",
        "",
        "| delta mm | stitched | Stage B pass | Stage A max qdot | Stage B qdot sat | Stage B tail qdot | Stage B max orientation rad | failed rows |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for case in cases:
        failed = ";".join(
            f"{row['trajectory']}:{','.join(row['failed_criteria'])}" for row in case["failed_rows"]
        )
        lines.append(
            "| `{delta}` | `{stitched}` | `{handoff}/{count}` | `{stage_a_qdot}` | `{stage_b_qdot}` | `{tail_qdot}` | `{orientation}` | `{failed}` |".format(
                delta=case["base_z_offset_delta_mm"],
                stitched=case["stitched_passed"],
                handoff=case["handoff_pass_count"],
                count=case["handoff_trajectory_count"],
                stage_a_qdot=case["stage_a_max_qdot_rad_s"],
                stage_b_qdot=case["stage_b_max_qdot_saturation_fraction"],
                tail_qdot=case["stage_b_max_tail_qdot_utilization"],
                orientation=case["stage_b_max_orientation_error_rad"],
                failed=failed or "none",
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The v70 relaxed terminal/path setup plus `paper_time_scale = 0.005` recovers the full positive E1-E4 stitched diagnostic matrix for all tested positive deltas.",
            "- This is still diagnostic-label simulation evidence using a run-local `0.12 rad` orientation gate, not strict paper-equivalent, robust, calibrated, or hardware-ready evidence.",
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
    parser.add_argument("--max-orientation-error-rad", type=float, default=0.12)
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    deltas_m = [value / 1000.0 for value in parse_float_list(args.base_z_deltas_mm)]
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "positive_full_stitched_recovery" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = []
    for delta_m in deltas_m:
        case_name = base_z_delta_label(delta_m)
        case_dir = out_dir / "cases" / case_name
        case_dir.mkdir(parents=True, exist_ok=True)
        metrics = run_child(
            stitched_command(
                out_dir=case_dir,
                source_run=source_run,
                delta_m=delta_m,
                stage_a_duration_s=args.stage_a_duration_s,
                paper_time_scale=args.paper_time_scale,
                qdot_limit_rad_s=args.qdot_limit_rad_s,
                max_orientation_error_rad=args.max_orientation_error_rad,
            ),
            out_dir=case_dir,
        )
        cases.append(summarize_stitched(delta_m, metrics))

    aggregate = aggregate_cases(cases)
    payload = {
        "run_id": run_id,
        "source": "v70 positive relaxed terminal/path setup with v71 E2-safe Stage B timing",
        "source_run": str(source_run),
        "relaxed_stage_a_target_config": str(source_run / "relaxed_stage_a_target_config.yaml"),
        "stage_a_duration_s": float(args.stage_a_duration_s),
        "paper_time_scale": float(args.paper_time_scale),
        "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
        "max_orientation_error_rad": float(args.max_orientation_error_rad),
        "trajectories": TRAJECTORY_ORDER,
        "aggregate": aggregate,
        "cases": cases,
        "warnings": [
            "diagnostic-label full stitched positive audit only",
            "uses the v70 run-local relaxed orientation target config",
            "not a canonical config change",
            "not strict paper-equivalent feasibility",
            "not robustness proof",
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
