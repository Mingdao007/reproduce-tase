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

from tase_repro.force_feedback import simulate_stationary_force_feedback, summarize_force_feedback
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
    parser.add_argument("--gain", type=float, default=5e-5)
    parser.add_argument("--r", type=float, default=0.5)
    parser.add_argument("--base-z-offset-m", type=float, default=-4e-5)
    parser.add_argument("--initial-q", default="0,-0.02,0.03,-0.01,0,0")
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
    out_dir = pathlib.Path(args.output_dir) if args.output_dir else ROOT / "runs" / "stationary_force_feedback" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    result = simulate_stationary_force_feedback(
        model_path,
        initial_q=parse_vector(args.initial_q),
        base_z_offset_m=args.base_z_offset_m,
        target_force_N=args.target_force_N,
        duration_s=args.duration_s,
        dt_s=dt_s,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
        gain=args.gain,
        r=args.r,
    )
    summary = summarize_force_feedback(
        result,
        target_force_N=args.target_force_N,
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
    )

    np.savez(
        out_dir / "stationary-force-feedback_raw.npz",
        q=result.q,
        qdot=result.qdot,
        tcp=result.tcp,
        force=result.force,
        commanded_vz=result.commanded_vz,
        actual_vz=result.actual_vz,
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
        "gain": float(args.gain),
        "r": float(args.r),
        **summary,
        "warnings": [
            "simulation-only stationary contact feedback",
            "kinematic velocity-level controller",
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
    plt.title("Stationary force feedback")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"stationary-force-feedback_force_{run_id}.png", dpi=160)

    plt.figure(figsize=(8, 4))
    plt.plot(t, result.commanded_vz, label="commanded z velocity")
    plt.plot(t, result.actual_vz, label="actual z velocity")
    plt.xlabel("time [s]")
    plt.ylabel("z velocity [m/s]")
    plt.title("Stationary force feedback z velocity")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"stationary-force-feedback_vz_{run_id}.png", dpi=160)

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

