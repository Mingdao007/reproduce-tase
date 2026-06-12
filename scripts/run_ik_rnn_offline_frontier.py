#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Any

import matplotlib
import numpy as np
import yaml

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.force_feedback import apply_base_z_offset  # noqa: E402
from tase_repro.ik_rnn import run_ik_rnn_frontier  # noqa: E402
from tase_repro.kinematics import (  # noqa: E402
    load_model,
    make_data,
    set_qpos,
    site_position,
    site_rotation_matrix,
)


DEFAULT_CONFIG = "configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml"
DEFAULT_SITE = "tcp_site_unverified_85mm"
DEFAULT_INITIAL_Q = "0.1,-0.4,0.3,-0.2,0.15,0.0"
DEFAULT_TARGET_OFFSET_M = "0.002,-0.001,0.0005"
DEFAULT_TARGET_ROT_OFFSET_RAD = "0.0,0.0,0.03"


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


def resolve(path: str | pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(path)
    if path.is_absolute():
        return path
    return ROOT / path


def rel(path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_vector(value: str, *, length: int, name: str) -> np.ndarray:
    parts = [float(part.strip()) for part in value.split(",") if part.strip()]
    if len(parts) != length:
        raise ValueError(f"{name} must contain {length} comma-separated values")
    return np.asarray(parts, dtype=float)


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(payload, f, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True)


def git_value(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def write_git_state(out_dir: pathlib.Path, *, command: list[str]) -> None:
    branch = git_value(["branch", "--show-current"])
    commit = git_value(["rev-parse", "HEAD"])
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
    lines = [
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
    (out_dir / "git_state.md").write_text("\n".join(lines), encoding="utf-8")


def rotation_matrix_from_rotvec(rotvec: np.ndarray) -> np.ndarray:
    vector = np.asarray(rotvec, dtype=float)
    theta = float(np.linalg.norm(vector))
    if theta == 0.0:
        return np.eye(3)
    axis = vector / theta
    skew = np.array(
        [
            [0.0, -axis[2], axis[1]],
            [axis[2], 0.0, -axis[0]],
            [-axis[1], axis[0], 0.0],
        ],
        dtype=float,
    )
    return np.eye(3) + np.sin(theta) * skew + (1.0 - np.cos(theta)) * (skew @ skew)


def build_claim_boundary() -> dict[str, bool]:
    return {
        "offline_ik_rnn_frontier_only": True,
        "live_hardware_accessed_by_this_run": False,
        "robot_motion_authorized": False,
        "hardware_writes_authorized": False,
        "force_control_authorized": False,
        "contact_force_gap_resolved": False,
        "contact_model_acceptance_claim": False,
        "setup_target_acceptance_claim": False,
        "strict_paper_equivalent_feasibility": False,
        "robustness_claim": False,
        "hardware_readiness": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }


def save_plots(out_dir: pathlib.Path, run_id: str, arrays: dict[str, np.ndarray]) -> dict[str, str]:
    time = arrays["time_s"]
    pos_mm = arrays["position_error_m"] * 1000.0
    pos_norm_mm = np.linalg.norm(arrays["position_error_m"], axis=1) * 1000.0
    orient_norm_deg = np.linalg.norm(arrays["orientation_error_rotvec"], axis=1) * 180.0 / np.pi
    qdot = arrays["qdot"]
    qdot_abs_max = np.max(np.abs(qdot), axis=1)
    active_bounds = arrays["active_bound_count"]

    paths: dict[str, str] = {}

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(time, pos_mm[:, 0], label="x error")
    ax.plot(time, pos_mm[:, 1], label="y error")
    ax.plot(time, pos_mm[:, 2], label="z error")
    ax.plot(time, pos_norm_mm, label="norm", linewidth=2.0)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("position error (mm)")
    ax.set_title("IK/RNN TCP position error")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    path = out_dir / f"ik-rnn-position-error_{run_id}.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    paths["position_error"] = rel(path)

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(time, orient_norm_deg, label="orientation error")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("orientation error (deg)")
    ax.set_title("IK/RNN orientation error")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    path = out_dir / f"ik-rnn-orientation-error_{run_id}.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    paths["orientation_error"] = rel(path)

    fig, ax1 = plt.subplots(figsize=(7.2, 4.2))
    ax1.plot(time, qdot_abs_max, label="max |qdot|")
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("max |qdot| (rad/s)")
    ax1.grid(True, alpha=0.3)
    ax2 = ax1.twinx()
    ax2.step(time, active_bounds, color="tab:orange", where="post", label="active bounds")
    ax2.set_ylabel("active bound count")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="best")
    ax1.set_title("IK/RNN qdot usage and active bounds")
    fig.tight_layout()
    path = out_dir / f"ik-rnn-qdot-utilization_{run_id}.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    paths["qdot_utilization"] = rel(path)

    return paths


def build_payload(args: argparse.Namespace, *, out_dir: pathlib.Path, run_id: str) -> dict[str, Any]:
    config_path = resolve(args.config)
    config = load_yaml(config_path)
    ur = config["ur10e_mujoco"]
    model_path = resolve(ur["mjcf_path"])
    model = load_model(model_path)
    base_z_offset = 0.0
    if args.apply_calibrated_base_z_offset:
        base_z_offset = float(ur["contact"]["calibrated_bend_0p10_base_z_offset_m_for_5N"])
        apply_base_z_offset(model, base_z_offset)
    data = make_data(model)
    initial_q = parse_vector(args.initial_q, length=model.nq, name="initial_q")
    target_offset_m = parse_vector(args.target_offset_m, length=3, name="target_offset_m")
    target_rot_offset = parse_vector(args.target_rot_offset_rad, length=3, name="target_rot_offset_rad")
    dt_s = float(args.dt_s if args.dt_s is not None else ur["timestep_s"])
    duration_s = float(args.duration_s)
    if args.smoke:
        duration_s = min(duration_s, 0.4)

    set_qpos(model, data, initial_q)
    initial_tcp = site_position(model, data, args.site_name)
    initial_rotation = site_rotation_matrix(model, data, args.site_name)
    target_tcp = initial_tcp + target_offset_m
    target_rotation = rotation_matrix_from_rotvec(target_rot_offset) @ initial_rotation

    result = run_ik_rnn_frontier(
        model,
        data,
        site_name=args.site_name,
        initial_q=initial_q,
        target_tcp_m=target_tcp,
        target_rotation=target_rotation,
        duration_s=duration_s,
        dt_s=dt_s,
        r=float(args.r),
        linear_gain=float(args.linear_gain),
        angular_gain=float(args.angular_gain),
        max_linear_speed_m_s=float(args.max_linear_speed_m_s),
        max_angular_speed_rad_s=float(args.max_angular_speed_rad_s),
        qdot_limit_rad_s=float(args.qdot_limit_rad_s),
        linear_slack_axis_weights=np.asarray(args.linear_slack_axis_weights, dtype=float),
        angular_slack_axis_weights=np.asarray(args.angular_slack_axis_weights, dtype=float),
        angular_priority_mode=args.angular_priority_mode,
        slack_constraint_weight=float(args.slack_constraint_weight),
        damping=float(args.damping),
    )
    arrays = result.arrays()
    np.savez(out_dir / "ik-rnn-frontier_raw.npz", **arrays)
    plots = save_plots(out_dir, run_id, arrays)
    metrics = result.metrics()
    qdot_ok = (
        metrics["hidden_qdot_clip_count"] == 0
        and metrics["max_abs_qdot_rad_s"] <= float(args.qdot_limit_rad_s) + 1e-9
    )
    payload = {
        "run_source": "offline constrained finite-time IK/RNN frontier",
        "audit_run_id": run_id,
        "source_files": {
            "config": rel(config_path),
            "mjcf": rel(model_path),
            "module": "src/tase_repro/ik_rnn.py",
            "script": "scripts/run_ik_rnn_offline_frontier.py",
        },
        "inputs": {
            "site_name": args.site_name,
            "initial_q": [float(x) for x in initial_q],
            "initial_tcp_m": [float(x) for x in initial_tcp],
            "target_offset_m": [float(x) for x in target_offset_m],
            "target_rot_offset_rad": [float(x) for x in target_rot_offset],
            "applied_base_z_offset_m": float(base_z_offset),
            "linear_slack_axis_weights": [float(x) for x in args.linear_slack_axis_weights],
            "angular_slack_axis_weights": [float(x) for x in args.angular_slack_axis_weights],
            "angular_priority_mode": args.angular_priority_mode,
        },
        "summary": {
            "audit_passed": bool(
                metrics["final_position_error_m"] < metrics["initial_position_error_m"]
                and metrics["final_orientation_error_rad"] < metrics["initial_orientation_error_rad"]
                and metrics["solver_success_fraction"] >= 0.999
                and qdot_ok
                and metrics["max_joint_limit_violation_rad"] <= 1e-12
            ),
            "position_error_reduced": bool(metrics["final_position_error_m"] < metrics["initial_position_error_m"]),
            "orientation_error_reduced": bool(
                metrics["final_orientation_error_rad"] < metrics["initial_orientation_error_rad"]
            ),
            "qdot_bounds_respected": bool(qdot_ok),
            "joint_bounds_respected": bool(metrics["max_joint_limit_violation_rad"] <= 1e-12),
            "solver_success_fraction": metrics["solver_success_fraction"],
            "initial_position_error_mm": metrics["initial_position_error_m"] * 1000.0,
            "final_position_error_mm": metrics["final_position_error_m"] * 1000.0,
            "position_error_reduction_mm": metrics["position_error_reduction_m"] * 1000.0,
            "initial_orientation_error_deg": metrics["initial_orientation_error_rad"] * 180.0 / np.pi,
            "final_orientation_error_deg": metrics["final_orientation_error_rad"] * 180.0 / np.pi,
            "orientation_error_reduction_deg": metrics["orientation_error_reduction_rad"] * 180.0 / np.pi,
            "max_abs_qdot_rad_s": metrics["max_abs_qdot_rad_s"],
            "qdot_limit_rad_s": metrics["qdot_limit_rad_s"],
            "max_qdot_utilization": metrics["max_qdot_utilization"],
            "qdot_saturation_fraction_98pct": metrics["qdot_saturation_fraction_98pct"],
            "completion_claim_allowed": False,
            "do_not_mark_goal_complete": True,
        },
        "metrics": metrics,
        "plots": plots,
        "raw_artifact": rel(out_dir / "ik-rnn-frontier_raw.npz"),
        "claim_boundary": build_claim_boundary(),
        "next_actions": [
            "Use this as the first offline inner-loop IK/RNN frontier artifact while the large platform is unavailable.",
            "Keep Step6 outer-loop parameter tuning parked unless a new hardware or report question requires it.",
            "Do not treat this run as resolving the V151 contact-force coverage gap.",
        ],
    }
    payload["output_dir"] = rel(out_dir)
    return payload


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    plots = payload["plots"]
    lines = [
        "# IK/RNN Offline Frontier Summary",
        "",
        f"Run root: `{payload['output_dir']}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Position error: `{summary['initial_position_error_mm']:.6f}` mm -> `{summary['final_position_error_mm']:.6f}` mm",
        f"- Orientation error: `{summary['initial_orientation_error_deg']:.6f}` deg -> `{summary['final_orientation_error_deg']:.6f}` deg",
        f"- Solver success fraction: `{summary['solver_success_fraction']}`",
        f"- Max |qdot|: `{summary['max_abs_qdot_rad_s']}` rad/s under `{summary['qdot_limit_rad_s']}` rad/s",
        f"- Completion claim allowed: `{summary['completion_claim_allowed']}`",
        "",
        "Figures:",
        "",
        f"- Position error: `{plots['position_error']}`",
        f"- Orientation error: `{plots['orientation_error']}`",
        f"- qdot utilization: `{plots['qdot_utilization']}`",
        "",
        "Interpretation:",
        "",
        "- This is an offline constrained IK/RNN inner-loop frontier, not a live robot run.",
        "- The run verifies the simple finite-time velocity law can reduce a small TCP pose error while respecting the selected qdot envelope.",
        "- It does not resolve contact-force modeling, strict paper-equivalent feasibility, robustness, or hardware readiness.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--site-name", default=DEFAULT_SITE)
    parser.add_argument("--initial-q", default=DEFAULT_INITIAL_Q)
    parser.add_argument("--target-offset-m", default=DEFAULT_TARGET_OFFSET_M)
    parser.add_argument("--target-rot-offset-rad", default=DEFAULT_TARGET_ROT_OFFSET_RAD)
    parser.add_argument("--duration-s", type=float, default=2.0)
    parser.add_argument("--dt-s", type=float, default=None)
    parser.add_argument("--r", type=float, default=0.5)
    parser.add_argument("--linear-gain", type=float, default=0.05)
    parser.add_argument("--angular-gain", type=float, default=0.08)
    parser.add_argument("--max-linear-speed-m-s", type=float, default=0.015)
    parser.add_argument("--max-angular-speed-rad-s", type=float, default=0.08)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--linear-slack-axis-weights", type=float, nargs=3, default=[1.0, 1.0, 2.0])
    parser.add_argument("--angular-slack-axis-weights", type=float, nargs=3, default=[1.0, 1.0, 1.0])
    parser.add_argument("--angular-priority-mode", default="linear_primary")
    parser.add_argument("--slack-constraint-weight", type=float, default=1e3)
    parser.add_argument("--damping", type=float, default=1e-6)
    parser.add_argument("--apply-calibrated-base-z-offset", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = pathlib.Path(args.output_dir) if args.output_dir else ROOT / "runs" / "ik_rnn_offline_frontier" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    command = ["python3", "scripts/run_ik_rnn_offline_frontier.py", "--run-id", run_id]
    if args.smoke:
        command.append("--smoke")
    payload = build_payload(args, out_dir=out_dir, run_id=run_id)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=command)
    print(json.dumps(payload["summary"], indent=2))
    return 0 if payload["summary"]["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
