#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from collections.abc import Callable

import numpy as np
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.feasibility import FeasibilityThresholds, evaluate_force_motion_feasibility
from tase_repro.force_feedback import simulate_planar_force_motion, summarize_force_motion
from tase_repro.kinematics import joint_ranges, load_model
from tase_repro.stage_a_target_handoff import (
    load_stage_a_target_config,
    metrics_with_target_pair_force,
    selected_stage_a_target,
    summarize_handoff_result,
)
from tase_repro.trajectories import (
    PlanarTrajectoryState,
    paper_e1_cycloid_planar_state,
    paper_e2_figure_eight_planar_state,
    paper_e3_circle_planar_state,
    paper_e4_cardioid_planar_state,
)


TRAJECTORY_ORDER = ["e1-cycloid", "e2-figure-eight", "e3-circle", "e4-cardioid"]


def build_trajectory(name: str, *, time_scale: float) -> Callable[[float], PlanarTrajectoryState]:
    if name == "e1-cycloid":
        return lambda t_s: paper_e1_cycloid_planar_state(t_s, time_scale=time_scale)
    if name == "e2-figure-eight":
        return lambda t_s: paper_e2_figure_eight_planar_state(t_s, time_scale=time_scale)
    if name == "e3-circle":
        return lambda t_s: paper_e3_circle_planar_state(t_s, time_scale=time_scale, zero_initial_offset=True)
    if name == "e4-cardioid":
        return lambda t_s: paper_e4_cardioid_planar_state(t_s, time_scale=time_scale, zero_initial_offset=True)
    raise ValueError(f"unknown trajectory: {name}")


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml")
    parser.add_argument("--stage-a-target-config", default="configs/ur10e_adapted_stage_a_target.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--duration-s", type=float, default=2.0)
    parser.add_argument("--target-force-N", type=float, default=5.0)
    parser.add_argument("--force-gain", type=float, default=5e-4)
    parser.add_argument("--r", type=float, default=0.5)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--planar-kp", type=float, default=0.5)
    parser.add_argument("--paper-time-scale", type=float, default=0.075)
    parser.add_argument("--orientation-kp", type=float, default=0.1)
    parser.add_argument("--max-orientation-error-rad", type=float, default=0.08)
    parser.add_argument("--max-angular-slack-rad-s", type=float, default=0.03)
    parser.add_argument("--trajectories", default=",".join(TRAJECTORY_ORDER))
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    target_config_path = (ROOT / args.stage_a_target_config).resolve()
    target_config = load_stage_a_target_config(target_config_path)
    selected = selected_stage_a_target(target_config)
    initial_q = np.asarray(selected["q_rad"], dtype=float)

    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    model = load_model(model_path)
    q_min, q_max = joint_ranges(model)
    qdot_limit = abs(float(args.qdot_limit_rad_s))
    qdot_min = np.full(model.nv, -qdot_limit, dtype=float)
    qdot_max = np.full(model.nv, qdot_limit, dtype=float)
    dt_s = float(cfg["ur10e_mujoco"]["timestep_s"])
    base_z_offset = float(cfg["ur10e_mujoco"]["contact"]["calibrated_bend_0p10_base_z_offset_m_for_5N"])
    trajectory_names = [name.strip() for name in args.trajectories.split(",") if name.strip()]

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "stage_a_target_handoff_eval" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    thresholds = FeasibilityThresholds(
        max_orientation_error_rad_max=args.max_orientation_error_rad,
        max_angular_velocity_slack_rad_s_max=args.max_angular_slack_rad_s,
    )
    rows = []
    for name in trajectory_names:
        result = simulate_planar_force_motion(
            model_path,
            initial_q=initial_q,
            base_z_offset_m=base_z_offset,
            target_force_N=args.target_force_N,
            planar_trajectory=build_trajectory(name, time_scale=args.paper_time_scale),
            duration_s=args.duration_s,
            dt_s=dt_s,
            qdot_min=qdot_min,
            qdot_max=qdot_max,
            force_gain=args.force_gain,
            r=args.r,
            planar_kp=args.planar_kp,
            axis_weights=np.ones(3, dtype=float),
            slack_axis_weights=np.array([1.0, 1.0, 10000.0], dtype=float),
            slack_constraint_weight=1000.0,
            normal_velocity_mode="contact_normal",
            orientation_mode="force_normal",
            orientation_priority_mode="linear_primary",
            orientation_kp=args.orientation_kp,
            angular_axis_weights=np.ones(3, dtype=float),
            angular_slack_axis_weights=np.ones(3, dtype=float),
        )
        total_force_metrics = summarize_force_motion(
            result,
            target_force_N=args.target_force_N,
            q_min=q_min,
            q_max=q_max,
            qdot_min=qdot_min,
            qdot_max=qdot_max,
        )
        target_pair_summary = summarize_handoff_result(
            result,
            model_path=model_path,
            base_z_offset_m=base_z_offset,
            target_force_N=args.target_force_N,
        )
        target_pair_metrics = metrics_with_target_pair_force(total_force_metrics, target_pair_summary)
        gate = evaluate_force_motion_feasibility(
            target_pair_metrics,
            thresholds=thresholds,
            qdot_abs_limit_rad_s=qdot_limit,
        )
        rows.append(
            {
                "trajectory": name,
                "duration_s": float(args.duration_s),
                "dt_s": dt_s,
                "target_pair_metrics": target_pair_metrics,
                "total_force_metrics": total_force_metrics,
                "target_pair_summary": target_pair_summary,
                "feasibility_gate": gate,
            }
        )

    pass_count = sum(1 for row in rows if row["feasibility_gate"]["feasibility_pass"])
    aggregate = {
        "run_id": run_id,
        "config": str(config_path),
        "model": str(model_path),
        "stage_a_target_config": str(target_config_path),
        "selected_target_label": selected["label"],
        "claim_scope": "diagnostic_target_handoff_only_not_stage_a_path_or_hardware",
        "initial_q": [float(x) for x in initial_q],
        "target_force_N": float(args.target_force_N),
        "base_z_offset_m": base_z_offset,
        "qdot_limit_rad_s": qdot_limit,
        "force_gain": float(args.force_gain),
        "r": float(args.r),
        "planar_kp": float(args.planar_kp),
        "orientation_kp": float(args.orientation_kp),
        "max_orientation_error_rad": float(args.max_orientation_error_rad),
        "max_angular_slack_rad_s": float(args.max_angular_slack_rad_s),
        "duration_s": float(args.duration_s),
        "paper_time_scale": float(args.paper_time_scale),
        "handoff_pass_count": pass_count,
        "trajectory_count": len(rows),
        "rows": rows,
        "warnings": [
            "starts directly from the selected diagnostic terminal target",
            "does not implement or validate a Stage A path to the target",
            "uses target contact pair force for the feasibility gate",
            "simulation-only and not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(aggregate, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(aggregate, f, indent=2)

    lines = [
        "# Stage A Target Handoff Evaluation Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        "Scope: start directly from the v58 selected diagnostic terminal target and evaluate Stage B handoff.",
        "",
        f"- Selected label: `{selected['label']}`",
        f"- Handoff passes: `{pass_count} / {len(rows)}`",
        "",
        "| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        metrics = row["target_pair_metrics"]
        gate = row["feasibility_gate"]
        lines.append(
            "| `{trajectory}` | `{passed}` | `{failed}` | `{force}` | `{xy}` | `{orientation}` | `{qdot}` | `{contact}` |".format(
                trajectory=row["trajectory"],
                passed=gate["feasibility_pass"],
                failed=";".join(gate["failed_criteria"]) or "none",
                force=metrics["tail_mean_abs_force_error_N"],
                xy=metrics["max_tangential_position_error_m"],
                orientation=metrics["max_orientation_error_rad"],
                qdot=metrics["qdot_saturation_fraction"],
                contact=metrics["contact_present_fraction"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- This is a handoff audit, not Stage A path feasibility.",
            "- A failure here means the selected terminal target is not enough for a trajectory claim.",
            "- A pass here would still require a separate Stage A path controller to reach the target.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
