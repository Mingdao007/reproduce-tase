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

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.feasibility import FeasibilityThresholds, evaluate_force_motion_feasibility


DEFAULT_TRAJECTORIES = ("e2-figure-eight", "e3-circle")
DEFAULT_TIME_SCALES = (1.0, 0.75, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1)
SUMMARY_FIELDS = (
    "trajectory",
    "paper_time_scale",
    "feasibility_pass",
    "failed_criteria",
    "tail_mean_abs_force_error_N",
    "contact_present_fraction",
    "max_tangential_position_error_m",
    "max_planar_velocity_slack_m_s",
    "max_abs_normal_velocity_slack_m_s",
    "max_abs_qdot_rad_s",
    "max_qdot_utilization",
    "tail_max_qdot_utilization",
    "qdot_saturation_fraction",
    "tail_qdot_saturation_fraction",
    "max_qdot_violation_rad_s",
    "max_joint_limit_violation_rad",
    "case_dir",
)


def parse_csv_floats(text: str) -> list[float]:
    return [float(part.strip()) for part in text.split(",") if part.strip()]


def parse_csv_strings(text: str) -> list[str]:
    return [part.strip() for part in text.split(",") if part.strip()]


def scale_label(scale: float) -> str:
    return f"{scale:.6g}".replace("-", "m").replace(".", "p")


def short_trajectory_name(name: str) -> str:
    return name.split("-", maxsplit=1)[0]


def display_path(path: pathlib.Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def run_case(args: argparse.Namespace, *, trajectory: str, time_scale: float, out_dir: pathlib.Path) -> dict[str, Any]:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_paper_trajectory_force_motion.py"),
        "--config",
        args.config,
        "--output-dir",
        str(out_dir),
        "--duration-s",
        str(args.duration_s),
        "--target-force-N",
        str(args.target_force_N),
        "--force-gain",
        str(args.force_gain),
        "--r",
        str(args.r),
        f"--base-z-offset-m={args.base_z_offset_m}",
        "--initial-q",
        args.initial_q,
        "--qdot-limit-rad-s",
        str(args.qdot_limit_rad_s),
        "--trajectory",
        trajectory,
        "--omega-rad-s",
        str(args.omega_rad_s),
        "--paper-time-scale",
        str(time_scale),
        "--planar-kp",
        str(args.planar_kp),
        "--use-slack-solve",
        "--planar-slack-weight",
        str(args.planar_slack_weight),
        "--normal-slack-weight",
        str(args.normal_slack_weight),
        "--slack-constraint-weight",
        str(args.slack_constraint_weight),
    ]
    subprocess.run(command, check=True, cwd=ROOT)
    with (out_dir / "metrics.yaml").open("r", encoding="utf-8") as f:
        metrics = yaml.safe_load(f)
    gate = evaluate_force_motion_feasibility(
        metrics,
        thresholds=FeasibilityThresholds(),
        qdot_abs_limit_rad_s=args.qdot_limit_rad_s,
    )
    return {
        "metrics": metrics,
        "gate": gate,
        "command": command,
    }


def build_summary_row(case: dict[str, Any], *, case_dir: pathlib.Path) -> dict[str, Any]:
    metrics = case["metrics"]
    gate = case["gate"]
    return {
        "trajectory": metrics["trajectory"],
        "paper_time_scale": metrics["paper_time_scale"],
        "feasibility_pass": gate["feasibility_pass"],
        "failed_criteria": ";".join(gate["failed_criteria"]),
        "tail_mean_abs_force_error_N": metrics["tail_mean_abs_force_error_N"],
        "contact_present_fraction": metrics["contact_present_fraction"],
        "max_tangential_position_error_m": metrics["max_tangential_position_error_m"],
        "max_planar_velocity_slack_m_s": metrics["max_planar_velocity_slack_m_s"],
        "max_abs_normal_velocity_slack_m_s": metrics["max_abs_normal_velocity_slack_m_s"],
        "max_abs_qdot_rad_s": metrics["max_abs_qdot_rad_s"],
        "max_qdot_utilization": metrics["max_qdot_utilization"],
        "tail_max_qdot_utilization": metrics["tail_max_qdot_utilization"],
        "qdot_saturation_fraction": metrics["qdot_saturation_fraction"],
        "tail_qdot_saturation_fraction": metrics["tail_qdot_saturation_fraction"],
        "max_qdot_violation_rad_s": metrics["max_qdot_violation_rad_s"],
        "max_joint_limit_violation_rad": metrics["max_joint_limit_violation_rad"],
        "case_dir": display_path(case_dir),
    }


def fastest_passing_scales(rows: list[dict[str, Any]]) -> dict[str, float | None]:
    result: dict[str, float | None] = {}
    for row in rows:
        trajectory = str(row["trajectory"])
        if trajectory not in result:
            result[trajectory] = None
        if bool(row["feasibility_pass"]):
            scale = float(row["paper_time_scale"])
            result[trajectory] = scale if result[trajectory] is None else max(result[trajectory], scale)
    return result


