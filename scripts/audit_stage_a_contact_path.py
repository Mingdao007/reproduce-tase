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
from scipy.optimize import least_squares

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.contact_ladder import positive_contact_normal_force_between
from tase_repro.force_feedback import apply_base_z_offset
from tase_repro.kinematics import (
    joint_ranges,
    load_model,
    make_data,
    orientation_error_rotvec,
    set_qpos,
    site_position,
    site_rotation_matrix,
)
from tase_repro.stage_a_contact_path import (
    contact_path_timing,
    path_passes_diagnostic_terminal,
    rotation_slerp_path,
)
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


def evaluate_path(
    *,
    model: mujoco.MjModel,
    data: mujoco.MjData,
    q_path: np.ndarray,
    desired_xy_path: np.ndarray,
    desired_rotation_path: np.ndarray,
    reference_xy_m: np.ndarray,
    surface_normal_world: np.ndarray,
    target_force_N: float,
    site_name: str,
    plane_geom_name: str,
    contact_geom_name: str,
) -> dict[str, Any]:
    rows = []
    for idx, q in enumerate(q_path):
        set_qpos(model, data, q)
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
                "q": [float(x) for x in q],
                "force_N": float(force),
                "target_contact_count": int(contact_count),
                "force_error_N": abs(float(force) - float(target_force_N)),
                "scheduled_xy_error_m": float(np.linalg.norm(tcp[:2] - desired_xy_path[idx])),
                "reference_xy_error_m": float(np.linalg.norm(tcp[:2] - reference_xy_m)),
                "scheduled_orientation_error_rad": float(
                    np.linalg.norm(orientation_error_rotvec(desired_rotation_path[idx], rotation))
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


def write_path_csv(path: pathlib.Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "index",
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
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--knot-count", type=int, default=128)
    parser.add_argument("--max-nfev", type=int, default=200)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--duration-s", type=float, default=None)
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

    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    model = load_model(model_path)
    apply_base_z_offset(model, float(setup["base_z_offset_m"]))
    data = make_data(model)
    q_min, q_max = joint_ranges(model)
    site_name = str(setup["site_name"])
    plane_geom_name = str(setup["plane_geom_name"])
    contact_geom_name = str(setup["contact_geom_name"])
    target_force = float(setup["target_force_N"])
    q_initial = np.asarray(setup["initial_q"], dtype=float)
    q_target = np.asarray(target["q_rad"], dtype=float)
    reference_xy = np.asarray(setup["reference_xy_m"], dtype=float)
    surface_normal = np.asarray(setup["surface_normal_world"], dtype=float)

    set_qpos(model, data, q_initial)
    mujoco.mj_forward(model, data)
    start_xy = site_position(model, data, site_name)[:2].copy()
    start_rotation = site_rotation_matrix(model, data, site_name)
    set_qpos(model, data, q_target)
    mujoco.mj_forward(model, data)
    target_xy = site_position(model, data, site_name)[:2].copy()
    target_rotation = site_rotation_matrix(model, data, site_name)

    knot_count = int(args.knot_count)
    if knot_count < 3:
        raise ValueError("knot-count must be at least 3")
    alphas = np.linspace(0.0, 1.0, knot_count)
    desired_xy = (1.0 - alphas[:, None]) * start_xy + alphas[:, None] * target_xy
    desired_rotation = rotation_slerp_path(start_rotation, target_rotation, alphas)
    q_path = np.empty((knot_count, model.nq), dtype=float)
    q_path[0] = q_initial
    q_previous = q_initial.copy()
    solve_rows = []

    for idx, alpha in enumerate(alphas[1:-1], start=1):
        q_linear = (1.0 - alpha) * q_initial + alpha * q_target

        def residual(q: np.ndarray) -> np.ndarray:
            set_qpos(model, data, q)
            mujoco.mj_forward(model, data)
            tcp = site_position(model, data, site_name)
            rotation = site_rotation_matrix(model, data, site_name)
            force, _ = positive_contact_normal_force_between(
                model,
                data,
                geom_a_name=plane_geom_name,
                geom_b_name=contact_geom_name,
            )
            return np.r_[
                (force - target_force) / float(gate["max_terminal_force_error_N"]),
                (tcp[:2] - desired_xy[idx]) / float(gate["max_terminal_tangential_error_m"]),
                orientation_error_rotvec(desired_rotation[idx], rotation)
                / float(gate["max_terminal_orientation_error_rad"]),
                float(args.continuity_weight) * (q - q_previous),
                float(args.linear_posture_weight) * (q - q_linear),
            ]

        solve = least_squares(
            residual,
            q_previous,
            bounds=(q_min, q_max),
            max_nfev=int(args.max_nfev),
            ftol=1e-10,
            xtol=1e-10,
            gtol=1e-10,
        )
        q_path[idx] = solve.x
        q_previous = solve.x.copy()
        solve_rows.append(
            {
                "index": idx,
                "alpha": float(alpha),
                "success": bool(solve.success),
                "cost": float(solve.cost),
                "nfev": int(solve.nfev),
                "status": int(solve.status),
                "message": str(solve.message),
            }
        )
    q_path[-1] = q_target

    evaluation = evaluate_path(
        model=model,
        data=data,
        q_path=q_path,
        desired_xy_path=desired_xy,
        desired_rotation_path=desired_rotation,
        reference_xy_m=reference_xy,
        surface_normal_world=surface_normal,
        target_force_N=target_force,
        site_name=site_name,
        plane_geom_name=plane_geom_name,
        contact_geom_name=contact_geom_name,
    )
    timing = contact_path_timing(q_path, qdot_limit_rad_s=args.qdot_limit_rad_s, duration_s=args.duration_s)
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
    path_gate = {
        "passed": bool(
            evaluation["target_contact_present_fraction"] >= 1.0
            and evaluation["max_force_error_N"] <= float(gate["max_terminal_force_error_N"])
            and evaluation["max_scheduled_xy_error_m"] <= float(gate["max_terminal_tangential_error_m"])
            and evaluation["max_scheduled_orientation_error_rad"] <= float(gate["max_terminal_orientation_error_rad"])
            and timing.max_abs_qdot_rad_s <= float(args.qdot_limit_rad_s) + 1e-12
            and terminal_gate["passed"]
        ),
        "criteria": {
            "target_contact_present_fraction": evaluation["target_contact_present_fraction"],
            "max_force_error_N": evaluation["max_force_error_N"],
            "max_scheduled_xy_error_m": evaluation["max_scheduled_xy_error_m"],
            "max_scheduled_orientation_error_rad": evaluation["max_scheduled_orientation_error_rad"],
            "max_abs_qdot_rad_s": timing.max_abs_qdot_rad_s,
            "terminal_gate_passed": terminal_gate["passed"],
        },
    }

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "stage_a_contact_path_audit" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    write_path_csv(out_dir / "path.csv", evaluation["rows"])
    metrics = {
        "run_id": run_id,
        "config": str(config_path),
        "model": str(model_path),
        "setup_metrics": str(setup_path),
        "stage_a_target_config": str(target_config_path),
        "selected_target_label": target["label"],
        "claim_scope": "offline_quasi_static_contact_path_not_online_controller_or_hardware",
        "knot_count": knot_count,
        "max_nfev": int(args.max_nfev),
        "continuity_weight": float(args.continuity_weight),
        "linear_posture_weight": float(args.linear_posture_weight),
        "target_force_N": target_force,
        "diagnostic_gate": gate,
        "timing": timing.to_dict(),
        "evaluation": {key: value for key, value in evaluation.items() if key != "rows"},
        "terminal_gate": terminal_gate,
        "path_gate": path_gate,
        "solve_rows": solve_rows,
        "warnings": [
            "offline quasi-static contact-manifold path only",
            "not an online Stage A controller",
            "not strict paper-equivalent trajectory feasibility",
            "not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    lines = [
        "# Stage A Contact Path Audit Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Selected label: `{target['label']}`",
        f"- Knot count: `{knot_count}`",
        f"- Path gate pass: `{path_gate['passed']}`",
        f"- Terminal diagnostic gate pass: `{terminal_gate['passed']}`",
        f"- Min duration for qdot limit: `{timing.min_duration_s}`",
        f"- Max qdot at recorded duration: `{timing.max_abs_qdot_rad_s}`",
        f"- Target contact present fraction: `{evaluation['target_contact_present_fraction']}`",
        f"- Max force error: `{evaluation['max_force_error_N']}`",
        f"- Max scheduled x/y error: `{evaluation['max_scheduled_xy_error_m']}`",
        f"- Max scheduled orientation error: `{evaluation['max_scheduled_orientation_error_rad']}`",
        f"- Max force-normal orientation error along path: `{evaluation['max_force_normal_orientation_error_rad']}`",
        f"- Terminal force-normal orientation error: `{evaluation['terminal_force_normal_orientation_error_rad']}`",
        "",
        "Interpretation:",
        "",
        "- This is an offline quasi-static path through optimized contact-manifold knots.",
        "- It does not prove an online Stage A controller can track the path.",
        "- The terminal target still uses the diagnostic setup label, not the strict paper-equivalent setup label.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
