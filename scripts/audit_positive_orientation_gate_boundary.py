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


def gate_label(value: float) -> str:
    return f"orientation_gate_{value:.6f}".rstrip("0").rstrip(".").replace(".", "p")


def write_stage_a_config(
    *,
    out_dir: pathlib.Path,
    source_config: pathlib.Path,
    orientation_gate_rad: float,
) -> pathlib.Path:
    config = yaml.safe_load(source_config.read_text(encoding="utf-8"))
    target = config["selected_stage_a_target"]
    target["diagnostic_gate"]["max_terminal_orientation_error_rad"] = float(orientation_gate_rad)
    config["v77_positive_orientation_gate_boundary_scope"] = {
        "source_config": str(source_config),
        "max_terminal_orientation_error_rad": float(orientation_gate_rad),
        "claim_scope": "run-local orientation-gate boundary config only",
    }
    if "v70_relaxed_orientation_scope" in config:
        config["v70_relaxed_orientation_scope"]["max_terminal_orientation_error_rad"] = float(
            orientation_gate_rad
        )

    config_dir = out_dir / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    gate_config = config_dir / f"{gate_label(orientation_gate_rad)}_stage_a_target_config.yaml"
    with gate_config.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)
    return gate_config


def stitched_command(
    *,
    out_dir: pathlib.Path,
    source_run: pathlib.Path,
    stage_a_target_config: pathlib.Path,
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
        str(stage_a_target_config),
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


def stage_b_orientation_rows(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in metrics["stage_b"]["rows"]:
        target = row["target_pair_metrics"]
        gate = row["feasibility_gate"]
        rows.append(
            {
                "trajectory": row["trajectory"],
                "passed": bool(gate["feasibility_pass"]),
                "failed_criteria": gate["failed_criteria"],
                "orientation_error_rad": float(target["max_orientation_error_rad"]),
            }
        )
    return rows


def aggregate_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    passing = [case for case in cases if case["stitched_passed"]]
    failing = [case for case in cases if not case["stitched_passed"]]
    return {
        "case_count": len(cases),
        "stitched_pass_count": len(passing),
        "stitched_fail_count": len(failing),
        "min_passing_orientation_gate_rad": min(
            (case["orientation_gate_rad"] for case in passing),
            default=None,
        ),
        "max_failing_orientation_gate_rad": max(
            (case["orientation_gate_rad"] for case in failing),
            default=None,
        ),
        "max_stage_a_terminal_orientation_error_rad": max(
            case["stage_a_terminal_orientation_error_rad"] for case in cases
        ),
        "max_stage_b_orientation_error_rad": max(case["stage_b_max_orientation_error_rad"] for case in cases),
        "stage_a_all_passed": all(case["stage_a_passed"] for case in cases),
    }


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    lines = [
        "# Positive Orientation Gate Boundary Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case count: `{aggregate['case_count']}`",
        f"- Stitched pass count: `{aggregate['stitched_pass_count']} / {aggregate['case_count']}`",
        f"- Max failing orientation gate: `{aggregate['max_failing_orientation_gate_rad']}`",
        f"- Min passing orientation gate: `{aggregate['min_passing_orientation_gate_rad']}`",
        f"- Stage A passed every case: `{aggregate['stage_a_all_passed']}`",
        "",
        "| orientation gate | stitched | Stage A | Stage B pass | Stage A orientation | Max Stage B orientation | failed rows |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for case in cases:
        failed_rows = [
            f"{row['trajectory']}:{','.join(row['failed_criteria'])}"
            for row in case["stage_b_orientation_rows"]
            if row["failed_criteria"]
        ]
        lines.append(
            "| `{gate}` | `{stitched}` | `{stage_a}` | `{handoff}/{count}` | `{stage_a_orientation}` | `{stage_b_orientation}` | `{failed}` |".format(
                gate=case["orientation_gate_rad"],
                stitched=case["stitched_passed"],
                stage_a=case["stage_a_passed"],
                handoff=case["handoff_pass_count"],
                count=case["handoff_trajectory_count"],
                stage_a_orientation=case["stage_a_terminal_orientation_error_rad"],
                stage_b_orientation=case["stage_b_max_orientation_error_rad"],
                failed="; ".join(failed_rows) or "none",
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The `+1.0 mm` tightened-orientation boundary is controlled by the maximum Stage B orientation error under the v72 timing.",
            "- Stage A passes once the gate is above the terminal orientation value, but stitched recovery still needs the Stage B maximum to fit.",
            "- This does not change the v75 qdot012 recovery or the v76 faster-timing boundary.",
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
    parser.add_argument(
        "--orientation-gates",
        default="0.119,0.11925,0.1195,0.11975,0.1199,0.11995,0.11997,0.11998,0.12",
    )
    parser.add_argument("--stage-a-duration-s", type=float, default=15.0)
    parser.add_argument("--paper-time-scale", type=float, default=0.005)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    source_config = source_run / "relaxed_stage_a_target_config.yaml"
    delta_m = float(args.base_z_delta_mm) / 1000.0
    orientation_gates = parse_float_list(args.orientation_gates)
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "positive_orientation_gate_boundary" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = []
    for orientation_gate_rad in orientation_gates:
        label = gate_label(orientation_gate_rad)
        case_dir = out_dir / "cases" / label
        case_dir.mkdir(parents=True, exist_ok=True)
        gate_config = write_stage_a_config(
            out_dir=out_dir,
            source_config=source_config,
            orientation_gate_rad=orientation_gate_rad,
        )
        metrics = run_child(
            stitched_command(
                out_dir=case_dir,
                source_run=source_run,
                stage_a_target_config=gate_config,
                delta_m=delta_m,
                stage_a_duration_s=args.stage_a_duration_s,
                paper_time_scale=args.paper_time_scale,
                qdot_limit_rad_s=args.qdot_limit_rad_s,
                max_orientation_error_rad=orientation_gate_rad,
            ),
            out_dir=case_dir,
        )
        case = summarize_case(delta_m, metrics)
        case["orientation_gate_rad"] = float(orientation_gate_rad)
        case["stage_a_target_config"] = str(gate_config)
        case["stage_b_orientation_rows"] = stage_b_orientation_rows(metrics)
        cases.append(case)

    aggregate = aggregate_cases(cases)
    payload = {
        "run_id": run_id,
        "source": "v77 focused +1.0 mm positive orientation-gate boundary audit",
        "source_run": str(source_run),
        "base_z_offset_delta_m": delta_m,
        "base_z_offset_delta_mm": float(args.base_z_delta_mm),
        "stage_a_duration_s": float(args.stage_a_duration_s),
        "paper_time_scale": float(args.paper_time_scale),
        "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
        "orientation_gates_rad": orientation_gates,
        "trajectories": TRAJECTORY_ORDER,
        "aggregate": aggregate,
        "cases": cases,
        "warnings": [
            "diagnostic-label +1.0 mm orientation-gate boundary audit only",
            "uses run-local copied Stage A target configs",
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