def write_summary_markdown(
    output_path: pathlib.Path,
    *,
    run_root: pathlib.Path,
    rows: list[dict[str, Any]],
    thresholds: FeasibilityThresholds,
) -> None:
    fastest = fastest_passing_scales(rows)
    lines = [
        "# Timing Feasibility Sweep Summary",
        "",
        f"Run root: `{display_path(run_root)}`",
        "",
        "## Gates",
        "",
    ]
    for key, value in thresholds.to_dict().items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Fastest Passing Scale", ""])
    for trajectory, scale in fastest.items():
        text = "none" if scale is None else f"`{scale}`"
        lines.append(f"- `{trajectory}`: {text}")
    lines.extend(
        [
            "",
            "## Cases",
            "",
            "| trajectory | scale | pass | failed criteria | force error N | contact | max pos err m | max planar slack m/s | max normal slack m/s | qdot sat frac | tail qdot util |",
            "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            "| {trajectory} | `{scale}` | `{passed}` | `{failed}` | `{force}` | `{contact}` | `{pos}` | `{planar_slack}` | `{normal_slack}` | `{qdot_sat}` | `{tail_qdot_util}` |".format(
                trajectory=row["trajectory"],
                scale=row["paper_time_scale"],
                passed=row["feasibility_pass"],
                failed=row["failed_criteria"] or "none",
                force=row["tail_mean_abs_force_error_N"],
                contact=row["contact_present_fraction"],
                pos=row["max_tangential_position_error_m"],
                planar_slack=row["max_planar_velocity_slack_m_s"],
                normal_slack=row["max_abs_normal_velocity_slack_m_s"],
                qdot_sat=row["qdot_saturation_fraction"],
                tail_qdot_util=row["tail_max_qdot_utilization"],
            )
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_git_state(run_root: pathlib.Path, *, args: argparse.Namespace) -> None:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
    dirty = status if status else "clean"
    trajectory_text = ", ".join(parse_csv_strings(args.trajectories))
    content = "\n".join(
        [
            "# Git State",
            "",
            f"- Run root: `{display_path(run_root)}`",
            f"- Branch: `{branch}`",
            f"- Starting commit: `{commit}`",
            f"- Dirty state: `{dirty}`",
            "- Scope:",
            f"  Force-motion feasibility sweep for `{trajectory_text}` with time scales `{args.time_scales}`.",
            "- Note:",
            "  Raw `.npz` files are ignored by repo policy. Metrics, plots, and aggregate summaries are tracked.",
            "",
        ]
    )
    (run_root / "git_state.md").write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--trajectories", default=",".join(DEFAULT_TRAJECTORIES))
    parser.add_argument("--time-scales", default=",".join(str(x) for x in DEFAULT_TIME_SCALES))
    parser.add_argument("--duration-s", type=float, default=8.0)
    parser.add_argument("--target-force-N", type=float, default=5.0)
    parser.add_argument("--force-gain", type=float, default=5e-4)
    parser.add_argument("--r", type=float, default=0.5)
    parser.add_argument("--base-z-offset-m", type=float, default=-4e-5)
    parser.add_argument("--initial-q", default="0,-0.02,0.03,-0.01,0,0")
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--omega-rad-s", type=float, default=0.1)
    parser.add_argument("--planar-kp", type=float, default=0.5)
    parser.add_argument("--planar-slack-weight", type=float, default=1.0)
    parser.add_argument("--normal-slack-weight", type=float, default=10000.0)
    parser.add_argument("--slack-constraint-weight", type=float, default=1000.0)
    args = parser.parse_args()

    trajectories = parse_csv_strings(args.trajectories)
    time_scales = parse_csv_floats(args.time_scales)
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    run_root = (
        pathlib.Path(args.output_dir).resolve()
        if args.output_dir
        else ROOT / "runs" / "timing_feasibility_sweep" / run_id
    )
    run_root.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    cases: list[dict[str, Any]] = []
    for trajectory in trajectories:
        for time_scale in time_scales:
            case_dir = run_root / f"{short_trajectory_name(trajectory)}_scale-{scale_label(time_scale)}"
            case_dir.mkdir(parents=True, exist_ok=True)
            case = run_case(args, trajectory=trajectory, time_scale=time_scale, out_dir=case_dir)
            row = build_summary_row(case, case_dir=case_dir)
            cases.append(
                {
                    "trajectory": trajectory,
                    "paper_time_scale": time_scale,
                    "case_dir": display_path(case_dir),
                    "metrics": case["metrics"],
                    "gate": case["gate"],
                    "command": case["command"],
                }
            )
            rows.append(row)

    thresholds = FeasibilityThresholds()
    with (run_root / "summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "run_id": run_id,
        "run_root": display_path(run_root),
        "thresholds": thresholds.to_dict(),
        "fastest_passing_scale_by_trajectory": fastest_passing_scales(rows),
        "rows": rows,
        "cases": cases,
    }
    with (run_root / "summary.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(summary, f, sort_keys=False, allow_unicode=True)
    with (run_root / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    write_summary_markdown(run_root / "summary.md", run_root=run_root, rows=rows, thresholds=thresholds)
    write_git_state(run_root, args=args)

    print(run_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
