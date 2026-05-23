#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.force_feedback import simulate_tangential_force_motion, summarize_force_motion
from tase_repro.kinematics import joint_ranges, load_model


def parse_vector(text: str) -> np.ndarray:
    values = [float(part.strip()) for part in text.split(",")]
    return np.asarray(values, dtype=float)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--duration-s", type=float, default=4.0)
    parser.add_argument("--target-force-N", type=float, default=5.0)
    parser.add_argument("--force-gain", type=float, default=5e-5)
    parser.add_argument("--r", type=float, default=0.5)
    parser.add_argument("--base-z-offset-m", type=float, default=-4e-5)
    parser.add_argument("--initial-q", default="0,-0.02,0.03,-0.01,0,0")
    parser.add_argument("--tangential-velocity", default="0.0005,0.0")
    parser.add_argument("--tangential-kp", type=float, default=0.5)
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    model = load_model(model_path)
    q_min, q_max = joint_ranges(model)
    qdot_limit_cfg = cfg["ur10e_mujoco"]["joint_velocity_limit_rad_s"]
    qdot_min = np.asarray(qdot_limit_cfg["lower"], dtype=float)
    qdot_max = np.asarray(qdot_limit_cfg["upper"], dtype=float)
    dt_s = float(cfg["ur10e_mujoco"]["timestep_s"])

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = pathlib.Path(args.output_dir) if args.output_dir else ROOT / "runs" / "tangential_force_motion" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    result = simulate_tangential_force_motion(
        model_path,
        initial_q=parse_vector(args.initial_q),
        base_z_offset_m=args.base_z_offset_m,
        target_force_N=args.target_force_N,
        tangential_velocity_m_s=parse_vector(args.tangential_velocity),
        duration_s=args.duration_s,
        dt_s=dt_s,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        force_gain=args.force_gain,
        r=args.r,
        tangential_kp=args.tangential_kp,
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
        out_dir / "tangential-force-motion_raw.npz",
        q=result.q,
        qdot=result.qdot,
        tcp=result.tcp,
        desired_tcp=result.desired_tcp,
        force=result.force,
        commanded_linear_velocity=result.commanded_linear_velocity,
        actual_linear_velocity=result.actual_linear_velocity,
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
        "base_z_offset_m": float(args.base_z_offset_m),
        "force_gain": float(args.force_gain),
        "r": float(args.r),
        "tangential_velocity_m_s": [float(x) for x in parse_vector(args.tangential_velocity)],
        "tangential_kp": float(args.tangential_kp),
        **summary,
        "warnings": [
            "simulation-only force-motion smoke",
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
    plt.title("Tangential motion with normal-force feedback")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"tangential-force-motion_force_{run_id}.png", dpi=160)

    plt.figure(figsize=(6, 5))
    plt.plot(result.desired_tcp[:, 0], result.desired_tcp[:, 1], linestyle="--", label="desired")
    plt.plot(result.tcp[:, 0], result.tcp[:, 1], label="actual")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.title("Tangential path")
    plt.axis("equal")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"tangential-force-motion_xy_{run_id}.png", dpi=160)

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

