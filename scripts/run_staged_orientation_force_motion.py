#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.feasibility import FeasibilityThresholds, evaluate_force_motion_feasibility
from tase_repro.force_feedback import ForceMotionResult, summarize_force_motion
from tase_repro.kinematics import joint_ranges, load_model
from tase_repro.staged_force_motion import simulate_orientation_prealign_then_planar_force_motion
from tase_repro.trajectories import (
    PlanarTrajectoryState,
    paper_e1_cycloid_planar_state,
    paper_e2_figure_eight_planar_state,
    paper_e3_circle_planar_state,
    paper_e4_cardioid_planar_state,
)

PAPER_FORMULAS = {
    "e1-cycloid": "x=x0+0.015*(0.1*t-sin(0.1*t)); y=y0+0.015*(1-cos(0.1*t))",
    "e2-figure-eight": "x=x0+0.04*sin(0.1*t); y=y0+0.01*sin(0.2*t)",
    "e3-circle": "x=x0+0.03*cos(0.1*t); y=y0+0.03*sin(0.1*t)",
    "e4-cardioid": "x=x0+0.015*(2*cos(0.1*t)-cos(0.2*t)); y=y0+0.015*(2*sin(0.1*t)-sin(0.2*t))",
}


def parse_vector(text: str) -> np.ndarray:
    return np.asarray([float(part.strip()) for part in text.split(",")], dtype=float)


def build_trajectory(args: argparse.Namespace) -> Callable[[float], PlanarTrajectoryState]:
    if args.trajectory == "e1-cycloid":
        return lambda t_s: paper_e1_cycloid_planar_state(
            t_s,
            amplitude_m=args.amplitude_m,
            omega_rad_s=args.omega_rad_s,
            time_scale=args.paper_time_scale,
        )
    if args.trajectory == "e2-figure-eight":
        return lambda t_s: paper_e2_figure_eight_planar_state(
            t_s,
            amplitude_x_m=args.amplitude_x_m,
            amplitude_y_m=args.amplitude_y_m,
            omega_rad_s=args.omega_rad_s,
            time_scale=args.paper_time_scale,
        )
    if args.trajectory == "e3-circle":
        return lambda t_s: paper_e3_circle_planar_state(
            t_s,
            radius_m=args.radius_m,
            omega_rad_s=args.omega_rad_s,
            time_scale=args.paper_time_scale,
            zero_initial_offset=args.zero_initial_offset,
        )
    if args.trajectory == "e4-cardioid":
        return lambda t_s: paper_e4_cardioid_planar_state(
            t_s,
            amplitude_m=args.amplitude_m,
            omega_rad_s=args.omega_rad_s,
            time_scale=args.paper_time_scale,
            zero_initial_offset=args.zero_initial_offset,
        )
    raise ValueError(f"unknown trajectory: {args.trajectory}")


