#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.force_feedback import simulate_planar_force_motion, summarize_force_motion
from tase_repro.kinematics import joint_ranges, load_model
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
    values = [float(part.strip()) for part in text.split(",")]
    return np.asarray(values, dtype=float)


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--duration-s", type=float, default=8.0)
    parser.add_argument("--target-force-N", type=float, default=5.0)
    parser.add_argument("--force-gain", type=float, default=5e-5)
    parser.add_argument("--r", type=float, default=0.5)
    parser.add_argument("--base-z-offset-m", type=float, default=-4e-5)
    parser.add_argument("--initial-q", default="0,-0.02,0.03,-0.01,0,0")
    parser.add_argument("--qdot-limit-rad-s", type=float, default=None)
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
    parser.add_argument("--paper-time-scale", type=float, default=1.0)
    parser.add_argument("--zero-initial-offset", dest="zero_initial_offset", action="store_true", default=True)
    parser.add_argument("--no-zero-initial-offset", dest="zero_initial_offset", action="store_false")
    parser.add_argument("--planar-kp", type=float, default=0.5)
    parser.add_argument("--planar-axis-weight", type=float, default=1.0)
    parser.add_argument("--normal-axis-weight", type=float, default=1.0)
    parser.add_argument("--normal-guard-force-fraction", type=float, default=None)
    parser.add_argument("--normal-guard-min-planar-scale", type=float, default=0.0)
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    model = load_model(model_path)
    q_min, q_max = joint_ranges(model)
    qdot_limit_cfg = cfg["ur10e_mujoco"]["joint_velocity_limit_rad_s"]
    if args.qdot_limit_rad_s is None:
        qdot_min = np.asarray(qdot_limit_cfg["lower"], dtype=float)
        qdot_max = np.asarray(qdot_limit_cfg["upper"], dtype=float)
        qdot_limit_source = qdot_limit_cfg["source"]
    else:
        qdot_limit = abs(float(args.qdot_limit_rad_s))
        qdot_min = np.full(model.nv, -qdot_limit, dtype=float)
        qdot_max = np.full(model.nv, qdot_limit, dtype=float)
        qdot_limit_source = "cli_override"
    dt_s = float(cfg["ur10e_mujoco"]["timestep_s"])

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = pathlib.Path(args.output_dir) if args.output_dir else ROOT / "runs" / "paper_trajectory_force_motion" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    result = simulate_planar_force_motion(
        model_path,
        initial_q=parse_vector(args.initial_q),
        base_z_offset_m=args.base_z_offset_m,
        target_force_N=args.target_force_N,
        planar_trajectory=build_trajectory(args),
        duration_s=args.duration_s,
        dt_s=dt_s,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        force_gain=args.force_gain,
        r=args.r,
        planar_kp=args.planar_kp,
        axis_weights=np.array([args.planar_axis_weight, args.planar_axis_weight, args.normal_axis_weight]),
        normal_guard_force_fraction=args.normal_guard_force_fraction,
        normal_guard_min_planar_scale=args.normal_guard_min_planar_scale,
    )
    summary = summarize_force_motion(
        result,
        target_force_N=args.target_force_N,
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
    )

    np.savez(
        out_dir / "paper-trajectory-force-motion_raw.npz",
        q=result.q,
        qdot=result.qdot,
        tcp=result.tcp,
        desired_tcp=result.desired_tcp,
        force=result.force,
        commanded_linear_velocity=result.commanded_linear_velocity,
        actual_linear_velocity=result.actual_linear_velocity,
        linear_velocity_residual=result.linear_velocity_residual,
        planar_scale=result.planar_scale,
        solver_success=result.solver_success,
        active_bounds=result.active_bounds,
        contact_count=result.contact_count,
    )

    metrics = {
        "config": str(config_path),
        "model": str(model_path),
        "run_id": run_id,
        "duration_s": float(args.duration_s),
        "dt_s": dt_s,
        "steps": int(len(result.force)),
        "initial_q": [float(x) for x in parse_vector(args.initial_q)],
        "qdot_limit_source": qdot_limit_source,
        "qdot_min_rad_s": [float(x) for x in qdot_min],
        "qdot_max_rad_s": [float(x) for x in qdot_max],
        "base_z_offset_m": float(args.base_z_offset_m),
        "force_gain": float(args.force_gain),
        "r": float(args.r),
        "trajectory": args.trajectory,
        "paper_formula": PAPER_FORMULAS[args.trajectory],
        "amplitude_m": float(args.amplitude_m),
        "amplitude_x_m": float(args.amplitude_x_m),
        "amplitude_y_m": float(args.amplitude_y_m),
        "radius_m": float(args.radius_m),
        "omega_rad_s": float(args.omega_rad_s),
        "paper_time_scale": float(args.paper_time_scale),
        "zero_initial_offset": bool(args.zero_initial_offset),
        "planar_kp": float(args.planar_kp),
        "axis_weights": [
            float(args.planar_axis_weight),
            float(args.planar_axis_weight),
            float(args.normal_axis_weight),
        ],
        "normal_guard_force_fraction": None
        if args.normal_guard_force_fraction is None
        else float(args.normal_guard_force_fraction),
        "normal_guard_min_planar_scale": float(args.normal_guard_min_planar_scale),
        **summary,
        "warnings": [
            "simulation-only paper-trajectory-shaped force-motion smoke",
            "uses MuJoCo contact force rather than hardware force sensing",
            "kinematic velocity-level controller",
            "no orientation compliance yet",
            "not torque dynamics",
            "not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    t = np.arange(len(result.force)) * dt_s
    plt.figure(figsize=(8, 4))
    plt.plot(t, result.force, label="measured")
    plt.axhline(args.target_force_N, linestyle="--", color="black", label="target")
    plt.xlabel("time [s]")
    plt.ylabel("normal force [N]")
    plt.title("Paper trajectory with normal-force feedback")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"paper-trajectory-force-motion_force_{run_id}.png", dpi=160)

    plt.figure(figsize=(6, 5))
    plt.plot(result.desired_tcp[:, 0], result.desired_tcp[:, 1], linestyle="--", label="desired")
    plt.plot(result.tcp[:, 0], result.tcp[:, 1], label="actual")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.title(f"Paper trajectory path: {args.trajectory}")
    plt.axis("equal")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"paper-trajectory-force-motion_xy_{run_id}.png", dpi=160)

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
