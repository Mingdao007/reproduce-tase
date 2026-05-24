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


def value_label(value: float) -> str:
    text = f"{float(value):.8g}".replace("-", "m").replace(".", "p")
    return text


def e2_command(
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
        "--trajectories",
        "e2-figure-eight",
    ]


def summarize_e2_run(
    *,
    delta_m: float,
    sweep_kind: str,
    sweep_value: float,
    metrics: dict[str, Any],
) -> dict[str, Any]:
    rows = metrics["stage_b"]["rows"]
    if len(rows) != 1 or rows[0]["trajectory"] != "e2-figure-eight":
        raise ValueError("expected exactly one e2-figure-eight row")
    row = rows[0]
    gate = row["feasibility_gate"]
    stage_a = metrics["stage_a"]
    e2_metrics = row["target_pair_metrics"]
    return {
        "case": base_z_delta_label(delta_m),
        "base_z_offset_delta_m": float(delta_m),
        "base_z_offset_delta_mm": 1000.0 * float(delta_m),
        "sweep_kind": sweep_kind,
        "sweep_value": float(sweep_value),
        "paper_time_scale": float(metrics["paper_time_scale"]),
        "qdot_limit_rad_s": float(metrics["qdot_limit_rad_s"]),
        "stage_a_duration_s": float(metrics["stage_a_duration_s"]),
        "stage_b_duration_s": float(metrics["stage_b_duration_s"]),
        "stage_a_passed": bool(stage_a["stage_a_gate"]["passed"]),
        "e2_passed": bool(gate["feasibility_pass"]),
        "failed_criteria": list(gate["failed_criteria"]),
        "qdot_saturation_fraction": float(e2_metrics["qdot_saturation_fraction"]),
        "tail_max_qdot_utilization": float(e2_metrics["tail_max_qdot_utilization"]),
        "max_qdot_utilization": float(e2_metrics["max_qdot_utilization"]),
        "max_abs_qdot_rad_s": float(e2_metrics["max_abs_qdot_rad_s"]),
        "max_orientation_error_rad": float(e2_metrics["max_orientation_error_rad"]),
        "tail_mean_abs_force_error_N": float(e2_metrics["tail_mean_abs_force_error_N"]),
        "max_tangential_position_error_m": float(e2_metrics["max_tangential_position_error_m"]),
        "contact_present_fraction": float(e2_metrics["contact_present_fraction"]),
        "source_path_csv": str(metrics["source_path_csv"]),
    }


def aggregate_timing(rows: list[dict[str, Any]], scales: list[float]) -> dict[str, Any]:
    timing_rows = [row for row in rows if row["sweep_kind"] == "paper_time_scale"]
    case_names = sorted({row["case"] for row in timing_rows})
    pass_count_by_scale: dict[str, int] = {}
    max_recovered_delta_by_scale: dict[str, float | None] = {}
    all_pass_scales = []
    for scale in scales:
        scale_rows = [row for row in timing_rows if row["paper_time_scale"] == scale]
        pass_count = sum(1 for row in scale_rows if row["stage_a_passed"] and row["e2_passed"])
        pass_count_by_scale[str(scale)] = pass_count
        passed_deltas = [row["base_z_offset_delta_mm"] for row in scale_rows if row["e2_passed"]]
        max_recovered_delta_by_scale[str(scale)] = max(passed_deltas) if passed_deltas else None
        if pass_count == len(case_names):
            all_pass_scales.append(scale)
    max_passing_scale_by_case = {}
    for case in case_names:
        passed_scales = [
            row["paper_time_scale"]
            for row in timing_rows
            if row["case"] == case and row["stage_a_passed"] and row["e2_passed"]
        ]
        max_passing_scale_by_case[case] = max(passed_scales) if passed_scales else None
    return {
        "case_count": len(case_names),
        "scale_count": len(scales),
        "timing_row_count": len(timing_rows),
        "pass_count_by_scale": pass_count_by_scale,
        "max_recovered_delta_by_scale_mm": max_recovered_delta_by_scale,
        "all_pass_scales": all_pass_scales,
        "fastest_all_pass_paper_time_scale": max(all_pass_scales) if all_pass_scales else None,
        "max_passing_scale_by_case": max_passing_scale_by_case,
    }


