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


TRAJECTORY = "e2-figure-eight"


def value_label(prefix: str, value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".").replace(".", "p")
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
    config["v78_stage_b_orientation_kp_probe_scope"] = {
        "source_config": str(source_config),
        "max_terminal_orientation_error_rad": float(orientation_gate_rad),
        "claim_scope": "run-local Stage A orientation gate for Stage B kp probe only",
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


def stitched_command(
    *,
    out_dir: pathlib.Path,
    source_run: pathlib.Path,
    stage_a_target_config: pathlib.Path,
    delta_m: float,
    stage_a_duration_s: float,
    paper_time_scale: float,
    qdot_limit_rad_s: float,
    orientation_kp: float,
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
        "--orientation-kp",
        f"{float(orientation_kp):.17g}",
        "--max-orientation-error-rad",
        f"{float(max_orientation_error_rad):.17g}",
        "--trajectories",
        TRAJECTORY,
    ]


def e2_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    for row in metrics["stage_b"]["rows"]:
        if row["trajectory"] == TRAJECTORY:
            target = row["target_pair_metrics"]
            gate = row["feasibility_gate"]
            return {
                "e2_passed": bool(gate["feasibility_pass"]),
                "e2_failed_criteria": gate["failed_criteria"],
                "e2_orientation_error_rad": float(target["max_orientation_error_rad"]),
                "e2_qdot_saturation_fraction": float(target["qdot_saturation_fraction"]),
                "e2_tail_qdot_utilization": float(target["tail_max_qdot_utilization"]),
                "e2_max_angular_velocity_slack_rad_s": float(
                    target["max_angular_velocity_slack_rad_s"]
                ),
                "e2_tail_force_error_N": float(target["tail_mean_abs_force_error_N"]),
                "e2_max_xy_error_m": float(target["max_tangential_position_error_m"]),
            }
    raise ValueError(f"missing {TRAJECTORY} row")


def aggregate_cases(cases: list[dict[str, Any]], *, orientation_gate_rad: float) -> dict[str, Any]:
    passing = [case for case in cases if case["stitched_passed"]]
    orientation_ok = [
        case for case in cases if case["e2_orientation_error_rad"] <= orientation_gate_rad + 1e-12
    ]
    stage_a_passed = [case for case in cases if case["stage_a_passed"]]
    orientation_sorted = sorted(cases, key=lambda case: case["e2_orientation_error_rad"])
    qdot_sorted = sorted(cases, key=lambda case: case["e2_qdot_saturation_fraction"])
    return {
        "case_count": len(cases),
        "stitched_pass_count": len(passing),
        "stitched_fail_count": len(cases) - len(passing),
        "stage_a_pass_count": len(stage_a_passed),
        "stage_a_all_passed": len(stage_a_passed) == len(cases) and bool(cases),
        "orientation_ok_count": len(orientation_ok),
        "min_e2_orientation_error_rad": min(
            (case["e2_orientation_error_rad"] for case in cases),
            default=None,
        ),
        "min_e2_qdot_saturation_fraction": min(
            (case["e2_qdot_saturation_fraction"] for case in cases),
            default=None,
        ),
        "min_e2_tail_qdot_utilization": min(
            (case["e2_tail_qdot_utilization"] for case in cases),
            default=None,
        ),
        "best_orientation_case": orientation_sorted[0] if orientation_sorted else None,
        "best_qdot_saturation_case": qdot_sorted[0] if qdot_sorted else None,
        "orientation_ok_cases": [
            {
                "qdot_limit_rad_s": case["qdot_limit_rad_s"],
                "orientation_kp": case["orientation_kp"],
                "e2_failed_criteria": case["e2_failed_criteria"],
                "e2_orientation_error_rad": case["e2_orientation_error_rad"],
                "e2_qdot_saturation_fraction": case["e2_qdot_saturation_fraction"],
                "e2_tail_qdot_utilization": case["e2_tail_qdot_utilization"],
            }
            for case in orientation_ok
        ],
    }


def write_summary(
    *,
    out_dir: pathlib.Path,
    aggregate: dict[str, Any],
    cases: list[dict[str, Any]],
    orientation_gate_rad: float,
) -> None:
    best_orientation = aggregate["best_orientation_case"]
    best_qdot = aggregate["best_qdot_saturation_case"]
    lines = [
        "# Stage B Orientation Kp Probe Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case count: `{aggregate['case_count']}`",
        f"- Stitched pass count: `{aggregate['stitched_pass_count']} / {aggregate['case_count']}`",
        f"- Stage A passed every case: `{aggregate['stage_a_all_passed']}`",
        f"- E2 orientation gate: `{orientation_gate_rad}`",
        f"- Orientation-ok cases: `{aggregate['orientation_ok_count']} / {aggregate['case_count']}`",
        f"- Min E2 orientation error: `{aggregate['min_e2_orientation_error_rad']}`",
        f"- Min E2 qdot saturation fraction: `{aggregate['min_e2_qdot_saturation_fraction']}`",
        f"- Min E2 tail qdot utilization: `{aggregate['min_e2_tail_qdot_utilization']}`",
        "",
    ]
    if best_orientation:
        lines.extend(
            [
                "Best orientation-error case:",
                "",
                "- qdot limit: `{qdot}`".format(qdot=best_orientation["qdot_limit_rad_s"]),
                "- orientation_kp: `{kp}`".format(kp=best_orientation["orientation_kp"]),
                "- E2 orientation error: `{orientation}`".format(
                    orientation=best_orientation["e2_orientation_error_rad"]
                ),
                "- E2 failed criteria: `{failed}`".format(
                    failed=",".join(best_orientation["e2_failed_criteria"]) or "none"
                ),
                "",
            ]
        )
    if best_qdot:
        lines.extend(
            [
                "Best qdot-saturation case:",
                "",
                "- qdot limit: `{qdot}`".format(qdot=best_qdot["qdot_limit_rad_s"]),
                "- orientation_kp: `{kp}`".format(kp=best_qdot["orientation_kp"]),
                "- E2 orientation error: `{orientation}`".format(
                    orientation=best_qdot["e2_orientation_error_rad"]
                ),
                "- E2 qdot saturation fraction: `{qdot_sat}`".format(
                    qdot_sat=best_qdot["e2_qdot_saturation_fraction"]
                ),
                "- E2 failed criteria: `{failed}`".format(
                    failed=",".join(best_qdot["e2_failed_criteria"]) or "none"
                ),
                "",
            ]
        )
    lines.extend(
        [
            "| qdot limit | orientation_kp | stitched | E2 pass | E2 orientation | E2 qdot sat | E2 tail qdot | E2 angular slack | E2 failed criteria |",
            "| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for case in cases:
        lines.append(
            "| `{qdot}` | `{kp}` | `{stitched}` | `{e2}` | `{orientation}` | `{qdot_sat}` | `{tail_qdot}` | `{slack}` | `{failed}` |".format(
                qdot=case["qdot_limit_rad_s"],
                kp=case["orientation_kp"],
                stitched=case["stitched_passed"],
                e2=case["e2_passed"],
                orientation=case["e2_orientation_error_rad"],
                qdot_sat=case["e2_qdot_saturation_fraction"],
                tail_qdot=case["e2_tail_qdot_utilization"],
                slack=case["e2_max_angular_velocity_slack_rad_s"],
                failed=",".join(case["e2_failed_criteria"]) or "none",
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- Low orientation feedback gains preserve the qdot budget but still miss the tightened E2 orientation gate.",
            "- Gains that reduce E2 orientation below the gate consume the qdot budget and fail qdot saturation and/or tail qdot utilization.",
            "- This probe does not change the canonical controller configuration or remove the v77 tightened-orientation boundary.",
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
    parser.add_argument("--paper-time-scale", type=float, default=0.005)
    parser.add_argument("--orientation-gate-rad", type=float, default=0.11995)
    parser.add_argument("--qdot-limits", default="0.15,0.16,0.18,0.2,0.25")
    parser.add_argument("--orientation-kps", default="0,0.001,0.002,0.003,0.005,0.01")
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    source_config = source_run / "relaxed_stage_a_target_config.yaml"
    delta_m = float(args.base_z_delta_mm) / 1000.0
    qdot_limits = parse_float_list(args.qdot_limits)
    orientation_kps = parse_float_list(args.orientation_kps)
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "stage_b_orientation_kp_probe" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    stage_a_target_config = write_stage_a_config(
        out_dir=out_dir,
        source_config=source_config,
        orientation_gate_rad=args.orientation_gate_rad,
    )

    cases = []
    for qdot_limit_rad_s in qdot_limits:
        for orientation_kp in orientation_kps:
            case_dir = (
                out_dir
                / "cases"
                / value_label("qdot", qdot_limit_rad_s)
                / value_label("kp", orientation_kp)
            )
            case_dir.mkdir(parents=True, exist_ok=True)
            metrics = run_child(
                stitched_command(
                    out_dir=case_dir,
                    source_run=source_run,
                    stage_a_target_config=stage_a_target_config,
                    delta_m=delta_m,
                    stage_a_duration_s=args.stage_a_duration_s,
                    paper_time_scale=args.paper_time_scale,
                    qdot_limit_rad_s=qdot_limit_rad_s,
                    orientation_kp=orientation_kp,
                    max_orientation_error_rad=args.orientation_gate_rad,
                ),
                out_dir=case_dir,
            )
            case = summarize_case(delta_m, metrics)
            case["qdot_limit_rad_s"] = float(qdot_limit_rad_s)
            case["orientation_kp"] = float(orientation_kp)
            case["orientation_gate_rad"] = float(args.orientation_gate_rad)
            case["stage_a_target_config"] = str(stage_a_target_config)
            case.update(e2_metrics(metrics))
            cases.append(case)

    aggregate = aggregate_cases(cases, orientation_gate_rad=float(args.orientation_gate_rad))
    payload = {
        "run_id": run_id,
        "source": "v78 focused E2 Stage B orientation-kp probe for the +1.0 mm tightened-orientation boundary",
        "source_run": str(source_run),
        "source_stage_a_target_config": str(source_config),
        "stage_a_target_config": str(stage_a_target_config),
        "base_z_offset_delta_m": delta_m,
        "base_z_offset_delta_mm": float(args.base_z_delta_mm),
        "stage_a_duration_s": float(args.stage_a_duration_s),
        "paper_time_scale": float(args.paper_time_scale),
        "orientation_gate_rad": float(args.orientation_gate_rad),
        "qdot_limits_rad_s": qdot_limits,
        "orientation_kps": orientation_kps,
        "trajectory": TRAJECTORY,
        "aggregate": aggregate,
        "cases": cases,
        "warnings": [
            "diagnostic-label E2 Stage B orientation-kp probe only",
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
    write_summary(
        out_dir=out_dir,
        aggregate=aggregate,
        cases=cases,
        orientation_gate_rad=float(args.orientation_gate_rad),
    )
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
