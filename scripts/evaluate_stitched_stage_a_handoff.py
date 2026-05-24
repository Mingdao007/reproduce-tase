#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import pathlib
import subprocess
import sys
from collections.abc import Callable
from typing import Any

import mujoco
import numpy as np
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.contact_ladder import positive_contact_normal_force_between
from tase_repro.feasibility import FeasibilityThresholds, evaluate_force_motion_feasibility
from tase_repro.force_feedback import apply_base_z_offset, simulate_planar_force_motion, summarize_force_motion
from tase_repro.kinematics import (
    joint_ranges,
    load_model,
    make_data,
    orientation_error_rotvec,
    set_qpos,
    site_position,
    site_rotation_matrix,
)
from tase_repro.stage_a_contact_path import path_passes_diagnostic_terminal, rotation_slerp_path
from tase_repro.stage_a_contact_path_tracking import replay_qdot_limited_joint_path
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


def force_normal_orientation_error(rotation: np.ndarray, normal: np.ndarray) -> float:
    local_z = np.asarray(rotation, dtype=float)[:, 2]
    normal_unit = np.asarray(normal, dtype=float)
    local_z = local_z / np.linalg.norm(local_z)
    normal_unit = normal_unit / np.linalg.norm(normal_unit)
    return float(np.arccos(np.clip(float(np.dot(local_z, normal_unit)), -1.0, 1.0)))


def read_path_csv(path: pathlib.Path) -> np.ndarray:
    rows = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append([float(row[f"q{idx}"]) for idx in range(6)])
    if len(rows) < 2:
        raise ValueError(f"path CSV must contain at least two rows: {path}")
    return np.asarray(rows, dtype=float)


