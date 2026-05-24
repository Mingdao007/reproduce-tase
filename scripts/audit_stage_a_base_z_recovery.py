#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Any

import mujoco
import numpy as np
import yaml
from scipy.optimize import least_squares

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.base_z_recovery import aggregate_base_z_recovery, summarize_base_z_recovery_case
from tase_repro.contact_ladder import positive_contact_normal_force_between
from tase_repro.force_feedback import apply_base_z_offset
from tase_repro.kinematics import (
    joint_ranges,
    load_model,
    make_data,
    set_qpos,
    site_position,
    site_rotation_matrix,
)
from tase_repro.setup_terminal_ik import SetupTerminalThresholds, solve_setup_terminal_ik
from tase_repro.stage_a_contact_path import parse_joint_vector
from tase_repro.stage_a_target_handoff import load_stage_a_target_config, selected_stage_a_target


DEFAULT_CASES: list[dict[str, float | str]] = [
    {
        "name": "base_z_minus_1mm",
        "base_z_offset_delta_m": -0.001,
        "stage_a_duration_s": 15.0,
    },
    {
        "name": "base_z_minus_1mm_stage_a_16s_recovery",
        "base_z_offset_delta_m": -0.001,
        "stage_a_duration_s": 16.0,
    },
    {
        "name": "base_z_plus_1mm",
        "base_z_offset_delta_m": 0.001,
        "stage_a_duration_s": 15.0,
    },
]


def write_git_state(out_dir: pathlib.Path, *, command: list[str]) -> None:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
    lines = [
        "# Git State",
        "",
        f"- Branch: `{branch}`",
        f"- Commit: `{commit}`",
        f"- Dirty tree: `{bool(status)}`",
        "- Status:",
        "",
        "```text",
        status,
        "```",
        "",
        "- Command:",
        "",
        "```bash",
        " ".join(command),
        "```",
        "",
    ]
    (out_dir / "git_state.md").write_text("\n".join(lines), encoding="utf-8")


def q_to_cli(q: list[float] | np.ndarray) -> str:
    return ",".join(f"{float(value):.17g}" for value in q)