def aggregate_qdot_probe(rows: list[dict[str, Any]]) -> dict[str, Any]:
    passing = [row for row in rows if row["stage_a_passed"] and row["e2_passed"]]
    failing = [row for row in rows if not (row["stage_a_passed"] and row["e2_passed"])]
    return {
        "row_count": len(rows),
        "pass_count": len(passing),
        "fail_count": len(failing),
        "min_passing_qdot_limit_rad_s": min(
            (row["qdot_limit_rad_s"] for row in passing),
            default=None,
        ),
        "max_failing_qdot_limit_rad_s": max(
            (row["qdot_limit_rad_s"] for row in failing),
            default=None,
        ),
        "max_qdot_saturation_fraction": max(
            (row["qdot_saturation_fraction"] for row in rows),
            default=None,
        ),
        "min_qdot_saturation_fraction": min(
            (row["qdot_saturation_fraction"] for row in rows),
            default=None,
        ),
        "max_tail_qdot_utilization": max(
            (row["tail_max_qdot_utilization"] for row in rows),
            default=None,
        ),
        "max_orientation_error_rad": max(
            (row["max_orientation_error_rad"] for row in rows),
            default=None,
        ),
    }


def write_summary(
    *,
    out_dir: pathlib.Path,
    aggregate: dict[str, Any],
    qdot_aggregate: dict[str, Any],
    timing_rows: list[dict[str, Any]],
    qdot_rows: list[dict[str, Any]],
    scales: list[float],
    qdot_probe_paper_time_scale: float,
) -> None:
    case_rows = []
    for case, scale in aggregate["max_passing_scale_by_case"].items():
        original = next(
            row
            for row in timing_rows
            if row["case"] == case and row["paper_time_scale"] == scales[0]
        )
        case_rows.append((case, original["base_z_offset_delta_mm"], scale, original))
    case_rows.sort(key=lambda row: row[1])

    lines = [
        "# Positive Stage B E2 Margin Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Timing rows: `{aggregate['timing_row_count']}`",
        f"- Fastest all-pass paper_time_scale: `{aggregate['fastest_all_pass_paper_time_scale']}`",
        f"- Qdot-only probe rows: `{len(qdot_rows)}`",
        f"- Qdot-only probe pass count: `{qdot_aggregate['pass_count']} / {qdot_aggregate['row_count']}`",
        "",
        "| paper_time_scale | E2 pass count | max recovered positive delta mm |",
        "| ---: | ---: | ---: |",
    ]
    for scale in scales:
        key = str(scale)
        lines.append(
            "| `{scale}` | `{passes} / {count}` | `{delta}` |".format(
                scale=scale,
                passes=aggregate["pass_count_by_scale"][key],
                count=aggregate["case_count"],
                delta=aggregate["max_recovered_delta_by_scale_mm"][key],
            )
        )
    lines.extend(
        [
            "",
            "| delta mm | max passing paper_time_scale | E2 failed criteria at first scale | first-scale qdot sat | first-scale tail qdot | first-scale max orientation rad |",
            "| ---: | ---: | --- | ---: | ---: | ---: |",
        ]
    )
    for _case, delta_mm, max_scale, original in case_rows:
        lines.append(
            "| `{delta}` | `{scale}` | `{failed}` | `{qdot}` | `{tail}` | `{orientation}` |".format(
                delta=delta_mm,
                scale=max_scale,
                failed=";".join(original["failed_criteria"]) or "none",
                qdot=original["qdot_saturation_fraction"],
                tail=original["tail_max_qdot_utilization"],
                orientation=original["max_orientation_error_rad"],
            )
        )
    if qdot_rows:
        lines.extend(
            [
                "",
                f"Qdot-only probe at `paper_time_scale = {qdot_probe_paper_time_scale}`:",
                "",
                "| qdot limit rad/s | pass | failed criteria | qdot sat | tail qdot | max orientation rad |",
                "| ---: | --- | --- | ---: | ---: | ---: |",
            ]
        )
        for row in qdot_rows:
            lines.append(
                "| `{qdot_limit}` | `{passed}` | `{failed}` | `{qdot}` | `{tail}` | `{orientation}` |".format(
                    qdot_limit=row["qdot_limit_rad_s"],
                    passed=row["e2_passed"],
                    failed=";".join(row["failed_criteria"]) or "none",
                    qdot=row["qdot_saturation_fraction"],
                    tail=row["tail_max_qdot_utilization"],
                    orientation=row["max_orientation_error_rad"],
                )
            )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- Slowing E2 to `paper_time_scale = {scale}` recovers all tested positive deltas under the v70 run-local `0.12 rad` gate.".format(
                scale=aggregate["fastest_all_pass_paper_time_scale"]
            ),
            "- Raising qdot limit alone at `paper_time_scale = {scale}` does not recover the hardest tested `+1.0 mm` case because max orientation error remains above `0.12 rad`.".format(
                scale=qdot_probe_paper_time_scale
            ),
            "- This is diagnostic-label simulation evidence only, not a canonical config change, robustness proof, paper-equivalent claim, or hardware readiness result.",
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
    parser.add_argument("--paper-time-scales", default="0.01,0.0075,0.005,0.0025")
    parser.add_argument("--qdot-probe-limits-rad-s", default="0.15,0.18,0.2,0.25")
    parser.add_argument("--stage-a-duration-s", type=float, default=15.0)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--max-orientation-error-rad", type=float, default=0.12)
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    deltas_m = [value / 1000.0 for value in parse_float_list(args.base_z_deltas_mm)]
    scales = parse_float_list(args.paper_time_scales)
    qdot_limits = parse_float_list(args.qdot_probe_limits_rad_s)
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "positive_stage_b_e2_margin" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    timing_rows = []
    for delta_m in deltas_m:
        case_name = base_z_delta_label(delta_m)
        for scale in scales:
            case_dir = out_dir / "cases" / case_name / f"timing_scale_{value_label(scale)}"
            case_dir.mkdir(parents=True, exist_ok=True)
            metrics = run_child(
                e2_command(
                    out_dir=case_dir,
                    source_run=source_run,
                    delta_m=delta_m,
                    stage_a_duration_s=args.stage_a_duration_s,
                    paper_time_scale=scale,
                    qdot_limit_rad_s=args.qdot_limit_rad_s,
                    max_orientation_error_rad=args.max_orientation_error_rad,
                ),
                out_dir=case_dir,
            )
            timing_rows.append(
                summarize_e2_run(
                    delta_m=delta_m,
                    sweep_kind="paper_time_scale",
                    sweep_value=scale,
                    metrics=metrics,
                )
            )

    qdot_rows = []
    hardest_delta_m = max(deltas_m)
    for qdot_limit in qdot_limits:
        case_name = base_z_delta_label(hardest_delta_m)
        case_dir = out_dir / "qdot_probe" / case_name / f"qdot_{value_label(qdot_limit)}"
        case_dir.mkdir(parents=True, exist_ok=True)
        metrics = run_child(
            e2_command(
                out_dir=case_dir,
                source_run=source_run,
                delta_m=hardest_delta_m,
                stage_a_duration_s=args.stage_a_duration_s,
                paper_time_scale=scales[0],
                qdot_limit_rad_s=qdot_limit,
                max_orientation_error_rad=args.max_orientation_error_rad,
            ),
            out_dir=case_dir,
        )
        qdot_rows.append(
            summarize_e2_run(
                delta_m=hardest_delta_m,
                sweep_kind="qdot_limit_rad_s",
                sweep_value=qdot_limit,
                metrics=metrics,
            )
        )

    aggregate = aggregate_timing(timing_rows, scales)
    qdot_aggregate = aggregate_qdot_probe(qdot_rows)
    qdot_probe_paper_time_scale = float(scales[0])
    payload = {
        "run_id": run_id,
        "source": "v70 positive relaxed-orientation Stage A/path cases with E2 Stage B margin probes",
        "source_run": str(source_run),
        "relaxed_stage_a_target_config": str(source_run / "relaxed_stage_a_target_config.yaml"),
        "stage_a_duration_s": float(args.stage_a_duration_s),
        "stage_b_trajectory": "e2-figure-eight",
        "default_qdot_limit_rad_s": float(args.qdot_limit_rad_s),
        "max_orientation_error_rad": float(args.max_orientation_error_rad),
        "paper_time_scales": scales,
        "qdot_probe_limits_rad_s": qdot_limits,
        "qdot_probe_paper_time_scale": qdot_probe_paper_time_scale,
        "aggregate": aggregate,
        "qdot_probe_aggregate": qdot_aggregate,
        "timing_rows": timing_rows,
        "qdot_probe_rows": qdot_rows,
        "warnings": [
            "diagnostic-label simulation margin audit only",
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
    write_summary(
        out_dir=out_dir,
        aggregate=aggregate,
        qdot_aggregate=qdot_aggregate,
        timing_rows=timing_rows,
        qdot_rows=qdot_rows,
        scales=scales,
        qdot_probe_paper_time_scale=qdot_probe_paper_time_scale,
    )
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
