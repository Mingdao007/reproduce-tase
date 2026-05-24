#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from typing import Any

import numpy as np
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from audit_stage_a_base_z_recovery import (
    run_path_case,
    run_stitched_case,
    start_metrics_for_case,
    write_git_state,
)
from tase_repro.base_z_recovery import aggregate_base_z_bracket, base_z_delta_label
from tase_repro.setup_terminal_ik import SetupTerminalThresholds, solve_setup_terminal_ik
from tase_repro.stage_a_target_handoff import load_stage_a_target_config, selected_stage_a_target


def parse_float_list(text: str) -> list[float]:
    values = [float(part.strip()) for part in text.split(",") if part.strip()]
    if not values:
        raise ValueError("expected at least one numeric value")
    return values


def compact_candidate(candidate: Any) -> dict[str, Any]:
    payload = candidate.to_dict()
    return {
        "seed_label": payload["seed_label"],
        "q": payload["q"],
        "cost": payload["cost"],
        "success": payload["success"],
        "status": payload["status"],
        "message": payload["message"],
        "nfev": payload["nfev"],
        "tcp_m": payload["tcp_m"],
        "force_N": payload["force_N"],
        "force_error_N": payload["force_error_N"],
        "tangential_error_m": payload["tangential_error_m"],
        "orientation_error_rad": payload["orientation_error_rad"],
        "target_contact_count": payload["target_contact_count"],
        "failed_criteria": payload["failed_criteria"],
        "passed": payload["passed"],
        "max_gate_ratio": payload["max_gate_ratio"],
    }