def run_child(command: list[str], *, out_dir: pathlib.Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    (out_dir / "command.txt").write_text(" ".join(command) + "\n", encoding="utf-8")
    (out_dir / "command_stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (out_dir / "command_stderr.txt").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"child command failed with exit code {completed.returncode}: {completed.stderr}")
    return yaml.safe_load((out_dir / "metrics.yaml").read_text(encoding="utf-8"))


def write_terminal_summary(out_dir: pathlib.Path, metrics: dict[str, Any]) -> None:
    best = metrics["best_candidate"]
    lines = [
        "# Base-Z Terminal Target Probe Summary",
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
        "- This is a terminal nonlinear least-squares feasibility probe for the perturbed base-z case.",
        "- It is not a path, online controller, robustness proof, or hardware result.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def force_normal_orientation_error(rotation: np.ndarray, normal: np.ndarray) -> float:
    local_z = np.asarray(rotation, dtype=float)[:, 2]
    normal_unit = np.asarray(normal, dtype=float)
    local_z = local_z / np.linalg.norm(local_z)
    normal_unit = normal_unit / np.linalg.norm(normal_unit)
    return float(np.arccos(np.clip(float(np.dot(local_z, normal_unit)), -1.0, 1.0)))


def start_candidate(
    *,
    model: Any,
    data: Any,
    q: np.ndarray,
    seed_label: str,
    solve: Any | None,
    site_name: str,
    contact_geom_name: str,
    plane_geom_name: str,
    reference_xy_m: np.ndarray,
    surface_normal_world: np.ndarray,
    target_force_N: float,
    thresholds: SetupTerminalThresholds,
) -> dict[str, Any]:
    set_qpos(model, data, q)
    mujoco.mj_forward(model, data)
    tcp = site_position(model, data, site_name)
    rotation = site_rotation_matrix(model, data, site_name)
    force, target_contact_count = positive_contact_normal_force_between(
        model,
        data,
        geom_a_name=plane_geom_name,
        geom_b_name=contact_geom_name,
    )
    force_error = abs(float(force) - float(target_force_N))
    tangential_error = float(np.linalg.norm(tcp[:2] - reference_xy_m))
    force_normal_error = force_normal_orientation_error(rotation, surface_normal_world)
    criteria = {
        "force_error_N": {
            "actual": force_error,
            "operator": "<=",
            "threshold": float(thresholds.max_force_error_N),
            "passed": force_error <= float(thresholds.max_force_error_N),
        },
        "tangential_error_m": {
            "actual": tangential_error,
            "operator": "<=",
            "threshold": float(thresholds.max_tangential_error_m),
            "passed": tangential_error <= float(thresholds.max_tangential_error_m),
        },
        "target_contact_count": {
            "actual": int(target_contact_count),
            "operator": ">=",
            "threshold": 1,
            "passed": int(target_contact_count) >= 1,
        },
    }
    failed = [name for name, criterion in criteria.items() if not criterion["passed"]]
    ratios = [
        force_error / float(thresholds.max_force_error_N),
        tangential_error / float(thresholds.max_tangential_error_m),
        0.0 if target_contact_count >= 1 else float("inf"),
    ]
    return {
        "seed_label": seed_label,
        "q": [float(x) for x in q],
        "cost": None if solve is None else float(solve.cost),
        "success": True if solve is None else bool(solve.success),
        "status": 0 if solve is None else int(solve.status),
        "message": "not optimized" if solve is None else str(solve.message),
        "nfev": 0 if solve is None else int(solve.nfev),
        "tcp_m": [float(x) for x in tcp],
        "target_force_N": float(target_force_N),
        "force_N": float(force),
        "force_error_N": force_error,
        "tangential_error_m": tangential_error,
        "force_normal_orientation_error_rad": force_normal_error,
        "target_contact_count": int(target_contact_count),
        "criteria": criteria,
        "failed_criteria": failed,
        "passed": not failed,
        "max_gate_ratio": float(np.max(ratios)),
    }


def write_start_summary(out_dir: pathlib.Path, metrics: dict[str, Any]) -> None:
    best = metrics["best_candidate"]
    lines = [
        "# Base-Z Start Contact Rebalance Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case: `{metrics['case']}`",
        f"- Base-z offset delta m: `{metrics['base_z_offset_delta_m']}`",
        f"- Start pass: `{best['passed']}`",
        f"- Failed criteria: `{';'.join(best['failed_criteria']) or 'none'}`",
        f"- Force error N: `{best['force_error_N']}`",
        f"- X/y error m: `{best['tangential_error_m']}`",
        f"- Force-normal orientation error rad: `{best['force_normal_orientation_error_rad']}`",
        "",
        "Interpretation:",
        "",
        "- This rebalances only the Stage A start contact under the perturbed base-z model.",
        "- It preserves a diagnostic simulation scope and is not a hardware or controller proof.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def start_metrics_for_case(
    *,
    case_name: str,
    base_z_offset_delta_m: float,
    base_z_offset_nominal_m: float,
    model_path: pathlib.Path,
    setup: dict[str, Any],
    setup_path: pathlib.Path,
    config_path: pathlib.Path,
    thresholds: SetupTerminalThresholds,
    args: argparse.Namespace,
    out_dir: pathlib.Path,
) -> dict[str, Any]:
    base_z_offset = base_z_offset_nominal_m + float(base_z_offset_delta_m)
    model = load_model(model_path)
    apply_base_z_offset(model, base_z_offset)
    data = make_data(model)
    q_min, q_max = joint_ranges(model)
    initial_q = np.asarray(setup["initial_q"], dtype=float)
    reference_xy = np.asarray(setup["reference_xy_m"], dtype=float)
    surface_normal = np.asarray(setup["surface_normal_world"], dtype=float)
    target_force = float(setup["target_force_N"])
    site_name = str(setup["site_name"])
    contact_geom_name = str(setup["contact_geom_name"])
    plane_geom_name = str(setup["plane_geom_name"])

    def residual(q: np.ndarray) -> np.ndarray:
        set_qpos(model, data, q)
        mujoco.mj_forward(model, data)
        tcp = site_position(model, data, site_name)
        force, _ = positive_contact_normal_force_between(
            model,
            data,
            geom_a_name=plane_geom_name,
            geom_b_name=contact_geom_name,
        )
        return np.r_[
            (force - target_force) / thresholds.max_force_error_N,
            (tcp[:2] - reference_xy) / thresholds.max_tangential_error_m,
            float(args.start_posture_weight) * (q - initial_q),
        ]

    solve = least_squares(
        residual,
        initial_q,
        bounds=(q_min, q_max),
        max_nfev=int(args.start_max_nfev),
        ftol=1e-10,
        xtol=1e-10,
        gtol=1e-10,
    )
    initial_candidate = start_candidate(
        model=model,
        data=data,
        q=initial_q,
        seed_label="initial_unoptimized",
        solve=None,
        site_name=site_name,
        contact_geom_name=contact_geom_name,
        plane_geom_name=plane_geom_name,
        reference_xy_m=reference_xy,
        surface_normal_world=surface_normal,
        target_force_N=target_force,
        thresholds=thresholds,
    )
    best_candidate = start_candidate(
        model=model,
        data=data,
        q=solve.x,
        seed_label="least_squares_start_rebalance",
        solve=solve,
        site_name=site_name,
        contact_geom_name=contact_geom_name,
        plane_geom_name=plane_geom_name,
        reference_xy_m=reference_xy,
        surface_normal_world=surface_normal,
        target_force_N=target_force,
        thresholds=thresholds,
    )
    candidates = [initial_candidate, best_candidate]
    metrics = {
        "case": case_name,
        "config": str(config_path),
        "model": str(model_path),
        "setup_metrics": str(setup_path),
        "base_z_offset_nominal_m": base_z_offset_nominal_m,
        "base_z_offset_delta_m": float(base_z_offset_delta_m),
        "base_z_offset_m": base_z_offset,
        "target_force_N": target_force,
        "site_name": site_name,
        "contact_geom_name": contact_geom_name,
        "plane_geom_name": plane_geom_name,
        "start_max_nfev": int(args.start_max_nfev),
        "start_posture_weight": float(args.start_posture_weight),
        "thresholds": {
            "max_force_error_N": float(thresholds.max_force_error_N),
            "max_tangential_error_m": float(thresholds.max_tangential_error_m),
        },
        "candidate_count": len(candidates),
        "pass_count": sum(1 for candidate in candidates if candidate["passed"]),
        "initial_candidate": initial_candidate,
        "best_candidate": best_candidate,
        "candidates": candidates,
        "warnings": [
            "start contact rebalance only",
            "orientation is recorded but not gated for the Stage A start endpoint",
            "simulation-only and not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    write_start_summary(out_dir, metrics)
    return metrics


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
    )
    metrics = {
        "case": case_name,
        "config": str(config_path),
        "model": str(model_path),
        "setup_metrics": str(setup_path),
        "base_z_offset_nominal_m": base_z_offset_nominal_m,
        "base_z_offset_delta_m": float(base_z_offset_delta_m),
        "base_z_offset_m": base_z_offset,
        "target_force_N": float(setup["target_force_N"]),
        "site_name": str(setup["site_name"]),
        "contact_geom_name": str(setup["contact_geom_name"]),
        "plane_geom_name": str(setup["plane_geom_name"]),
        "random_seed_count": int(args.random_seed_count),
        "random_seed_std_rad": float(args.random_seed_std_rad),
        "random_seed": int(args.random_seed),
        "terminal_max_nfev": int(args.terminal_max_nfev),
        "posture_weight": float(args.posture_weight),
        **result.to_dict(),
        "warnings": [
            "terminal nonlinear least-squares feasibility audit only",
            "not a path or velocity-controller feasibility proof",
            "uses approximate tilted-plane MuJoCo model and unverified 85 mm TCP",
            "simulation-only and not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    write_terminal_summary(out_dir, metrics)
    return metrics


def run_path_case(
    *,
    case_name: str,
    base_z_offset_delta_m: float,
    stage_a_duration_s: float | None,
    initial_q: list[float],
    target_q: list[float],
    args: argparse.Namespace,
    out_dir: pathlib.Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(ROOT / "scripts" / "audit_stage_a_contact_path.py"),
        "--config",
        args.config,
        "--setup-metrics",
        args.setup_metrics,
        "--stage-a-target-config",
        args.stage_a_target_config,
        "--output-dir",
        str(out_dir),
        f"--initial-q={q_to_cli(initial_q)}",
        "--initial-label",
        f"{case_name}_perturbed_start_contact",
        f"--target-q={q_to_cli(target_q)}",
        "--target-label",
        f"{case_name}_perturbed_terminal_target",
        f"--base-z-offset-delta-m={base_z_offset_delta_m}",
        "--knot-count",
        str(args.knot_count),
        "--max-nfev",
        str(args.path_max_nfev),
        "--qdot-limit-rad-s",
        str(args.qdot_limit_rad_s),
        "--continuity-weight",
        str(args.continuity_weight),
        "--linear-posture-weight",
        str(args.linear_posture_weight),
    ]
    if stage_a_duration_s is not None:
        command.extend(["--duration-s", str(stage_a_duration_s)])
    return run_child(command, out_dir=out_dir)


def run_stitched_case(
    *,
    base_z_offset_delta_m: float,
    stage_a_duration_s: float,
    source_path_csv: pathlib.Path,
    args: argparse.Namespace,
    out_dir: pathlib.Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(ROOT / "scripts" / "evaluate_stitched_stage_a_handoff.py"),
        "--config",
        args.config,
        "--setup-metrics",
        args.setup_metrics,
        "--stage-a-target-config",
        args.stage_a_target_config,
        "--source-path-csv",
        str(source_path_csv),
        "--output-dir",
        str(out_dir),
        "--base-z-offset-delta-m",
        str(base_z_offset_delta_m),
        "--stage-a-duration-s",
        str(stage_a_duration_s),
        "--stage-b-duration-s",
        str(args.stage_b_duration_s),
        "--target-force-N",
        str(args.target_force_N),
        "--force-gain",
        str(args.force_gain),
        "--r",
        str(args.r),
        "--qdot-limit-rad-s",
        str(args.qdot_limit_rad_s),
        "--planar-kp",
        str(args.planar_kp),
        "--paper-time-scale",
        str(args.paper_time_scale),
        "--orientation-kp",
        str(args.orientation_kp),
        "--max-orientation-error-rad",
        str(args.max_orientation_error_rad),
        "--max-angular-slack-rad-s",
        str(args.max_angular_slack_rad_s),
    ]
    return run_child(command, out_dir=out_dir)


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    lines = [
        "# Stage A Base-Z Recovery Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Recovered cases: `{aggregate['recovered_count']} / {aggregate['case_count']}`",
        f"- Start pass cases: `{', '.join(aggregate['start_pass_cases']) or 'none'}`",
        f"- Terminal pass cases: `{', '.join(aggregate['terminal_pass_cases']) or 'none'}`",
        f"- Path pass cases: `{', '.join(aggregate['path_pass_cases']) or 'none'}`",
        f"- Stitched pass cases: `{', '.join(aggregate['stitched_pass_cases']) or 'none'}`",
        f"- Unresolved cases: `{', '.join(aggregate['unresolved_cases']) or 'none'}`",
        "",
        "| case | status | Stage A duration s | start pass | terminal pass count | path pass | stitched pass | terminal orientation err rad | path min duration s | Stage B pass |",
        "| --- | --- | ---: | --- | ---: | --- | --- | ---: | ---: | ---: |",
    ]
    for case in cases:
        terminal = case["terminal"]
        start = case["start"]
        path = case["path"]
        stitched = case["stitched"]
        lines.append(
            "| `{case}` | `{status}` | `{stage_a_duration}` | `{start_pass}` | `{term_pass}` | `{path_pass}` | `{stitched_pass}` | `{orientation}` | `{duration}` | `{handoff}` |".format(
                case=case["case"],
                status=case["status"],
                stage_a_duration=case["stage_a_duration_s"],
                start_pass=start["passed"],
                term_pass=terminal["pass_count"],
                path_pass=None if path is None else path["path_gate_passed"],
                stitched_pass=None if stitched is None else stitched["stitched_gate_passed"],
                orientation=terminal["best_orientation_error_rad"],
                duration=None if path is None else path["min_duration_s"],
                handoff=None
                if stitched is None
                else f"{stitched['handoff_pass_count']}/{stitched['handoff_trajectory_count']}",
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- This audit tests perturbation-aware terminal target search and path reoptimization for the v64 1 mm base-z failures.",
            "- A recovered case requires a passing rebalanced start contact, passing terminal target, passing qdot-limited path gate at the listed Stage A duration, and passing stitched Stage A plus Stage B handoff.",
            "- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility, a robustness proof, or hardware readiness.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml")
    parser.add_argument("--setup-metrics", default="runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml")
    parser.add_argument("--stage-a-target-config", default="configs/ur10e_adapted_stage_a_target.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--random-seed-count", type=int, default=512)
    parser.add_argument("--random-seed-std-rad", type=float, default=0.15)
    parser.add_argument("--random-seed", type=int, default=37)
    parser.add_argument("--start-max-nfev", type=int, default=300)
    parser.add_argument("--start-posture-weight", type=float, default=0.01)
    parser.add_argument("--terminal-max-nfev", type=int, default=300)
    parser.add_argument("--posture-weight", type=float, default=1e-4)
    parser.add_argument("--knot-count", type=int, default=128)
    parser.add_argument("--path-max-nfev", type=int, default=200)
    parser.add_argument("--stage-a-duration-s", type=float, default=15.0)
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

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "stage_a_base_z_recovery" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    case_summaries = []
    for case_spec in DEFAULT_CASES:
        case_name = str(case_spec["name"])
        delta = float(case_spec["base_z_offset_delta_m"])
        stage_a_duration = float(case_spec["stage_a_duration_s"])
        case_dir = out_dir / "cases" / case_name
        start_dir = case_dir / "start"
        start_dir.mkdir(parents=True, exist_ok=True)
        start_metrics = start_metrics_for_case(
            case_name=case_name,
            base_z_offset_delta_m=delta,
            base_z_offset_nominal_m=base_z_offset_nominal,
            model_path=model_path,
            setup=setup,
            setup_path=setup_path,
            config_path=config_path,
            thresholds=thresholds,
            args=args,
            out_dir=start_dir,
        )
        terminal_dir = case_dir / "terminal"
        terminal_dir.mkdir(parents=True, exist_ok=True)
        terminal_metrics = terminal_metrics_for_case(
            case_name=case_name,
            base_z_offset_delta_m=delta,
            base_z_offset_nominal_m=base_z_offset_nominal,
            model_path=model_path,
            setup=setup,
            setup_path=setup_path,
            config_path=config_path,
            thresholds=thresholds,
            args=args,
            out_dir=terminal_dir,
        )
        path_metrics = None
        stitched_metrics = None
        if start_metrics["best_candidate"]["passed"] and terminal_metrics["best_candidate"]["passed"]:
            initial_q = parse_joint_vector(q_to_cli(start_metrics["best_candidate"]["q"]), expected_size=6)
            target_q = parse_joint_vector(q_to_cli(terminal_metrics["best_candidate"]["q"]), expected_size=6)
            path_dir = case_dir / "path"
            path_metrics = run_path_case(
                case_name=case_name,
                base_z_offset_delta_m=delta,
                stage_a_duration_s=stage_a_duration,
                initial_q=initial_q.tolist(),
                target_q=target_q.tolist(),
                args=args,
                out_dir=path_dir,
            )
            stitched_metrics = run_stitched_case(
                base_z_offset_delta_m=delta,
                stage_a_duration_s=stage_a_duration,
                source_path_csv=path_dir / "path.csv",
                args=args,
                out_dir=case_dir / "stitched",
            )
        case_summaries.append(
            summarize_base_z_recovery_case(
                case_name=case_name,
                base_z_offset_delta_m=delta,
                stage_a_duration_s=stage_a_duration,
                start_metrics=start_metrics,
                terminal_metrics=terminal_metrics,
                path_metrics=path_metrics,
                stitched_metrics=stitched_metrics,
            )
        )

    aggregate = aggregate_base_z_recovery(case_summaries)
    payload = {
        "run_id": run_id,
        "source": "perturbation-aware Stage A base-z terminal/path/stitch recovery audit",
        "case_specs": DEFAULT_CASES,
        "case_count": len(case_summaries),
        "diagnostic_gate": gate,
        "parameters": {
            "start_max_nfev": int(args.start_max_nfev),
            "start_posture_weight": float(args.start_posture_weight),
            "random_seed_count": int(args.random_seed_count),
            "random_seed_std_rad": float(args.random_seed_std_rad),
            "random_seed": int(args.random_seed),
            "terminal_max_nfev": int(args.terminal_max_nfev),
            "posture_weight": float(args.posture_weight),
            "knot_count": int(args.knot_count),
            "path_max_nfev": int(args.path_max_nfev),
            "stage_a_duration_s": float(args.stage_a_duration_s),
            "stage_b_duration_s": float(args.stage_b_duration_s),
            "target_force_N": float(args.target_force_N),
            "force_gain": float(args.force_gain),
            "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
            "paper_time_scale": float(args.paper_time_scale),
        },
        "aggregate": aggregate,
        "cases": case_summaries,
        "warnings": [
            "diagnostic-label simulation recovery audit only",
            "not strict paper-equivalent feasibility",
            "not a formal robustness proof",
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
