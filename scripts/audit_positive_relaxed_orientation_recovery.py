#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
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

from audit_positive_base_z_start_contact import start_search_for_case, summarize_start_search
from audit_stage_a_base_z_bracket import (
    case_status,
    compact_candidate,
    duration_row_without_stitch,
    parse_float_list,
    summarize_path,
    summarize_stitched,
)
from audit_stage_a_base_z_recovery import run_path_case, run_stitched_case, write_git_state
from tase_repro.base_z_recovery import aggregate_base_z_bracket, base_z_delta_label
from tase_repro.setup_terminal_ik import SetupTerminalCandidate, SetupTerminalThresholds, solve_setup_terminal_ik
from tase_repro.stage_a_target_handoff import load_stage_a_target_config, selected_stage_a_target


def write_relaxed_target_config(
    *,
    source_config: dict[str, Any],
    orientation_threshold_rad: float,
    out_path: pathlib.Path,
) -> dict[str, Any]:
    relaxed = copy.deepcopy(source_config)
    relaxed["selected_stage_a_target"]["diagnostic_gate"][
        "max_terminal_orientation_error_rad"
    ] = float(orientation_threshold_rad)
    relaxed.setdefault("v70_relaxed_orientation_scope", {})
    relaxed["v70_relaxed_orientation_scope"] = {
        "description": "Run-local diagnostic gate relaxation for positive-side recovery audit.",
        "max_terminal_orientation_error_rad": float(orientation_threshold_rad),
        "claim_scope": "simulation_only_not_hardware_ready_not_paper_equivalent",
    }
    with out_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(relaxed, f, sort_keys=False, allow_unicode=True)
    return relaxed


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    lines = [
        "# Positive Relaxed Orientation Recovery Summary",
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
        "| delta mm | status | start | terminal | path pass | path min duration s | recovered durations | terminal orientation rad |",
        "| ---: | --- | --- | --- | --- | ---: | --- | ---: |",
    ]
    for case in cases:
        recovered = [
            str(duration["stage_a_duration_s"])
            for duration in case["durations"]
            if duration["stitched_passed"]
        ]
        lines.append(
            "| `{delta}` | `{status}` | `{start}` | `{terminal}` | `{path}` | `{min_duration}` | `{durations}` | `{orientation}` |".format(
                delta=case["base_z_offset_delta_mm"],
                status=case["status"],
                start=case["start"]["passed"],
                terminal=case["terminal"]["passed"],
                path=None if case["path"] is None else case["path"]["path_gate_passed"],
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
            "- This audit tests whether the v69 `0.12 rad` diagnostic orientation margin can unlock positive-side terminal, path, and stitched recovery in the current contact-point model.",
            "- It uses a run-local relaxed Stage A target config and does not change the canonical v58 target config.",
            "- It remains diagnostic-label simulation evidence only, not strict paper-equivalent feasibility, robustness, contact-model calibration, or hardware readiness.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def relaxed_candidate_eval(candidate: SetupTerminalCandidate, thresholds: SetupTerminalThresholds) -> dict[str, Any]:
    criteria = {
        "force_error_N": {
            "actual": float(candidate.force_error_N),
            "operator": "<=",
            "threshold": float(thresholds.max_force_error_N),
            "passed": float(candidate.force_error_N) <= float(thresholds.max_force_error_N),
        },
        "tangential_error_m": {
            "actual": float(candidate.tangential_error_m),
            "operator": "<=",
            "threshold": float(thresholds.max_tangential_error_m),
            "passed": float(candidate.tangential_error_m) <= float(thresholds.max_tangential_error_m),
        },
        "orientation_error_rad": {
            "actual": float(candidate.orientation_error_rad),
            "operator": "<=",
            "threshold": float(thresholds.max_orientation_error_rad),
            "passed": float(candidate.orientation_error_rad) <= float(thresholds.max_orientation_error_rad),
        },
        "contact_present": {
            "actual": int(candidate.target_contact_count),
            "operator": ">=",
            "threshold": 1,
            "passed": int(candidate.target_contact_count) >= 1,
        },
    }
    failed = [name for name, criterion in criteria.items() if not criterion["passed"]]
    ratios = [
        float(candidate.force_error_N) / float(thresholds.max_force_error_N),
        float(candidate.tangential_error_m) / float(thresholds.max_tangential_error_m),
        float(candidate.orientation_error_rad) / float(thresholds.max_orientation_error_rad),
        0.0 if int(candidate.target_contact_count) >= 1 else float("inf"),
    ]
    return {
        "criteria": criteria,
        "failed_criteria": failed,
        "passed": not failed,
        "max_gate_ratio": float(np.max(ratios)),
    }


def terminal_metrics_for_relaxed_gate(
    *,
    case_name: str,
    base_z_offset_delta_m: float,
    base_z_offset_nominal_m: float,
    model_path: pathlib.Path,
    setup: dict[str, Any],
    setup_path: pathlib.Path,
    config_path: pathlib.Path,
    solver_thresholds: SetupTerminalThresholds,
    gate_thresholds: SetupTerminalThresholds,
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
        thresholds=solver_thresholds,
        surface_normal_world=np.asarray(setup["surface_normal_world"], dtype=float),
        site_name=str(setup["site_name"]),
        contact_geom_name=str(setup["contact_geom_name"]),
        plane_geom_name=str(setup["plane_geom_name"]),
        random_seed_count=int(args.terminal_random_seed_count),
        random_seed_std_rad=float(args.terminal_random_seed_std_rad),
        random_seed=int(args.terminal_random_seed),
        max_nfev=int(args.terminal_max_nfev),
        posture_weight=float(args.posture_weight),
        extra_seed_qs=extra_seed_qs,
    )
    relaxed_rows = []
    for candidate in result.candidates:
        relaxed = relaxed_candidate_eval(candidate, gate_thresholds)
        relaxed_rows.append((candidate, relaxed))
    relaxed_rows.sort(key=lambda row: (row[1]["max_gate_ratio"], candidate_sort_tie(row[0])))
    best_candidate, best_relaxed = relaxed_rows[0]
    best = compact_candidate(best_candidate)
    best["failed_criteria"] = best_relaxed["failed_criteria"]
    best["passed"] = best_relaxed["passed"]
    best["max_gate_ratio"] = best_relaxed["max_gate_ratio"]
    metrics = {
        "case": case_name,
        "config": str(config_path),
        "model": str(model_path),
        "setup_metrics": str(setup_path),
        "base_z_offset_nominal_m": base_z_offset_nominal_m,
        "base_z_offset_delta_m": float(base_z_offset_delta_m),
        "base_z_offset_m": base_z_offset,
        "candidate_count": len(result.candidates),
        "pass_count": sum(1 for _candidate, relaxed in relaxed_rows if relaxed["passed"]),
        "extra_seed_labels": list(extra_seed_qs),
        "solver_thresholds": solver_thresholds.to_dict(),
        "relaxed_gate_thresholds": gate_thresholds.to_dict(),
        "best_candidate": best,
        "best_relaxed_criteria": best_relaxed["criteria"],
        "warnings": [
            "terminal nonlinear least-squares uses solver thresholds but evaluates a relaxed diagnostic gate",
            "not a path or velocity-controller feasibility proof",
            "simulation-only and not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    lines = [
        "# Relaxed Terminal Target Probe Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case: `{case_name}`",
        f"- Base-z offset delta m: `{base_z_offset_delta_m}`",
        f"- Relaxed terminal pass count: `{metrics['pass_count']} / {metrics['candidate_count']}`",
        f"- Best pass: `{best['passed']}`",
        f"- Best seed: `{best['seed_label']}`",
        f"- Best failed criteria: `{';'.join(best['failed_criteria']) or 'none'}`",
        f"- Best force error N: `{best['force_error_N']}`",
        f"- Best x/y error m: `{best['tangential_error_m']}`",
        f"- Best orientation error rad: `{best['orientation_error_rad']}`",
        "",
        "Interpretation:",
        "",
        "- Solver thresholds and relaxed gate thresholds are recorded separately.",
        "- This is terminal-state diagnostic simulation evidence only.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return metrics


def candidate_sort_tie(candidate: SetupTerminalCandidate) -> tuple[float, str]:
    cost = float("inf") if not np.isfinite(candidate.cost) else float(candidate.cost)
    return cost, str(candidate.seed_label)


def summarize_relaxed_terminal(metrics: dict[str, Any]) -> dict[str, Any]:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml")
    parser.add_argument("--setup-metrics", default="runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml")
    parser.add_argument("--stage-a-target-config", default="configs/ur10e_adapted_stage_a_target.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--base-z-deltas-mm", default="0.05,0.1,0.15,0.2,0.25,0.5,0.75,1.0")
    parser.add_argument("--stage-a-durations-s", default="15.0,16.0")
    parser.add_argument("--relaxed-orientation-threshold-rad", type=float, default=0.12)
    parser.add_argument("--terminal-solver-orientation-threshold-rad", type=float, default=0.08)
    parser.add_argument("--joint-sweep-rad", type=float, default=0.08)
    parser.add_argument("--joint-sweep-count", type=int, default=321)
    parser.add_argument("--pair-sweep-rad", type=float, default=0.04)
    parser.add_argument("--pair-sweep-count", type=int, default=161)
    parser.add_argument("--pair-sweep-joints", default="1:2,2:5,2:3,3:5")
    parser.add_argument("--random-seed-count", type=int, default=10000)
    parser.add_argument("--random-seed-std-rad", type=float, default=0.03)
    parser.add_argument("--random-seed", type=int, default=541)
    parser.add_argument("--max-force-error-N", type=float, default=0.25)
    parser.add_argument("--max-tangential-error-m", type=float, default=0.004)
    parser.add_argument("--terminal-random-seed-count", type=int, default=512)
    parser.add_argument("--terminal-random-seed-std-rad", type=float, default=0.15)
    parser.add_argument("--terminal-random-seed", type=int, default=37)
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
    source_target_config_path = (ROOT / args.stage_a_target_config).resolve()
    source_target_config = load_stage_a_target_config(source_target_config_path)

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "positive_relaxed_orientation_recovery" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    relaxed_config_path = out_dir / "relaxed_stage_a_target_config.yaml"
    relaxed_target_config = write_relaxed_target_config(
        source_config=source_target_config,
        orientation_threshold_rad=float(args.relaxed_orientation_threshold_rad),
        out_path=relaxed_config_path,
    )
    target = selected_stage_a_target(relaxed_target_config)
    gate = target["diagnostic_gate"]
    gate_thresholds = SetupTerminalThresholds(
        max_force_error_N=float(gate["max_terminal_force_error_N"]),
        max_tangential_error_m=float(gate["max_terminal_tangential_error_m"]),
        max_orientation_error_rad=float(gate["max_terminal_orientation_error_rad"]),
    )
    solver_thresholds = SetupTerminalThresholds(
        max_force_error_N=float(gate["max_terminal_force_error_N"]),
        max_tangential_error_m=float(gate["max_terminal_tangential_error_m"]),
        max_orientation_error_rad=float(args.terminal_solver_orientation_threshold_rad),
    )
    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    base_z_offset_nominal = float(setup["base_z_offset_m"])
    extra_terminal_seeds = {
        "selected_stage_a_target": np.asarray(target["q_rad"], dtype=float),
    }
    child_args = copy.copy(args)
    child_args.stage_a_target_config = str(relaxed_config_path)
    child_args.max_orientation_error_rad = float(args.relaxed_orientation_threshold_rad)

    cases = []
    for delta_m in deltas_m:
        case_name = base_z_delta_label(delta_m)
        case_dir = out_dir / "cases" / case_name
        start_dir = case_dir / "start_search"
        terminal_dir = case_dir / "terminal"
        start_dir.mkdir(parents=True, exist_ok=True)
        terminal_dir.mkdir(parents=True, exist_ok=True)

        start_metrics = start_search_for_case(
            case_name=case_name,
            base_z_offset_delta_m=delta_m,
            base_z_offset_nominal_m=base_z_offset_nominal,
            model_path=model_path,
            setup=setup,
            config_path=config_path,
            setup_path=setup_path,
            args=args,
            out_dir=start_dir,
        )
        terminal_metrics = terminal_metrics_for_relaxed_gate(
            case_name=case_name,
            base_z_offset_delta_m=delta_m,
            base_z_offset_nominal_m=base_z_offset_nominal,
            model_path=model_path,
            setup=setup,
            setup_path=setup_path,
            config_path=config_path,
            solver_thresholds=solver_thresholds,
            gate_thresholds=gate_thresholds,
            extra_seed_qs=extra_terminal_seeds,
            args=args,
            out_dir=terminal_dir,
        )
        start_summary = summarize_start_search(start_metrics)
        terminal_summary = summarize_relaxed_terminal(terminal_metrics)
        start_for_case = {
            "passed": start_summary["passed"],
            "force_error_N": start_summary["best_force_error_N"],
            "tangential_error_m": start_summary["best_tangential_error_m"],
            "target_contact_count": start_summary["best_target_contact_count"],
            "failed_criteria": start_summary["best_failed_criteria"],
            "q": start_summary["best_q"],
        }
        path_summary = None
        duration_summaries: list[dict[str, Any]] = []
        if start_summary["passed"] and terminal_summary["passed"]:
            path_dir = case_dir / "path"
            path_metrics = run_path_case(
                case_name=case_name,
                base_z_offset_delta_m=delta_m,
                stage_a_duration_s=None,
                initial_q=start_summary["best_q"],
                target_q=terminal_summary["q"],
                args=child_args,
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
                        args=child_args,
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
            "start": start_for_case,
            "terminal": terminal_summary,
            "path": path_summary,
            "durations": duration_summaries,
        }
        case["status"] = case_status(case)
        cases.append(case)

    aggregate = aggregate_base_z_bracket(cases)
    payload = {
        "run_id": run_id,
        "source": "positive base-z recovery under relaxed diagnostic orientation threshold",
        "base_z_deltas_mm": [1000.0 * value for value in deltas_m],
        "stage_a_durations_s": durations_s,
        "source_stage_a_target_config": str(source_target_config_path),
        "relaxed_stage_a_target_config": str(relaxed_config_path),
        "relaxed_orientation_threshold_rad": float(args.relaxed_orientation_threshold_rad),
        "terminal_solver_orientation_threshold_rad": float(args.terminal_solver_orientation_threshold_rad),
        "diagnostic_gate": gate,
        "parameters": {
            "joint_sweep_rad": float(args.joint_sweep_rad),
            "joint_sweep_count": int(args.joint_sweep_count),
            "pair_sweep_rad": float(args.pair_sweep_rad),
            "pair_sweep_count": int(args.pair_sweep_count),
            "pair_sweep_joints": args.pair_sweep_joints,
            "random_seed_count": int(args.random_seed_count),
            "random_seed_std_rad": float(args.random_seed_std_rad),
            "random_seed": int(args.random_seed),
            "terminal_random_seed_count": int(args.terminal_random_seed_count),
            "terminal_random_seed_std_rad": float(args.terminal_random_seed_std_rad),
            "terminal_random_seed": int(args.terminal_random_seed),
            "terminal_max_nfev": int(args.terminal_max_nfev),
            "terminal_solver_orientation_threshold_rad": float(args.terminal_solver_orientation_threshold_rad),
            "knot_count": int(args.knot_count),
            "path_max_nfev": int(args.path_max_nfev),
            "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
            "stage_b_duration_s": float(args.stage_b_duration_s),
            "paper_time_scale": float(args.paper_time_scale),
        },
        "aggregate": aggregate,
        "cases": cases,
        "warnings": [
            "run-local relaxed diagnostic orientation gate only",
            "not strict paper-equivalent feasibility",
            "not robustness proof",
            "not contact-model calibration",
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