def write_terminal_summary(out_dir: pathlib.Path, metrics: dict[str, Any]) -> None:
    best = metrics["best_candidate"]
    lines = [
        "# Compact Base-Z Terminal Probe Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case: `{metrics['case']}`",
        f"- Base-z offset delta m: `{metrics['base_z_offset_delta_m']}`",
        f"- Terminal pass count: `{metrics['pass_count']} / {metrics['candidate_count']}`",
        f"- Best pass: `{best['passed']}`",
        f"- Best seed: `{best['seed_label']}`",
        f"- Best failed criteria: `{';'.join(best['failed_criteria']) or 'none'}`",
        f"- Best force error N: `{best['force_error_N']}`",
        f"- Best x/y error m: `{best['tangential_error_m']}`",
        f"- Best orientation error rad: `{best['orientation_error_rad']}`",
        "",
        "Interpretation:",
        "",
        "- This compact probe stores only initial and best terminal candidates.",
        "- It is a diagnostic simulation search, not a path, robustness proof, or hardware result.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def terminal_metrics_for_case(
    *,
    case_name: str,
    base_z_offset_delta_m: float,
    base_z_offset_nominal_m: float,
    model_path: pathlib.Path,
    setup: dict[str, Any],
    setup_path: pathlib.Path,
    config_path: pathlib.Path,
    thresholds: SetupTerminalThresholds,
    extra_seed_qs: dict[str, np.ndarray],
    args: argparse.Namespace,
    out_dir: pathlib.Path,
) -> dict[str, Any]:
    base_z_offset = base_z_offset_nominal_m + float(base_z_offset_delta_m)
    result = solve_setup_terminal_ik(
        model_path,
        initial_q=np.asarray(setup["initial_q"], dtype=float),
        base_z_offset_m=base_z_offset,
        target_force_N=float(setup["target_force_N"]),
        thresholds=thresholds,
        surface_normal_world=np.asarray(setup["surface_normal_world"], dtype=float),
        site_name=str(setup["site_name"]),
        contact_geom_name=str(setup["contact_geom_name"]),
        plane_geom_name=str(setup["plane_geom_name"]),
        random_seed_count=int(args.random_seed_count),
        random_seed_std_rad=float(args.random_seed_std_rad),
        random_seed=int(args.random_seed),
        max_nfev=int(args.terminal_max_nfev),
        posture_weight=float(args.posture_weight),
        extra_seed_qs=extra_seed_qs,
    )
    metrics = {
        "case": case_name,
        "config": str(config_path),
        "model": str(model_path),
        "setup_metrics": str(setup_path),
        "base_z_offset_nominal_m": base_z_offset_nominal_m,
        "base_z_offset_delta_m": float(base_z_offset_delta_m),
        "base_z_offset_m": base_z_offset,
        "candidate_count": len(result.candidates),
        "pass_count": result.pass_count,
        "extra_seed_labels": list(extra_seed_qs),
        "initial_candidate": compact_candidate(result.initial_candidate),
        "best_candidate": compact_candidate(result.best_candidate),
        "warnings": [
            "compact terminal nonlinear least-squares feasibility audit only",
            "not a path or velocity-controller feasibility proof",
            "simulation-only and not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    write_terminal_summary(out_dir, metrics)
    return metrics


def summarize_start(metrics: dict[str, Any]) -> dict[str, Any]:
    best = metrics["best_candidate"]
    return {
        "passed": bool(best["passed"]),
        "force_error_N": float(best["force_error_N"]),
        "tangential_error_m": float(best["tangential_error_m"]),
        "target_contact_count": int(best["target_contact_count"]),
        "failed_criteria": list(best["failed_criteria"]),
        "q": list(best["q"]),
    }


def summarize_terminal(metrics: dict[str, Any]) -> dict[str, Any]:
    best = metrics["best_candidate"]
    return {
        "passed": bool(best["passed"]),
        "pass_count": int(metrics["pass_count"]),
        "candidate_count": int(metrics["candidate_count"]),
        "best_seed": str(best["seed_label"]),
        "force_error_N": float(best["force_error_N"]),
        "tangential_error_m": float(best["tangential_error_m"]),
        "orientation_error_rad": float(best["orientation_error_rad"]),
        "target_contact_count": int(best["target_contact_count"]),
        "failed_criteria": list(best["failed_criteria"]),
        "q": list(best["q"]),
    }


def summarize_path(metrics: dict[str, Any], path_dir: pathlib.Path) -> dict[str, Any]:
    return {
        "path_gate_passed": bool(metrics["path_gate"]["passed"]),
        "terminal_gate_passed": bool(metrics["terminal_gate"]["passed"]),
        "min_duration_s": float(metrics["timing"]["min_duration_s"]),
        "max_abs_qdot_rad_s": float(metrics["timing"]["max_abs_qdot_rad_s"]),
        "target_contact_present_fraction": float(metrics["evaluation"]["target_contact_present_fraction"]),
        "max_force_error_N": float(metrics["evaluation"]["max_force_error_N"]),
        "max_scheduled_xy_error_m": float(metrics["evaluation"]["max_scheduled_xy_error_m"]),
        "max_scheduled_orientation_error_rad": float(
            metrics["evaluation"]["max_scheduled_orientation_error_rad"]
        ),
        "path_csv": str(path_dir / "path.csv"),
    }


def duration_row_without_stitch(duration_s: float, reason: str) -> dict[str, Any]:
    return {
        "stage_a_duration_s": float(duration_s),
        "stitched_ran": False,
        "stitched_passed": False,
        "stage_a_passed": False,
        "handoff_pass_count": 0,
        "handoff_trajectory_count": 0,
        "skipped_reason": reason,
    }


def summarize_stitched(metrics: dict[str, Any], duration_s: float) -> dict[str, Any]:
    gate = metrics["stitched_gate"]
    return {
        "stage_a_duration_s": float(duration_s),
        "stitched_ran": True,
        "stitched_passed": bool(gate["passed"]),
        "stage_a_passed": bool(gate["stage_a_passed"]),
        "handoff_pass_count": int(gate["handoff_pass_count"]),
        "handoff_trajectory_count": int(gate["handoff_trajectory_count"]),
        "stage_a_max_qdot_rad_s": float(metrics["stage_a"]["tracking"]["max_abs_qdot_rad_s"]),
        "stage_a_terminal_force_error_N": float(metrics["stage_a"]["evaluation"]["terminal_force_error_N"]),
        "skipped_reason": None,
    }


def case_status(case: dict[str, Any]) -> str:
    if not case["start"]["passed"] and not case["terminal"]["passed"]:
        return "start_and_terminal_not_found"
    if not case["start"]["passed"]:
        return "start_contact_not_found"
    if not case["terminal"]["passed"]:
        return "terminal_target_not_found"
    if case["path"] is None:
        return "path_not_run"
    if not case["path"]["path_gate_passed"]:
        return "path_geometry_failed"
    if any(duration["stitched_passed"] for duration in case["durations"]):
        return "recovered_at_tested_duration"
    if any(duration["stitched_ran"] for duration in case["durations"]):
        return "stitched_failed"
    return "path_timing_margin_required"


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    lines = [
        "# Stage A Base-Z Bracket Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case count: `{aggregate['case_count']}`",
        f"- Start pass count: `{aggregate['start_pass_count']}`",
        f"- Terminal pass count: `{aggregate['terminal_pass_count']}`",
        f"- Path geometry pass count: `{aggregate['path_geometry_pass_count']}`",
        f"- Duration recovered count: `{aggregate['duration_recovered_count']}`",
        f"- Max positive terminal-pass delta mm: `{aggregate['max_positive_terminal_pass_delta_mm']}`",
        f"- Max positive recovered delta mm: `{aggregate['max_positive_recovered_delta_mm']}`",
        "",
        "| delta mm | status | start | terminal | path min duration s | recovered durations | terminal orientation rad |",
        "| ---: | --- | --- | --- | ---: | --- | ---: |",
    ]
    for case in cases:
        recovered = [
            str(duration["stage_a_duration_s"])
            for duration in case["durations"]
            if duration["stitched_passed"]
        ]
        lines.append(
            "| `{delta}` | `{status}` | `{start}` | `{terminal}` | `{min_duration}` | `{durations}` | `{orientation}` |".format(
                delta=1000.0 * float(case["base_z_offset_delta_m"]),
                status=case["status"],
                start=case["start"]["passed"],
                terminal=case["terminal"]["passed"],
                min_duration=None if case["path"] is None else case["path"]["min_duration_s"],
                durations=", ".join(recovered) or "none",
                orientation=case["terminal"]["orientation_error_rad"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- This compact bracket locates where diagnostic start, terminal, path, and stitched feasibility break as base-z is perturbed.",
            "- It does not replace strict paper-equivalent setup, contact-model calibration, or hardware validation.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml")
    parser.add_argument("--setup-metrics", default="runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml")
    parser.add_argument("--stage-a-target-config", default="configs/ur10e_adapted_stage_a_target.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument(
        "--base-z-deltas-mm",
        default="-1.0,-0.75,-0.5,-0.25,0.0,0.05,0.1,0.15,0.2,0.25,0.5,0.75,1.0",
    )
    parser.add_argument("--stage-a-durations-s", default="15.0,16.0")
    parser.add_argument("--random-seed-count", type=int, default=512)
    parser.add_argument("--random-seed-std-rad", type=float, default=0.15)
    parser.add_argument("--random-seed", type=int, default=37)
    parser.add_argument("--start-max-nfev", type=int, default=300)
    parser.add_argument("--start-posture-weight", type=float, default=0.01)
    parser.add_argument("--terminal-max-nfev", type=int, default=300)
    parser.add_argument("--posture-weight", type=float, default=1e-4)
    parser.add_argument("--knot-count", type=int, default=128)
    parser.add_argument("--path-max-nfev", type=int, default=200)
    parser.add_argument("--stage-b-duration-s", type=float, default=2.0)
    parser.add_argument("--target-force-N", type=float, default=5.0)
    parser.add_argument("--force-gain", type=float, default=1e-4)
    parser.add_argument("--r", type=float, default=0.5)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--planar-kp", type=float, default=0.5)
    parser.add_argument("--paper-time-scale", type=float, default=0.01)
    parser.add_argument("--orientation-kp", type=float, default=0.0)
    parser.add_argument("--max-orientation-error-rad", type=float, default=0.08)
    parser.add_argument("--max-angular-slack-rad-s", type=float, default=0.03)
    parser.add_argument("--continuity-weight", type=float, default=0.02)
    parser.add_argument("--linear-posture-weight", type=float, default=0.002)
    args = parser.parse_args()

    deltas_m = [value / 1000.0 for value in parse_float_list(args.base_z_deltas_mm)]
    durations_s = parse_float_list(args.stage_a_durations_s)

    config_path = (ROOT / args.config).resolve()
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    setup_path = (ROOT / args.setup_metrics).resolve()
    with setup_path.open("r", encoding="utf-8") as f:
        setup = yaml.safe_load(f)
    target_config_path = (ROOT / args.stage_a_target_config).resolve()
    target_config = load_stage_a_target_config(target_config_path)
    target = selected_stage_a_target(target_config)
    gate = target["diagnostic_gate"]
    thresholds = SetupTerminalThresholds(
        max_force_error_N=float(gate["max_terminal_force_error_N"]),
        max_tangential_error_m=float(gate["max_terminal_tangential_error_m"]),
        max_orientation_error_rad=float(gate["max_terminal_orientation_error_rad"]),
    )
    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    base_z_offset_nominal = float(setup["base_z_offset_m"])
    extra_terminal_seeds = {
        "selected_stage_a_target": np.asarray(target["q_rad"], dtype=float),
    }

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "stage_a_base_z_bracket" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    case_summaries = []
    for delta_m in deltas_m:
        case_name = base_z_delta_label(delta_m)
        case_dir = out_dir / "cases" / case_name
        start_dir = case_dir / "start"
        terminal_dir = case_dir / "terminal"
        start_dir.mkdir(parents=True, exist_ok=True)
        terminal_dir.mkdir(parents=True, exist_ok=True)
        start_metrics = start_metrics_for_case(
            case_name=case_name,
            base_z_offset_delta_m=delta_m,
            base_z_offset_nominal_m=base_z_offset_nominal,
            model_path=model_path,
            setup=setup,
            setup_path=setup_path,
            config_path=config_path,
            thresholds=thresholds,
            args=args,
            out_dir=start_dir,
        )
        terminal_metrics = terminal_metrics_for_case(
            case_name=case_name,
            base_z_offset_delta_m=delta_m,
            base_z_offset_nominal_m=base_z_offset_nominal,
            model_path=model_path,
            setup=setup,
            setup_path=setup_path,
            config_path=config_path,
            thresholds=thresholds,
            extra_seed_qs=extra_terminal_seeds,
            args=args,
            out_dir=terminal_dir,
        )
        start_summary = summarize_start(start_metrics)
        terminal_summary = summarize_terminal(terminal_metrics)
        path_summary = None
        duration_summaries: list[dict[str, Any]] = []

        if start_summary["passed"] and terminal_summary["passed"]:
            path_dir = case_dir / "path"
            path_metrics = run_path_case(
                case_name=case_name,
                base_z_offset_delta_m=delta_m,
                stage_a_duration_s=None,
                initial_q=start_summary["q"],
                target_q=terminal_summary["q"],
                args=args,
                out_dir=path_dir,
            )
            path_summary = summarize_path(path_metrics, path_dir)
            if path_summary["path_gate_passed"]:
                for duration_s in durations_s:
                    if path_summary["min_duration_s"] > duration_s + 1e-12:
                        duration_summaries.append(
                            duration_row_without_stitch(
                                duration_s,
                                "path_min_duration_exceeds_stage_a_duration",
                            )
                        )
                        continue
                    stitched_dir = case_dir / f"stitched_{str(duration_s).replace('.', 'p')}s"
                    stitched_metrics = run_stitched_case(
                        base_z_offset_delta_m=delta_m,
                        stage_a_duration_s=duration_s,
                        source_path_csv=path_dir / "path.csv",
                        args=args,
                        out_dir=stitched_dir,
                    )
                    duration_summaries.append(summarize_stitched(stitched_metrics, duration_s))
            else:
                duration_summaries = [
                    duration_row_without_stitch(duration_s, "path_gate_failed")
                    for duration_s in durations_s
                ]

        case = {
            "case": case_name,
            "base_z_offset_delta_m": float(delta_m),
            "base_z_offset_delta_mm": 1000.0 * float(delta_m),
            "start": start_summary,
            "terminal": terminal_summary,
            "path": path_summary,
            "durations": duration_summaries,
        }
        case["status"] = case_status(case)
        case_summaries.append(case)

    aggregate = aggregate_base_z_bracket(case_summaries)
    payload = {
        "run_id": run_id,
        "source": "compact base-z perturbation bracket around v66 recovery gaps",
        "base_z_deltas_mm": [1000.0 * value for value in deltas_m],
        "stage_a_durations_s": durations_s,
        "diagnostic_gate": gate,
        "parameters": {
            "random_seed_count": int(args.random_seed_count),
            "random_seed_std_rad": float(args.random_seed_std_rad),
            "random_seed": int(args.random_seed),
            "start_max_nfev": int(args.start_max_nfev),
            "terminal_max_nfev": int(args.terminal_max_nfev),
            "extra_terminal_seed_labels": list(extra_terminal_seeds),
            "knot_count": int(args.knot_count),
            "path_max_nfev": int(args.path_max_nfev),
            "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
            "stage_b_duration_s": float(args.stage_b_duration_s),
            "paper_time_scale": float(args.paper_time_scale),
        },
        "aggregate": aggregate,
        "cases": case_summaries,
        "warnings": [
            "compact diagnostic-label simulation bracket only",
            "not strict paper-equivalent feasibility",
            "not contact-model calibration",
            "not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    write_summary(out_dir, aggregate, case_summaries)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
