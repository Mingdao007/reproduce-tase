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
        "max_passing_paper_time_scale": max(
            (case["paper_time_scale"] for case in passing),
            default=None,
        ),
        "min_failing_paper_time_scale": min(
            (case["paper_time_scale"] for case in failing),
            default=None,
        ),
        "max_e2_orientation_error_rad": max(case["e2_orientation_error_rad"] for case in cases),
        "max_e2_qdot_saturation_fraction": max(case["e2_qdot_saturation_fraction"] for case in cases),
        "max_e2_tail_qdot_utilization": max(case["e2_tail_qdot_utilization"] for case in cases),
        "stage_a_all_passed": all(case["stage_a_passed"] for case in cases),
    }


def e2_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    for row in metrics["stage_b"]["rows"]:
        if row["trajectory"] == "e2-figure-eight":
            target = row["target_pair_metrics"]
            gate = row["feasibility_gate"]
            return {
                "e2_passed": bool(gate["feasibility_pass"]),
                "e2_failed_criteria": gate["failed_criteria"],
                "e2_orientation_error_rad": float(target["max_orientation_error_rad"]),
                "e2_qdot_saturation_fraction": float(target["qdot_saturation_fraction"]),
                "e2_tail_qdot_utilization": float(target["tail_max_qdot_utilization"]),
            }
    raise ValueError("missing e2-figure-eight row")


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    lines = [
        "# Positive Timing Boundary Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case count: `{aggregate['case_count']}`",
        f"- Stitched pass count: `{aggregate['stitched_pass_count']} / {aggregate['case_count']}`",
        f"- Max passing paper_time_scale: `{aggregate['max_passing_paper_time_scale']}`",
        f"- Min failing paper_time_scale: `{aggregate['min_failing_paper_time_scale']}`",
        f"- Stage A passed every case: `{aggregate['stage_a_all_passed']}`",
        "",
        "| paper_time_scale | stitched | Stage B pass | E2 pass | E2 orientation | E2 qdot sat | E2 tail qdot | E2 failed criteria |",
        "| ---: | --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for case in cases:
        lines.append(
            "| `{scale}` | `{stitched}` | `{handoff}/{count}` | `{e2}` | `{orientation}` | `{qdot}` | `{tail_qdot}` | `{failed}` |".format(
                scale=case["paper_time_scale"],
                stitched=case["stitched_passed"],
                handoff=case["handoff_pass_count"],
                count=case["handoff_trajectory_count"],
                e2=case["e2_passed"],
                orientation=case["e2_orientation_error_rad"],
                qdot=case["e2_qdot_saturation_fraction"],
                tail_qdot=case["e2_tail_qdot_utilization"],
                failed=",".join(case["e2_failed_criteria"]) or "none",
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The `+1.0 mm` timing boundary is primarily an E2 orientation boundary immediately above `paper_time_scale = 0.0052`.",
            "- At larger timing scales, E2 also accumulates qdot saturation and tail qdot utilization failures.",
            "- This does not change the qdot012 recovery from v75 or the tightened-orientation sensitivity limit from v73.",
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
    parser.add_argument("--paper-time-scales", default="0.005,0.0052,0.0054,0.0056,0.0058,0.006,0.0065,0.007,0.0075")
    parser.add_argument("--stage-a-duration-s", type=float, default=15.0)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--max-orientation-error-rad", type=float, default=0.12)
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    delta_m = float(args.base_z_delta_mm) / 1000.0
    paper_time_scales = parse_float_list(args.paper_time_scales)
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "positive_timing_boundary" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = []
    for paper_time_scale in paper_time_scales:
        case_dir = out_dir / "cases" / f"paper_time_scale_{str(paper_time_scale).replace('.', 'p')}"
        case_dir.mkdir(parents=True, exist_ok=True)
        metrics = run_child(
            stitched_command(
                out_dir=case_dir,
                source_run=source_run,
                delta_m=delta_m,
                stage_a_duration_s=args.stage_a_duration_s,
                paper_time_scale=paper_time_scale,
                qdot_limit_rad_s=args.qdot_limit_rad_s,
                max_orientation_error_rad=args.max_orientation_error_rad,
            ),
            out_dir=case_dir,
        )
        case = summarize_case(delta_m, metrics)
        case["paper_time_scale"] = float(paper_time_scale)
        case.update(e2_metrics(metrics))
        cases.append(case)

    aggregate = aggregate_cases(cases)
    payload = {
        "run_id": run_id,
        "source": "v76 focused +1.0 mm positive timing boundary audit",
        "source_run": str(source_run),
        "relaxed_stage_a_target_config": str(source_run / "relaxed_stage_a_target_config.yaml"),
        "base_z_offset_delta_m": delta_m,
        "base_z_offset_delta_mm": float(args.base_z_delta_mm),
        "stage_a_duration_s": float(args.stage_a_duration_s),
        "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
        "max_orientation_error_rad": float(args.max_orientation_error_rad),
        "trajectories": TRAJECTORY_ORDER,
        "aggregate": aggregate,
        "cases": cases,
        "warnings": [
            "diagnostic-label +1.0 mm timing boundary audit only",
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