def write_git_state(out_dir: pathlib.Path, *, command: list[str]) -> None:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
    content = "\n".join(
        [
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
    )
    (out_dir / "git_state.md").write_text(content, encoding="utf-8")


def phase_prefix(phase: str) -> str:
    return f"staged-{phase}"


def write_phase_artifacts(
    phase_dir: pathlib.Path,
    *,
    phase: str,
    result: ForceMotionResult,
    metrics: dict,
    dt_s: float,
    run_id: str,
    target_force_N: float,
    trajectory_name: str,
) -> None:
    phase_dir.mkdir(parents=True, exist_ok=True)
    prefix = phase_prefix(phase)
    np.savez(
        phase_dir / f"{prefix}_raw.npz",
        q=result.q,
        qdot=result.qdot,
        tcp=result.tcp,
        desired_tcp=result.desired_tcp,
        tcp_rotation=result.tcp_rotation,
        desired_tcp_rotation=result.desired_tcp_rotation,
        orientation_error_rotvec=result.orientation_error_rotvec,
        force=result.force,
        commanded_linear_velocity=result.commanded_linear_velocity,
        commanded_angular_velocity=result.commanded_angular_velocity,
        commanded_joint_velocity_target=result.commanded_joint_velocity_target,
        actual_linear_velocity=result.actual_linear_velocity,
        actual_angular_velocity=result.actual_angular_velocity,
        linear_velocity_residual=result.linear_velocity_residual,
        angular_velocity_residual=result.angular_velocity_residual,
        task_slack_linear_velocity=result.task_slack_linear_velocity,
        task_slack_angular_velocity=result.task_slack_angular_velocity,
        planar_scale=result.planar_scale,
        solver_success=result.solver_success,
        active_bounds=result.active_bounds,
        contact_count=result.contact_count,
    )
    with (phase_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (phase_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    t = np.arange(len(result.force)) * dt_s
    plt.figure(figsize=(8, 4))
    plt.plot(t, result.force, label="measured")
    plt.axhline(target_force_N, linestyle="--", color="black", label="target")
    plt.xlabel("time [s]")
    plt.ylabel("normal force [N]")
    plt.title(f"{phase} normal-force feedback")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(phase_dir / f"{prefix}_force_{run_id}.png", dpi=160)
    plt.close()

    plt.figure(figsize=(6, 5))
    plt.plot(result.desired_tcp[:, 0], result.desired_tcp[:, 1], linestyle="--", label="desired")
    plt.plot(result.tcp[:, 0], result.tcp[:, 1], label="actual")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.title(f"{phase} path: {trajectory_name}")
    plt.axis("equal")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(phase_dir / f"{prefix}_xy_{run_id}.png", dpi=160)
    plt.close()

    orientation_error = np.linalg.norm(result.orientation_error_rotvec, axis=1)
    angular_slack = np.linalg.norm(result.task_slack_angular_velocity, axis=1)
    plt.figure(figsize=(8, 4))
    plt.plot(t, orientation_error, label="orientation error")
    plt.xlabel("time [s]")
    plt.ylabel("angle [rad]")
    plt.title(f"{phase} force-normal orientation error")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(phase_dir / f"{prefix}_orientation_{run_id}.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 4))
    plt.plot(t, angular_slack, label="angular slack")
    plt.xlabel("time [s]")
    plt.ylabel("slack [rad/s]")
    plt.title(f"{phase} angular slack")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(phase_dir / f"{prefix}_angular-slack_{run_id}.png", dpi=160)
    plt.close()


def build_thresholds(args: argparse.Namespace) -> FeasibilityThresholds:
    return FeasibilityThresholds(
        max_orientation_error_rad_max=args.max_orientation_error_rad,
        max_angular_velocity_slack_rad_s_max=args.max_angular_slack_rad_s,
    )


def phase_metrics(
    *,
    phase: str,
    result: ForceMotionResult,
    summary: dict,
    args: argparse.Namespace,
    dt_s: float,
    qdot_limit_source: str,
    qdot_min: np.ndarray,
    qdot_max: np.ndarray,
    joint_posture_target: np.ndarray | None,
    joint_posture_kp: float,
    joint_posture_weight: float,
    max_joint_posture_velocity_rad_s: float | None,
) -> dict:
    return {
        "phase": phase,
        "duration_s": float(len(result.force) * dt_s),
        "dt_s": dt_s,
        "steps": int(len(result.force)),
        "qdot_limit_source": qdot_limit_source,
        "qdot_min_rad_s": [float(x) for x in qdot_min],
        "qdot_max_rad_s": [float(x) for x in qdot_max],
        "target_force_N": float(args.target_force_N),
        "force_gain": float(args.force_gain),
        "r": float(args.r),
        "normal_velocity_mode": args.normal_velocity_mode,
        "planar_kp": float(args.planar_kp),
        "joint_posture_target": None
        if joint_posture_target is None
        else [float(x) for x in joint_posture_target],
        "joint_posture_kp": float(joint_posture_kp),
        "joint_posture_weight": float(joint_posture_weight),
        "max_joint_posture_velocity_rad_s": None
        if max_joint_posture_velocity_rad_s is None
        else float(max_joint_posture_velocity_rad_s),
        "use_slack_solve": True,
        "slack_axis_weights": [
            float(args.planar_slack_weight),
            float(args.planar_slack_weight),
            float(args.normal_slack_weight),
        ],
        "slack_constraint_weight": float(args.slack_constraint_weight),
        **summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e_tilted_plane.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--approach-duration-s", type=float, default=4.0)
    parser.add_argument("--trajectory-duration-s", type=float, default=2.0)
    parser.add_argument("--target-force-N", type=float, default=5.0)
    parser.add_argument("--force-gain", type=float, default=5e-4)
    parser.add_argument("--r", type=float, default=0.5)
    parser.add_argument("--base-z-offset-m", type=float, default=-0.0011631221220595766)
    parser.add_argument("--initial-q", default="0,-0.1,0.15,-0.05,0,0")
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--approach-qdot-limit-rad-s", type=float, default=None)
    parser.add_argument("--trajectory-qdot-limit-rad-s", type=float, default=None)
    parser.add_argument(
        "--trajectory",
        choices=["e1-cycloid", "e2-figure-eight", "e3-circle", "e4-cardioid"],
        default="e1-cycloid",
    )
    parser.add_argument("--amplitude-m", type=float, default=0.015)
    parser.add_argument("--amplitude-x-m", type=float, default=0.04)
    parser.add_argument("--amplitude-y-m", type=float, default=0.01)
    parser.add_argument("--radius-m", type=float, default=0.03)
    parser.add_argument("--omega-rad-s", type=float, default=0.1)
    parser.add_argument("--paper-time-scale", type=float, default=0.075)
    parser.add_argument("--zero-initial-offset", dest="zero_initial_offset", action="store_true", default=True)
    parser.add_argument("--no-zero-initial-offset", dest="zero_initial_offset", action="store_false")
    parser.add_argument("--planar-kp", type=float, default=0.5)
    parser.add_argument("--planar-axis-weight", type=float, default=1.0)
    parser.add_argument("--normal-axis-weight", type=float, default=1.0)
    parser.add_argument("--planar-slack-weight", type=float, default=1.0)
    parser.add_argument("--normal-slack-weight", type=float, default=10000.0)
    parser.add_argument("--slack-constraint-weight", type=float, default=1000.0)
    parser.add_argument("--normal-velocity-mode", choices=["world-z", "contact-normal"], default="contact-normal")
    parser.add_argument("--approach-orientation-priority-mode", choices=["weighted", "linear-primary"], default="weighted")
    parser.add_argument("--approach-orientation-kp", type=float, default=2.0)
    parser.add_argument("--approach-max-angular-command-rad-s", type=float, default=None)
    parser.add_argument("--trajectory-orientation-priority-mode", choices=["weighted", "linear-primary"], default="linear-primary")
    parser.add_argument("--trajectory-orientation-kp", type=float, default=0.1)
    parser.add_argument("--trajectory-max-angular-command-rad-s", type=float, default=None)
    parser.add_argument("--angular-axis-weight", type=float, default=1.0)
    parser.add_argument("--angular-slack-weight", type=float, default=1.0)
    parser.add_argument("--approach-posture-target-q", default=None)
    parser.add_argument("--trajectory-posture-target-q", default=None)
    parser.add_argument("--approach-posture-kp", type=float, default=0.0)
    parser.add_argument("--trajectory-posture-kp", type=float, default=0.0)
    parser.add_argument("--approach-posture-weight", type=float, default=0.0)
    parser.add_argument("--trajectory-posture-weight", type=float, default=0.0)
    parser.add_argument("--approach-max-posture-velocity-rad-s", type=float, default=None)
    parser.add_argument("--trajectory-max-posture-velocity-rad-s", type=float, default=None)
    parser.add_argument("--approach-orientation-threshold-rad", type=float, default=0.03)
    parser.add_argument("--max-orientation-error-rad", type=float, default=0.03)
    parser.add_argument("--max-angular-slack-rad-s", type=float, default=0.03)
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    model = load_model(model_path)
    q_min, q_max = joint_ranges(model)
    qdot_limit = abs(float(args.qdot_limit_rad_s))
    approach_qdot_limit = qdot_limit if args.approach_qdot_limit_rad_s is None else abs(float(args.approach_qdot_limit_rad_s))
    trajectory_qdot_limit = (
        qdot_limit if args.trajectory_qdot_limit_rad_s is None else abs(float(args.trajectory_qdot_limit_rad_s))
    )
    approach_qdot_min = np.full(model.nv, -approach_qdot_limit, dtype=float)
    approach_qdot_max = np.full(model.nv, approach_qdot_limit, dtype=float)
    trajectory_qdot_min = np.full(model.nv, -trajectory_qdot_limit, dtype=float)
    trajectory_qdot_max = np.full(model.nv, trajectory_qdot_limit, dtype=float)
    approach_qdot_limit_source = (
        "approach_cli_override" if args.approach_qdot_limit_rad_s is not None else "cli_override"
    )
    trajectory_qdot_limit_source = (
        "trajectory_cli_override" if args.trajectory_qdot_limit_rad_s is not None else "cli_override"
    )
    approach_posture_target = None if args.approach_posture_target_q is None else parse_vector(args.approach_posture_target_q)
    trajectory_posture_target = (
        None if args.trajectory_posture_target_q is None else parse_vector(args.trajectory_posture_target_q)
    )
    dt_s = float(cfg["ur10e_mujoco"]["timestep_s"])
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = pathlib.Path(args.output_dir) if args.output_dir else ROOT / "runs" / "staged_orientation_force_motion" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    staged = simulate_orientation_prealign_then_planar_force_motion(
        model_path,
        initial_q=parse_vector(args.initial_q),
        base_z_offset_m=args.base_z_offset_m,
        target_force_N=args.target_force_N,
        planar_trajectory=build_trajectory(args),
        approach_duration_s=args.approach_duration_s,
        trajectory_duration_s=args.trajectory_duration_s,
        dt_s=dt_s,
        qdot_min=approach_qdot_min,
        qdot_max=approach_qdot_max,
        trajectory_qdot_min=trajectory_qdot_min,
        trajectory_qdot_max=trajectory_qdot_max,
        force_gain=args.force_gain,
        r=args.r,
        planar_kp=args.planar_kp,
        axis_weights=np.array([args.planar_axis_weight, args.planar_axis_weight, args.normal_axis_weight]),
        slack_axis_weights=np.array([args.planar_slack_weight, args.planar_slack_weight, args.normal_slack_weight]),
        slack_constraint_weight=args.slack_constraint_weight,
        normal_velocity_mode=args.normal_velocity_mode.replace("-", "_"),
        approach_orientation_priority_mode=args.approach_orientation_priority_mode.replace("-", "_"),
        approach_orientation_kp=args.approach_orientation_kp,
        approach_max_angular_command_rad_s=args.approach_max_angular_command_rad_s,
        trajectory_orientation_priority_mode=args.trajectory_orientation_priority_mode.replace("-", "_"),
        trajectory_orientation_kp=args.trajectory_orientation_kp,
        trajectory_max_angular_command_rad_s=args.trajectory_max_angular_command_rad_s,
        angular_axis_weights=np.full(3, args.angular_axis_weight, dtype=float),
        angular_slack_axis_weights=np.full(3, args.angular_slack_weight, dtype=float),
        approach_joint_posture_target=approach_posture_target,
        approach_joint_posture_kp=args.approach_posture_kp,
        approach_joint_posture_weight=args.approach_posture_weight,
        approach_max_joint_posture_velocity_rad_s=args.approach_max_posture_velocity_rad_s,
        trajectory_joint_posture_target=trajectory_posture_target,
        trajectory_joint_posture_kp=args.trajectory_posture_kp,
        trajectory_joint_posture_weight=args.trajectory_posture_weight,
        trajectory_max_joint_posture_velocity_rad_s=args.trajectory_max_posture_velocity_rad_s,
        approach_orientation_threshold_rad=args.approach_orientation_threshold_rad,
    )
    approach_summary = summarize_force_motion(
        staged.approach,
        target_force_N=args.target_force_N,
        q_min=q_min,
        q_max=q_max,
        qdot_min=approach_qdot_min,
        qdot_max=approach_qdot_max,
    )
    trajectory_summary = summarize_force_motion(
        staged.trajectory,
        target_force_N=args.target_force_N,
        q_min=q_min,
        q_max=q_max,
        qdot_min=trajectory_qdot_min,
        qdot_max=trajectory_qdot_max,
    )
    thresholds = build_thresholds(args)
    approach_gate = evaluate_force_motion_feasibility(
        approach_summary,
        thresholds=thresholds,
        qdot_abs_limit_rad_s=approach_qdot_limit,
    )
    trajectory_gate = evaluate_force_motion_feasibility(
        trajectory_summary,
        thresholds=thresholds,
        qdot_abs_limit_rad_s=trajectory_qdot_limit,
    )
    approach_terminal_gate = {
        "final_orientation_error_rad": staged.approach_final_orientation_error_rad,
        "threshold_rad": float(args.approach_orientation_threshold_rad),
        "passed": staged.approach_final_orientation_error_rad <= float(args.approach_orientation_threshold_rad),
    }
    approach_metrics = phase_metrics(
        phase="approach",
        result=staged.approach,
        summary=approach_summary,
        args=args,
        dt_s=dt_s,
        qdot_limit_source=approach_qdot_limit_source,
        qdot_min=approach_qdot_min,
        qdot_max=approach_qdot_max,
        joint_posture_target=approach_posture_target,
        joint_posture_kp=args.approach_posture_kp,
        joint_posture_weight=args.approach_posture_weight,
        max_joint_posture_velocity_rad_s=args.approach_max_posture_velocity_rad_s,
    )
    approach_metrics.update(
        {
            "orientation_priority_mode": args.approach_orientation_priority_mode,
            "orientation_kp": float(args.approach_orientation_kp),
            "max_angular_command_rad_s": args.approach_max_angular_command_rad_s,
            "orientation_threshold_rad": float(args.approach_orientation_threshold_rad),
            "reached_threshold": bool(staged.approach_reached_threshold),
            "first_threshold_index": staged.approach_first_threshold_index,
            "first_threshold_time_s": staged.approach_first_threshold_time_s,
            "final_orientation_error_rad": staged.approach_final_orientation_error_rad,
            "feasibility_gate": approach_gate,
            "terminal_orientation_gate": approach_terminal_gate,
        }
    )
    trajectory_metrics = phase_metrics(
        phase="trajectory",
        result=staged.trajectory,
        summary=trajectory_summary,
        args=args,
        dt_s=dt_s,
        qdot_limit_source=trajectory_qdot_limit_source,
        qdot_min=trajectory_qdot_min,
        qdot_max=trajectory_qdot_max,
        joint_posture_target=trajectory_posture_target,
        joint_posture_kp=args.trajectory_posture_kp,
        joint_posture_weight=args.trajectory_posture_weight,
        max_joint_posture_velocity_rad_s=args.trajectory_max_posture_velocity_rad_s,
    )
    trajectory_metrics.update(
        {
            "trajectory": args.trajectory,
            "paper_formula": PAPER_FORMULAS[args.trajectory],
            "paper_time_scale": float(args.paper_time_scale),
            "orientation_priority_mode": args.trajectory_orientation_priority_mode,
            "orientation_kp": float(args.trajectory_orientation_kp),
            "max_angular_command_rad_s": args.trajectory_max_angular_command_rad_s,
            "initial_q": [float(x) for x in staged.trajectory_initial_q],
            "feasibility_gate": trajectory_gate,
        }
    )

    write_phase_artifacts(
        out_dir / "approach",
        phase="approach",
        result=staged.approach,
        metrics=approach_metrics,
        dt_s=dt_s,
        run_id=run_id,
        target_force_N=args.target_force_N,
        trajectory_name="stationary",
    )
    write_phase_artifacts(
        out_dir / "trajectory",
        phase="trajectory",
        result=staged.trajectory,
        metrics=trajectory_metrics,
        dt_s=dt_s,
        run_id=run_id,
        target_force_N=args.target_force_N,
        trajectory_name=args.trajectory,
    )

    trajectory_after_approach_pass = bool(
        approach_terminal_gate["passed"]
        and trajectory_gate["feasibility_pass"]
        and approach_summary["max_qdot_violation_rad_s"] <= thresholds.max_qdot_violation_rad_s_max
        and approach_summary["max_joint_limit_violation_rad"] <= thresholds.max_joint_limit_violation_rad_max
    )
    full_staged_feasibility_pass = bool(approach_gate["feasibility_pass"] and trajectory_gate["feasibility_pass"])
    aggregate = {
        "config": str(config_path),
        "model": str(model_path),
        "run_id": run_id,
        "initial_q": [float(x) for x in parse_vector(args.initial_q)],
        "base_z_offset_m": float(args.base_z_offset_m),
        "trajectory": args.trajectory,
        "paper_formula": PAPER_FORMULAS[args.trajectory],
        "paper_time_scale": float(args.paper_time_scale),
        "approach_duration_s": float(args.approach_duration_s),
        "trajectory_duration_s": float(args.trajectory_duration_s),
        "approach_qdot_limit_rad_s": approach_qdot_limit,
        "trajectory_qdot_limit_rad_s": trajectory_qdot_limit,
        "dt_s": dt_s,
        "thresholds": thresholds.to_dict(),
        "approach": approach_metrics,
        "trajectory_phase": trajectory_metrics,
        "trajectory_after_approach_pass": trajectory_after_approach_pass,
        "full_staged_feasibility_pass": full_staged_feasibility_pass,
        "staged_pass": full_staged_feasibility_pass,
        "warnings": [
            "simulation-only staged tilted-plane force-normal orientation approach",
            "approach phase may spend qdot saturation budget and must be evaluated separately",
            "uses MuJoCo contact force rather than hardware force sensing",
            "kinematic velocity-level controller",
            "not torque dynamics",
            "not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(aggregate, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(aggregate, f, indent=2)
    summary_lines = [
        "# Staged Orientation Force-Motion Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        "## Result",
        "",
        f"- Approach final orientation error: `{staged.approach_final_orientation_error_rad}`",
        f"- Approach first threshold time: `{staged.approach_first_threshold_time_s}`",
        f"- Approach qdot saturation fraction: `{approach_summary['qdot_saturation_fraction']}`",
        f"- Trajectory feasibility pass: `{trajectory_gate['feasibility_pass']}`",
        f"- Trajectory failed criteria: `{';'.join(trajectory_gate['failed_criteria']) or 'none'}`",
        f"- Trajectory max orientation error: `{trajectory_summary['max_orientation_error_rad']}`",
        f"- Trajectory qdot saturation fraction: `{trajectory_summary['qdot_saturation_fraction']}`",
        f"- Trajectory after approach pass: `{aggregate['trajectory_after_approach_pass']}`",
        f"- Full staged feasibility pass: `{aggregate['full_staged_feasibility_pass']}`",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
