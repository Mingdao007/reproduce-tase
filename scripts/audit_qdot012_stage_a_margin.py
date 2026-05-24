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


def aggregate_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    passing = [case for case in cases if case["stitched_passed"]]
    failing = [case for case in cases if not case["stitched_passed"]]
    return {
        "case_count": len(cases),
        "stitched_pass_count": len(passing),
        "stitched_fail_count": len(failing),
        "first_passing_stage_a_duration_s": min(
            (case["stage_a_duration_s"] for case in passing),
            default=None,
        ),
        "last_failing_stage_a_duration_s": max(
            (case["stage_a_duration_s"] for case in failing),
            default=None,
        ),
        "min_passing_stage_a_max_qdot_rad_s": min(
            (case["stage_a_max_qdot_rad_s"] for case in passing),
            default=None,
        ),
        "min_passing_stage_a_final_tracking_error_norm_rad": min(
            (case["stage_a_final_tracking_error_norm_rad"] for case in passing),
            default=None,
        ),
        "max_failing_stage_a_final_tracking_error_norm_rad": max(
            (case["stage_a_final_tracking_error_norm_rad"] for case in failing),
            default=None,
        ),
        "all_passing_stage_b_counts": all(
            case["handoff_pass_count"] == case["handoff_trajectory_count"] for case in cases
        ),
    }


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    lines = [
        "# Qdot012 Stage A Duration Margin Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case count: `{aggregate['case_count']}`",
        f"- Stitched pass count: `{aggregate['stitched_pass_count']} / {aggregate['case_count']}`",
        f"- Last failing Stage A duration s: `{aggregate['last_failing_stage_a_duration_s']}`",
        f"- First passing Stage A duration s: `{aggregate['first_passing_stage_a_duration_s']}`",
        f"- All Stage B rows pass in every case: `{aggregate['all_passing_stage_b_counts']}`",
        "",
        "| Stage A duration s | stitched | Stage A | Stage B pass | Stage A max qdot | final tracking error | failed Stage A criteria | failed Stage B rows |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for case in cases:
        failed_stage_b = ";".join(
            f"{row['trajectory']}:{','.join(row['failed_criteria'])}"
            for row in case["stage_b_failed_rows"]
        )
        lines.append(
            "| `{duration}` | `{stitched}` | `{stage_a}` | `{handoff}/{count}` | `{qdot}` | `{tracking}` | `{stage_a_failed}` | `{stage_b_failed}` |".format(
                duration=case["stage_a_duration_s"],
                stitched=case["stitched_passed"],
                stage_a=case["stage_a_passed"],
                handoff=case["handoff_pass_count"],
                count=case["handoff_trajectory_count"],
                qdot=case["stage_a_max_qdot_rad_s"],
                tracking=case["stage_a_final_tracking_error_norm_rad"],
                stage_a_failed=",".join(case["stage_a_failed_criteria"]) or "none",
                stage_b_failed=failed_stage_b or "none",
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The v73 `qdot012_stage_a18s` `+0.2 mm` failure is a narrow Stage A duration margin, not a Stage B handoff failure.",
            "- Extending Stage A from `18.03 s` to `18.035 s` recovers the failing cell in this diagnostic setup.",
            "- This does not change the faster-timing or tighter-orientation sensitivity limits from v73.",
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
    parser.add_argument("--base-z-delta-mm", type=float, default=0.2)
    parser.add_argument("--stage-a-durations-s", default="18.0,18.01,18.02,18.03,18.035,18.04,18.05")
    parser.add_argument("--paper-time-scale", type=float, default=0.005)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.12)
    parser.add_argument("--max-orientation-error-rad", type=float, default=0.12)
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    delta_m = float(args.base_z_delta_mm) / 1000.0
    durations_s = parse_float_list(args.stage_a_durations_s)
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "qdot012_stage_a_margin" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = []
    for duration_s in durations_s:
        case_dir = out_dir / "cases" / f"stage_a_{str(duration_s).replace('.', 'p')}s"
        case_dir.mkdir(parents=True, exist_ok=True)
        metrics = run_child(
            stitched_command(
                out_dir=case_dir,
                source_run=source_run,
                delta_m=delta_m,
                stage_a_duration_s=duration_s,
                paper_time_scale=args.paper_time_scale,
                qdot_limit_rad_s=args.qdot_limit_rad_s,
                max_orientation_error_rad=args.max_orientation_error_rad,
            ),
            out_dir=case_dir,
        )
        case = summarize_case(delta_m, metrics)
        case["stage_a_duration_s"] = float(duration_s)
        cases.append(case)

    aggregate = aggregate_cases(cases)
    payload = {
        "run_id": run_id,
        "source": "v74 focused qdot012 Stage A duration margin audit for the v73 +0.2 mm failure",
        "source_run": str(source_run),
        "relaxed_stage_a_target_config": str(source_run / "relaxed_stage_a_target_config.yaml"),
        "base_z_offset_delta_m": delta_m,
        "base_z_offset_delta_mm": float(args.base_z_delta_mm),
        "paper_time_scale": float(args.paper_time_scale),
        "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
        "max_orientation_error_rad": float(args.max_orientation_error_rad),
        "trajectories": TRAJECTORY_ORDER,
        "aggregate": aggregate,
        "cases": cases,
        "warnings": [
            "diagnostic-label qdot012 Stage A duration margin audit only",
            "uses the v70 run-local relaxed orientation target config",
            "not a canonical config change",
            "not strict paper-equivalent feasibility",
            "not a formal robustness proof",
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
