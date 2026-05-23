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
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.contact_ladder import calibrate_base_z_for_target_force


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--tail-steps", type=int, default=100)
    parser.add_argument("--tolerance-N", type=float, default=0.01)
    parser.add_argument("--lower-offset-m", type=float, default=0.0)
    parser.add_argument("--upper-offset-m", type=float, default=0.002)
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    targets = [float(x) for x in cfg["ur10e_mujoco"]["force_ladder_N"]]
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = pathlib.Path(args.output_dir) if args.output_dir else ROOT / "runs" / "contact_force_ladder" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for target in targets:
        meas = calibrate_base_z_for_target_force(
            model_path,
            target_force_N=target,
            lower_offset_m=args.lower_offset_m,
            upper_offset_m=args.upper_offset_m,
            steps=args.steps,
            tail_steps=args.tail_steps,
            tolerance_N=args.tolerance_N,
        )
        rows.append(
            {
                "target_force_N": target,
                "base_z_offset_m": meas.base_z_offset_m,
                "mean_normal_force_N": meas.mean_normal_force_N,
                "force_error_N": meas.mean_normal_force_N - target,
                "max_normal_force_N": meas.max_normal_force_N,
                "final_tcp_z_m": meas.final_tcp_z_m,
                "mean_contact_count": meas.mean_contact_count,
            }
        )

    max_abs_error = max(abs(row["force_error_N"]) for row in rows)
    metrics = {
        "config": str(config_path),
        "model": str(model_path),
        "run_id": run_id,
        "steps": int(args.steps),
        "tail_steps": int(args.tail_steps),
        "tolerance_N": float(args.tolerance_N),
        "lower_offset_m": float(args.lower_offset_m),
        "upper_offset_m": float(args.upper_offset_m),
        "contact_force_sign": "positive MuJoCo contact-frame normal wrench[0]",
        "modeling_method": "base_link z offset static penetration calibration",
        "max_abs_force_error_N": float(max_abs_error),
        "ladder": rows,
        "warnings": [
            "simulation-only contact-model probe",
            "base_link z offsets are not robot commands",
            "not closed-loop force control",
            "not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    target_values = [row["target_force_N"] for row in rows]
    measured_values = [row["mean_normal_force_N"] for row in rows]
    offsets_mm = [1000.0 * row["base_z_offset_m"] for row in rows]

    plt.figure(figsize=(6, 4))
    plt.plot(target_values, measured_values, marker="o", label="measured")
    plt.plot(target_values, target_values, linestyle="--", label="target")
    plt.xlabel("target force [N]")
    plt.ylabel("measured mean normal force [N]")
    plt.title("Static contact force ladder")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"contact-force-ladder_target-vs-measured_{run_id}.png", dpi=160)

    plt.figure(figsize=(6, 4))
    plt.plot(target_values, offsets_mm, marker="o")
    plt.xlabel("target force [N]")
    plt.ylabel("base z offset [mm]")
    plt.title("Static contact force ladder offsets")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_dir / f"contact-force-ladder_offsets_{run_id}.png", dpi=160)

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