def evaluate_stage_a_tracking(
    *,
    model: mujoco.MjModel,
    data: mujoco.MjData,
    q: np.ndarray,
    alpha: np.ndarray,
    start_xy: np.ndarray,
    target_xy: np.ndarray,
    start_rotation: np.ndarray,
    target_rotation: np.ndarray,
    reference_xy_m: np.ndarray,
    surface_normal_world: np.ndarray,
    target_force_N: float,
    site_name: str,
    plane_geom_name: str,
    contact_geom_name: str,
) -> dict[str, Any]:
    desired_xy = (1.0 - alpha[:, None]) * start_xy + alpha[:, None] * target_xy
    desired_rotation = rotation_slerp_path(start_rotation, target_rotation, alpha)
    rows = []
    for idx, q_i in enumerate(q):
        set_qpos(model, data, q_i)
        mujoco.mj_forward(model, data)
        tcp = site_position(model, data, site_name)
        rotation = site_rotation_matrix(model, data, site_name)
        force, contact_count = positive_contact_normal_force_between(
            model,
            data,
            geom_a_name=plane_geom_name,
            geom_b_name=contact_geom_name,
        )
        rows.append(
            {
                "index": idx,
                "force_N": float(force),
                "target_contact_count": int(contact_count),
                "force_error_N": abs(float(force) - float(target_force_N)),
                "scheduled_xy_error_m": float(np.linalg.norm(tcp[:2] - desired_xy[idx])),
                "reference_xy_error_m": float(np.linalg.norm(tcp[:2] - reference_xy_m)),
                "scheduled_orientation_error_rad": float(
                    np.linalg.norm(orientation_error_rotvec(desired_rotation[idx], rotation))
                ),
                "force_normal_orientation_error_rad": force_normal_orientation_error(rotation, surface_normal_world),
            }
        )
    force_errors = np.array([row["force_error_N"] for row in rows], dtype=float)
    contact_counts = np.array([row["target_contact_count"] for row in rows], dtype=int)
    scheduled_xy_errors = np.array([row["scheduled_xy_error_m"] for row in rows], dtype=float)
    reference_xy_errors = np.array([row["reference_xy_error_m"] for row in rows], dtype=float)
    scheduled_orientation_errors = np.array([row["scheduled_orientation_error_rad"] for row in rows], dtype=float)
    force_normal_orientation_errors = np.array(
        [row["force_normal_orientation_error_rad"] for row in rows],
        dtype=float,
    )
    return {
        "target_contact_present_fraction": float(np.mean(contact_counts > 0)),
        "min_target_contact_count": int(np.min(contact_counts)),
        "max_force_error_N": float(np.max(force_errors)),
        "terminal_force_error_N": float(force_errors[-1]),
        "max_scheduled_xy_error_m": float(np.max(scheduled_xy_errors)),
        "max_reference_xy_error_m": float(np.max(reference_xy_errors)),
        "terminal_reference_xy_error_m": float(reference_xy_errors[-1]),
        "max_scheduled_orientation_error_rad": float(np.max(scheduled_orientation_errors)),
        "max_force_normal_orientation_error_rad": float(np.max(force_normal_orientation_errors)),
        "terminal_force_normal_orientation_error_rad": float(force_normal_orientation_errors[-1]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml")
    parser.add_argument("--setup-metrics", default="runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml")
    parser.add_argument("--stage-a-target-config", default="configs/ur10e_adapted_stage_a_target.yaml")
    parser.add_argument("--source-path-csv", default="runs/stage_a_contact_path_audit/20260524T151201/path.csv")
    parser.add_argument("--output-dir", default=None)
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
    parser.add_argument("--trajectories", default=",".join(TRAJECTORY_ORDER))
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
    diagnostic_gate = target["diagnostic_gate"]
    path_csv = (ROOT / args.source_path_csv).resolve()
    q_path = read_path_csv(path_csv)

    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    dt_s = float(cfg["ur10e_mujoco"]["timestep_s"])
    base_z_offset = float(setup["base_z_offset_m"])
    qdot_limit = abs(float(args.qdot_limit_rad_s))
    target_force = float(args.target_force_N)

    stage_a_model = load_model(model_path)
    apply_base_z_offset(stage_a_model, base_z_offset)
    stage_a_data = make_data(stage_a_model)
    site_name = str(setup["site_name"])
    plane_geom_name = str(setup["plane_geom_name"])
    contact_geom_name = str(setup["contact_geom_name"])
    reference_xy = np.asarray(setup["reference_xy_m"], dtype=float)
    surface_normal = np.asarray(setup["surface_normal_world"], dtype=float)

    set_qpos(stage_a_model, stage_a_data, q_path[0])
    mujoco.mj_forward(stage_a_model, stage_a_data)
    start_xy = site_position(stage_a_model, stage_a_data, site_name)[:2].copy()
    start_rotation = site_rotation_matrix(stage_a_model, stage_a_data, site_name)
    set_qpos(stage_a_model, stage_a_data, q_path[-1])
    mujoco.mj_forward(stage_a_model, stage_a_data)
    target_xy = site_position(stage_a_model, stage_a_data, site_name)[:2].copy()
    target_rotation = site_rotation_matrix(stage_a_model, stage_a_data, site_name)

    stage_a_tracking = replay_qdot_limited_joint_path(
        q_path,
        duration_s=args.stage_a_duration_s,
        dt_s=dt_s,
        qdot_limit_rad_s=qdot_limit,
    )
    stage_a_tracking_summary = stage_a_tracking.summary()
    stage_a_evaluation = evaluate_stage_a_tracking(
        model=stage_a_model,
        data=stage_a_data,
        q=stage_a_tracking.q,
        alpha=stage_a_tracking.alpha,
        start_xy=start_xy,
        target_xy=target_xy,
        start_rotation=start_rotation,
        target_rotation=target_rotation,
        reference_xy_m=reference_xy,
        surface_normal_world=surface_normal,
        target_force_N=target_force,
        site_name=site_name,
        plane_geom_name=plane_geom_name,
        contact_geom_name=contact_geom_name,
    )
    terminal_gate = path_passes_diagnostic_terminal(
        terminal_force_error_N=stage_a_evaluation["terminal_force_error_N"],
        terminal_xy_error_m=stage_a_evaluation["terminal_reference_xy_error_m"],
        terminal_force_normal_orientation_error_rad=stage_a_evaluation[
            "terminal_force_normal_orientation_error_rad"
        ],
        target_contact_count=stage_a_evaluation["min_target_contact_count"],
        force_threshold_N=float(diagnostic_gate["max_terminal_force_error_N"]),
        xy_threshold_m=float(diagnostic_gate["max_terminal_tangential_error_m"]),
        orientation_threshold_rad=float(diagnostic_gate["max_terminal_orientation_error_rad"]),
        min_target_contact_count=int(diagnostic_gate["min_target_contact_count"]),
    )
    stage_a_gate = {
        "passed": bool(
            stage_a_evaluation["target_contact_present_fraction"] >= 1.0
            and stage_a_evaluation["max_force_error_N"] <= float(diagnostic_gate["max_terminal_force_error_N"])
            and stage_a_evaluation["max_scheduled_xy_error_m"]
            <= float(diagnostic_gate["max_terminal_tangential_error_m"])
            and stage_a_evaluation["max_scheduled_orientation_error_rad"]
            <= float(diagnostic_gate["max_terminal_orientation_error_rad"])
            and stage_a_tracking_summary["max_abs_qdot_rad_s"] <= qdot_limit + 1e-12
            and stage_a_tracking_summary["final_tracking_error_norm_rad"] <= 1e-9
            and terminal_gate["passed"]
        ),
        "criteria": {
            "target_contact_present_fraction": stage_a_evaluation["target_contact_present_fraction"],
            "max_force_error_N": stage_a_evaluation["max_force_error_N"],
            "max_scheduled_xy_error_m": stage_a_evaluation["max_scheduled_xy_error_m"],
            "max_scheduled_orientation_error_rad": stage_a_evaluation["max_scheduled_orientation_error_rad"],
            "max_abs_qdot_rad_s": stage_a_tracking_summary["max_abs_qdot_rad_s"],
            "final_tracking_error_norm_rad": stage_a_tracking_summary["final_tracking_error_norm_rad"],
            "terminal_gate_passed": terminal_gate["passed"],
        },
    }

    handoff_model = load_model(model_path)
    q_min, q_max = joint_ranges(handoff_model)
    qdot_min = np.full(handoff_model.nv, -qdot_limit, dtype=float)
    qdot_max = np.full(handoff_model.nv, qdot_limit, dtype=float)
    thresholds = FeasibilityThresholds(
        max_orientation_error_rad_max=args.max_orientation_error_rad,
        max_angular_velocity_slack_rad_s_max=args.max_angular_slack_rad_s,
    )
    rows = []
    trajectory_names = [name.strip() for name in args.trajectories.split(",") if name.strip()]
    stage_b_initial_q = stage_a_tracking.q[-1]
    for name in trajectory_names:
        result = simulate_planar_force_motion(
            model_path,
            initial_q=stage_b_initial_q,
            base_z_offset_m=base_z_offset,
            target_force_N=target_force,
            planar_trajectory=build_trajectory(name, time_scale=args.paper_time_scale),
            duration_s=args.stage_b_duration_s,
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
            target_force_N=target_force,
            q_min=q_min,
            q_max=q_max,
            qdot_min=qdot_min,
            qdot_max=qdot_max,
        )
        target_pair_summary = summarize_handoff_result(
            result,
            model_path=model_path,
            base_z_offset_m=base_z_offset,
            target_force_N=target_force,
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
                "duration_s": float(args.stage_b_duration_s),
                "dt_s": dt_s,
                "target_pair_metrics": target_pair_metrics,
                "total_force_metrics": total_force_metrics,
                "target_pair_summary": target_pair_summary,
                "feasibility_gate": gate,
            }
        )

    handoff_pass_count = sum(1 for row in rows if row["feasibility_gate"]["feasibility_pass"])
    stitched_gate = {
        "passed": bool(stage_a_gate["passed"] and handoff_pass_count == len(rows)),
        "stage_a_passed": stage_a_gate["passed"],
        "handoff_pass_count": handoff_pass_count,
        "handoff_trajectory_count": len(rows),
    }

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "stitched_stage_a_handoff_eval" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = {
        "run_id": run_id,
        "config": str(config_path),
        "model": str(model_path),
        "setup_metrics": str(setup_path),
        "stage_a_target_config": str(target_config_path),
        "source_path_csv": str(path_csv),
        "selected_target_label": target["label"],
        "claim_scope": "stitched_diagnostic_stage_a_tracking_and_stage_b_handoff_not_paper_or_hardware",
        "target_force_N": target_force,
        "base_z_offset_m": base_z_offset,
        "qdot_limit_rad_s": qdot_limit,
        "stage_a_duration_s": float(args.stage_a_duration_s),
        "stage_b_duration_s": float(args.stage_b_duration_s),
        "force_gain": float(args.force_gain),
        "r": float(args.r),
        "planar_kp": float(args.planar_kp),
        "orientation_kp": float(args.orientation_kp),
        "paper_time_scale": float(args.paper_time_scale),
        "stage_a": {
            "tracking": stage_a_tracking_summary,
            "evaluation": stage_a_evaluation,
            "terminal_gate": terminal_gate,
            "stage_a_gate": stage_a_gate,
        },
        "stage_b": {
            "handoff_pass_count": handoff_pass_count,
            "trajectory_count": len(rows),
            "rows": rows,
        },
        "stitched_gate": stitched_gate,
        "warnings": [
            "diagnostic selected-target staged prototype only",
            "Stage A is qdot-limited joint-path replay of the v61 path",
            "Stage B uses the v60 slowed low-gain handoff parameters",
            "not strict paper-equivalent trajectory feasibility",
            "not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    lines = [
        "# Stitched Stage A Tracking + Stage B Handoff Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Selected label: `{target['label']}`",
        f"- Stitched gate pass: `{stitched_gate['passed']}`",
        f"- Stage A gate pass: `{stage_a_gate['passed']}`",
        f"- Stage B handoff passes: `{handoff_pass_count} / {len(rows)}`",
        f"- Stage A duration: `{args.stage_a_duration_s}`",
        f"- Stage B duration per trajectory: `{args.stage_b_duration_s}`",
        f"- Stage A max qdot: `{stage_a_tracking_summary['max_abs_qdot_rad_s']}`",
        f"- Stage A qdot saturation fraction: `{stage_a_tracking_summary['qdot_saturation_fraction']}`",
        "",
        "| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        metrics_row = row["target_pair_metrics"]
        gate = row["feasibility_gate"]
        lines.append(
            "| `{trajectory}` | `{passed}` | `{failed}` | `{force}` | `{xy}` | `{orientation}` | `{qdot}` | `{contact}` |".format(
                trajectory=row["trajectory"],
                passed=gate["feasibility_pass"],
                failed=";".join(gate["failed_criteria"]) or "none",
                force=metrics_row["tail_mean_abs_force_error_N"],
                xy=metrics_row["max_tangential_position_error_m"],
                orientation=metrics_row["max_orientation_error_rad"],
                qdot=metrics_row["qdot_saturation_fraction"],
                contact=metrics_row["contact_present_fraction"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.",
            "- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.",
            "- It is not hardware-ready.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
