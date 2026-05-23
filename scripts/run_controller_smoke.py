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
import mujoco
import numpy as np
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.controller import CartesianVelocityCommand, solve_site_linear_velocity_step
from tase_repro.kinematics import joint_ranges, load_model, make_data, set_qpos, site_position


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--duration-s", type=float, default=2.0)
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    model = load_model(model_path)
    data = make_data(model)
    dt_s = float(cfg["ur10e_mujoco"]["timestep_s"])
    steps = int(round(args.duration_s / dt_s))
    site_name = "tcp_site_unverified_85mm"

    q_min, q_max = joint_ranges(model)
    qdot_limit_cfg = cfg["ur10e_mujoco"]["joint_velocity_limit_rad_s"]
    qdot_min = np.asarray(qdot_limit_cfg["lower"], dtype=float)
    qdot_max = np.asarray(qdot_limit_cfg["upper"], dtype=float)

    q = np.zeros(model.nq, dtype=float)
    set_qpos(model, data, q)

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = pathlib.Path(args.output_dir) if args.output_dir else ROOT / "runs" / "controller_smoke" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    q_hist = np.empty((steps, model.nq))
    qdot_hist = np.empty((steps, model.nv))
    tcp_hist = np.empty((steps, 3))
    desired_hist = np.empty((steps, 3))
    actual_hist = np.empty((steps, 3))
    residual_hist = np.empty(steps)
    solver_success = np.empty(steps, dtype=bool)
    active_bounds = np.empty(steps, dtype=int)

    for idx in range(steps):
        # A conservative no-contact kinematic smoke: lateral plus slight upward
        # velocity, avoiding the contact plane and hardware force assumptions.
        desired = np.array([0.002, 0.0, 0.001], dtype=float)
        command = CartesianVelocityCommand(desired, weight=1.0)
        set_qpos(model, data, q)
        result = solve_site_linear_velocity_step(
            model,
            data,
            site_name=site_name,
            q=q,
            command=command,
            dt=dt_s,
            q_min=q_min,
            q_max=q_max,
            qdot_min=qdot_min,
            qdot_max=qdot_max,
        )
        q = q + dt_s * result.qdot
        set_qpos(model, data, q)

        q_hist[idx] = q
        qdot_hist[idx] = result.qdot
        tcp_hist[idx] = site_position(model, data, site_name)
        desired_hist[idx] = result.desired_linear_velocity_m_s
        actual_hist[idx] = result.actual_linear_velocity_m_s
        residual_hist[idx] = result.residual_norm
        solver_success[idx] = result.solver_success
        active_bounds[idx] = result.active_bound_count

    joint_limit_violation = np.maximum(q_min - q_hist, 0.0) + np.maximum(q_hist - q_max, 0.0)
    qdot_violation = np.maximum(qdot_min - qdot_hist, 0.0) + np.maximum(qdot_hist - qdot_max, 0.0)
    tracking_error = actual_hist - desired_hist

    np.savez(
        out_dir / "controller-smoke_raw.npz",
        q=q_hist,
        qdot=qdot_hist,
        tcp=tcp_hist,
        desired_linear_velocity=desired_hist,
        actual_linear_velocity=actual_hist,
        residual=residual_hist,
        solver_success=solver_success,
        active_bounds=active_bounds,
    )

    metrics = {
        "config": str(config_path),
        "model": str(model_path),
        "run_id": run_id,
        "site_name": site_name,
        "duration_s": float(args.duration_s),
        "dt_s": dt_s,
        "steps": steps,
        "solver_success_fraction": float(np.mean(solver_success)),
        "max_abs_qdot_rad_s": float(np.max(np.abs(qdot_hist))),
        "max_qdot_violation_rad_s": float(np.max(qdot_violation)),
        "max_joint_limit_violation_rad": float(np.max(joint_limit_violation)),
        "mean_tracking_error_norm_m_s": float(np.mean(np.linalg.norm(tracking_error, axis=1))),
        "max_tracking_error_norm_m_s": float(np.max(np.linalg.norm(tracking_error, axis=1))),
        "max_active_bound_count": int(np.max(active_bounds)),
        "warnings": [
            "simulation-only velocity-level smoke",
            "not force control",
            "not contact control",
            "not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    t = np.arange(steps) * dt_s
    plt.figure(figsize=(8, 4))
    plt.plot(t, np.linalg.norm(tracking_error, axis=1))
    plt.xlabel("time [s]")
    plt.ylabel("linear velocity error norm [m/s]")
    plt.title("Controller smoke velocity tracking error")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_dir / f"controller-smoke_tracking-error_{run_id}.png", dpi=160)

    plt.figure(figsize=(8, 4))
    plt.plot(t, qdot_hist)
    plt.xlabel("time [s]")
    plt.ylabel("qdot [rad/s]")
    plt.title("Controller smoke joint velocities")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_dir / f"controller-smoke_qdot_{run_id}.png", dpi=160)

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

