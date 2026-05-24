#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Any

import mujoco
import numpy as np
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.contact_ladder import positive_contact_normal_force_between
from tase_repro.force_feedback import apply_base_z_offset
from tase_repro.kinematics import (
    load_model,
    make_data,
    orientation_error_rotvec,
    set_qpos,
    site_position,
    site_rotation_matrix,
)
from tase_repro.stage_a_contact_path import (
    path_passes_diagnostic_terminal,
    rotation_slerp_path,
)
from tase_repro.stage_a_contact_path_tracking import replay_qdot_limited_joint_path
from tase_repro.stage_a_target_handoff import load_stage_a_target_config, selected_stage_a_target


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


def evaluate_tracking(
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
                "time_alpha": float(alpha[idx]),
                "q": [float(x) for x in q_i],
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
        "rows": rows,
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


def write_tracking_csv(path: pathlib.Path, rows: list[dict[str, Any]], time_s: np.ndarray) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(
            [
                "index",
                "time_s",
                "q0",
                "q1",
                "q2",
                "q3",
                "q4",
                "q5",
                "force_N",
                "target_contact_count",
                "force_error_N",
                "scheduled_xy_error_m",
                "reference_xy_error_m",
                "scheduled_orientation_error_rad",
                "force_normal_orientation_error_rad",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row["index"],
                    time_s[row["index"]],
                    *row["q"],
                    row["force_N"],
                    row["target_contact_count"],
                    row["force_error_N"],
                    row["scheduled_xy_error_m"],
                    row["reference_xy_error_m"],
                    row["scheduled_orientation_error_rad"],
                    row["force_normal_orientation_error_rad"],
                ]
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml")
    parser.add_argument("--setup-metrics", default="runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml")
    parser.add_argument("--stage-a-target-config", default="configs/ur10e_adapted_stage_a_target.yaml")
    parser.add_argument("--source-path-csv", default="runs/stage_a_contact_path_audit/20260524T151201/path.csv")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--duration-s", type=float, default=15.0)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
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
    path_csv = (ROOT / args.source_path_csv).resolve()
    q_path = read_path_csv(path_csv)

    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    model = load_model(model_path)
    apply_base_z_offset(model, float(setup["base_z_offset_m"]))
    data = make_data(model)
    site_name = str(setup["site_name"])
    plane_geom_name = str(setup["plane_geom_name"])
    contact_geom_name = str(setup["contact_geom_name"])
    target_force = float(setup["target_force_N"])
    reference_xy = np.asarray(setup["reference_xy_m"], dtype=float)
    surface_normal = np.asarray(setup["surface_normal_world"], dtype=float)
    dt_s = float(cfg["ur10e_mujoco"]["timestep_s"])

    set_qpos(model, data, q_path[0])
    mujoco.mj_forward(model, data)
    start_xy = site_position(model, data, site_name)[:2].copy()
    start_rotation = site_rotation_matrix(model, data, site_name)
    set_qpos(model, data, q_path[-1])
    mujoco.mj_forward(model, data)
    target_xy = site_position(model, data, site_name)[:2].copy()
    target_rotation = site_rotation_matrix(model, data, site_name)

    tracking = replay_qdot_limited_joint_path(
        q_path,
        duration_s=args.duration_s,
        dt_s=dt_s,
        qdot_limit_rad_s=args.qdot_limit_rad_s,
    )
    tracking_summary = tracking.summary()
    evaluation = evaluate_tracking(
        model=model,
        data=data,
        q=tracking.q,
        alpha=tracking.alpha,
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
        terminal_force_error_N=evaluation["terminal_force_error_N"],
        terminal_xy_error_m=evaluation["terminal_reference_xy_error_m"],
        terminal_force_normal_orientation_error_rad=evaluation["terminal_force_normal_orientation_error_rad"],
        target_contact_count=evaluation["rows"][-1]["target_contact_count"],
        force_threshold_N=float(gate["max_terminal_force_error_N"]),
        xy_threshold_m=float(gate["max_terminal_tangential_error_m"]),
        orientation_threshold_rad=float(gate["max_terminal_orientation_error_rad"]),
        min_target_contact_count=int(gate["min_target_contact_count"]),
    )
    tracking_gate = {
        "passed": bool(
            evaluation["target_contact_present_fraction"] >= 1.0
            and evaluation["max_force_error_N"] <= float(gate["max_terminal_force_error_N"])
            and evaluation["max_scheduled_xy_error_m"] <= float(gate["max_terminal_tangential_error_m"])
            and evaluation["max_scheduled_orientation_error_rad"] <= float(gate["max_terminal_orientation_error_rad"])
            and tracking_summary["max_abs_qdot_rad_s"] <= float(args.qdot_limit_rad_s) + 1e-12
            and tracking_summary["final_tracking_error_norm_rad"] <= 1e-9
            and terminal_gate["passed"]
        ),
        "criteria": {
            "target_contact_present_fraction": evaluation["target_contact_present_fraction"],
            "max_force_error_N": evaluation["max_force_error_N"],
            "max_scheduled_xy_error_m": evaluation["max_scheduled_xy_error_m"],
            "max_scheduled_orientation_error_rad": evaluation["max_scheduled_orientation_error_rad"],
            "max_abs_qdot_rad_s": tracking_summary["max_abs_qdot_rad_s"],
            "final_tracking_error_norm_rad": tracking_summary["final_tracking_error_norm_rad"],
            "terminal_gate_passed": terminal_gate["passed"],
        },
    }

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "stage_a_contact_path_tracking" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    write_tracking_csv(out_dir / "tracking_trace.csv", evaluation["rows"], tracking.time_s)
    metrics = {
        "run_id": run_id,
        "config": str(config_path),
        "model": str(model_path),
        "setup_metrics": str(setup_path),
        "stage_a_target_config": str(target_config_path),
        "source_path_csv": str(path_csv),
        "selected_target_label": target["label"],
        "claim_scope": "qdot_limited_joint_path_tracking_prototype_not_stage_b_or_hardware",
        "duration_s": float(args.duration_s),
        "dt_s": dt_s,
        "target_force_N": target_force,
        "diagnostic_gate": gate,
        "tracking": tracking_summary,
        "evaluation": {key: value for key, value in evaluation.items() if key != "rows"},
        "terminal_gate": terminal_gate,
        "tracking_gate": tracking_gate,
        "warnings": [
            "tracks the v61 offline path with qdot-limited joint replay",
            "not a force-feedback path optimizer",
            "not connected to Stage B handoff in this run",
            "not strict paper-equivalent trajectory feasibility",
            "not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    lines = [
        "# Stage A Contact Path Tracking Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Selected label: `{target['label']}`",
        f"- Source path: `{path_csv}`",
        f"- Duration: `{args.duration_s}`",
        f"- Tracking gate pass: `{tracking_gate['passed']}`",
        f"- Terminal diagnostic gate pass: `{terminal_gate['passed']}`",
        f"- Max qdot: `{tracking_summary['max_abs_qdot_rad_s']}`",
        f"- Qdot saturation fraction: `{tracking_summary['qdot_saturation_fraction']}`",
        f"- Final tracking error norm: `{tracking_summary['final_tracking_error_norm_rad']}`",
        f"- Target contact present fraction: `{evaluation['target_contact_present_fraction']}`",
        f"- Max force error: `{evaluation['max_force_error_N']}`",
        f"- Max scheduled x/y error: `{evaluation['max_scheduled_xy_error_m']}`",
        f"- Max scheduled orientation error: `{evaluation['max_scheduled_orientation_error_rad']}`",
        f"- Terminal force-normal orientation error: `{evaluation['terminal_force_normal_orientation_error_rad']}`",
        "",
        "Interpretation:",
        "",
        "- This is a qdot-limited joint-path tracking prototype for the v61 offline path.",
        "- It does not connect the tracked Stage A path to the v60 Stage B handoff.",
        "- It is not a hardware-readiness or strict paper-equivalent claim.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
