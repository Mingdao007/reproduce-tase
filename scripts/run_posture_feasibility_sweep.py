#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import pathlib
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.contact_ladder import calibrate_base_z_for_initial_q_target_force
from tase_repro.feasibility import FeasibilityThresholds, evaluate_force_motion_feasibility


DEFAULT_POSTURES = (
    "baseline:0,-0.02,0.03,-0.01,0,0",
    "bend_0p03:0,-0.03,0.05,-0.02,0,0",
    "bend_0p05:0,-0.05,0.08,-0.03,0,0",
    "bend_0p075:0,-0.075,0.115,-0.04,0,0",
    "bend_0p10:0,-0.10,0.15,-0.05,0,0",
)
DEFAULT_TRAJECTORIES = ("e2-figure-eight", "e3-circle")
DEFAULT_TIME_SCALES = (1.0, 0.75, 0.6, 0.5, 0.35, 0.25, 0.2)
SUMMARY_FIELDS = (
    "posture",
    "initial_q",
    "calibrated_base_z_offset_m",
    "initial_force_N",
    "trajectory",
    "paper_time_scale",
    "feasibility_pass",
    "failed_criteria",
    "tail_mean_abs_force_error_N",
    "contact_present_fraction",
    "max_tangential_position_error_m",
    "max_planar_velocity_slack_m_s",
    "max_abs_normal_velocity_slack_m_s",
    "max_orientation_error_rad",
    "max_angular_velocity_slack_rad_s",
    "qdot_saturation_fraction",
    "tail_max_qdot_utilization",
    "case_dir",
)


@dataclass(frozen=True)
class Posture:
    name: str
    q: list[float]

    @property
    def q_text(self) -> str:
        return ",".join(f"{value:.12g}" for value in self.q)


def parse_csv_floats(text: str) -> list[float]:
    return [float(part.strip()) for part in text.split(",") if part.strip()]


def parse_csv_strings(text: str) -> list[str]:
    return [part.strip() for part in text.split(",") if part.strip()]


def parse_postures(text: str) -> list[Posture]:
    postures = []
    for spec in text.split(";"):
        spec = spec.strip()
        if not spec:
            continue
        if ":" not in spec:
            raise ValueError(f"posture spec must be name:q1,...,q6, got {spec!r}")
        name, values = spec.split(":", maxsplit=1)
        q = parse_csv_floats(values)
        if len(q) != 6:
            raise ValueError(f"posture {name!r} must have 6 joints, got {len(q)}")
        postures.append(Posture(name=name.strip(), q=q))
    if not postures:
        raise ValueError("at least one posture is required")
    return postures


def scale_label(scale: float) -> str:
    return f"{scale:.6g}".replace("-", "m").replace(".", "p")


def display_path(path: pathlib.Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def short_trajectory_name(name: str) -> str:
    return name.split("-", maxsplit=1)[0]


def run_case(
    args: argparse.Namespace,
    *,
    posture: Posture,
    base_z_offset_m: float,
    trajectory: str,
    time_scale: float,
    out_dir: pathlib.Path,
) -> dict[str, Any]:
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
        f"--base-z-offset-m={base_z_offset_m}",
        "--initial-q",
        posture.q_text,
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
        "--normal-velocity-mode",
        args.normal_velocity_mode,
        "--orientation-mode",
        args.orientation_mode,
        "--orientation-priority-mode",
        args.orientation_priority_mode,
        "--orientation-kp",
        str(args.orientation_kp),
        "--angular-axis-weight",
        str(args.angular_axis_weight),
        "--angular-slack-weight",
        str(args.angular_slack_weight),
    ]
    subprocess.run(command, check=True, cwd=ROOT)
    with (out_dir / "metrics.yaml").open("r", encoding="utf-8") as f:
        metrics = yaml.safe_load(f)
    gate = evaluate_force_motion_feasibility(
        metrics,
        thresholds=build_thresholds(args),
        qdot_abs_limit_rad_s=args.qdot_limit_rad_s,
    )
    return {
        "metrics": metrics,
        "gate": gate,
        "command": command,
    }


def build_thresholds(args: argparse.Namespace) -> FeasibilityThresholds:
    return FeasibilityThresholds(
        max_orientation_error_rad_max=args.max_orientation_error_rad,
        max_angular_velocity_slack_rad_s_max=args.max_angular_slack_rad_s,
    )


def build_summary_row(
    case: dict[str, Any],
    *,
    posture: Posture,
    calibrated_base_z_offset_m: float,
    initial_force_N: float,
    case_dir: pathlib.Path,
) -> dict[str, Any]:
    metrics = case["metrics"]
    gate = case["gate"]
    return {
        "posture": posture.name,
        "initial_q": posture.q_text,
        "calibrated_base_z_offset_m": calibrated_base_z_offset_m,
        "initial_force_N": initial_force_N,
        "trajectory": metrics["trajectory"],
        "paper_time_scale": metrics["paper_time_scale"],
        "feasibility_pass": gate["feasibility_pass"],
        "failed_criteria": ";".join(gate["failed_criteria"]),
        "tail_mean_abs_force_error_N": metrics["tail_mean_abs_force_error_N"],
        "contact_present_fraction": metrics["contact_present_fraction"],
        "max_tangential_position_error_m": metrics["max_tangential_position_error_m"],
        "max_planar_velocity_slack_m_s": metrics["max_planar_velocity_slack_m_s"],
        "max_abs_normal_velocity_slack_m_s": metrics["max_abs_normal_velocity_slack_m_s"],
        "max_orientation_error_rad": metrics["max_orientation_error_rad"],
        "max_angular_velocity_slack_rad_s": metrics["max_angular_velocity_slack_rad_s"],
        "qdot_saturation_fraction": metrics["qdot_saturation_fraction"],
        "tail_max_qdot_utilization": metrics["tail_max_qdot_utilization"],
        "case_dir": display_path(case_dir),
    }


def fastest_passing_scale(rows: list[dict[str, Any]]) -> dict[str, dict[str, float | None]]:
    result: dict[str, dict[str, float | None]] = {}
    for row in rows:
        posture = str(row["posture"])
        trajectory = str(row["trajectory"])
        result.setdefault(posture, {})
        result[posture].setdefault(trajectory, None)
        if bool(row["feasibility_pass"]):
            scale = float(row["paper_time_scale"])
            current = result[posture][trajectory]
            result[posture][trajectory] = scale if current is None else max(current, scale)
    return result


def fastest_joint_scale(rows: list[dict[str, Any]], trajectories: list[str]) -> dict[str, float | None]:
    by_trajectory = fastest_passing_scale(rows)
    result: dict[str, float | None] = {}
    for posture, values in by_trajectory.items():
        scales = [values.get(trajectory) for trajectory in trajectories]
        result[posture] = None if any(scale is None for scale in scales) else min(float(scale) for scale in scales)
    return result


def write_summary_markdown(
    output_path: pathlib.Path,
    *,
    run_root: pathlib.Path,
    rows: list[dict[str, Any]],
    posture_calibrations: list[dict[str, Any]],
    trajectories: list[str],
    thresholds: FeasibilityThresholds,
) -> None:
    joint = fastest_joint_scale(rows, trajectories)
    lines = [
        "# Posture Feasibility Sweep Summary",
        "",
        f"Run root: `{display_path(run_root)}`",
        "",
        "## Gates",
        "",
    ]
    for key, value in thresholds.to_dict().items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Fastest Scale Passing All Requested Trajectories", ""])
    for posture, scale in joint.items():
        text = "none" if scale is None else f"`{scale}`"
        lines.append(f"- `{posture}`: {text}")
    lines.extend(
        [
            "",
            "## Posture Calibration",
            "",
            "| posture | pass | base z offset m | initial force N | contact count | error |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for calibration in posture_calibrations:
        error = str(calibration.get("calibration_error") or "none").replace("\n", " ")
        lines.append(
            "| {posture} | `{passed}` | `{offset}` | `{force}` | `{contact_count}` | `{error}` |".format(
                posture=calibration["posture"],
                passed=calibration.get("calibration_pass"),
                offset=calibration.get("calibrated_base_z_offset_m"),
                force=calibration.get("initial_force_N"),
                contact_count=calibration.get("initial_contact_count"),
                error=error,
            )
        )
    lines.extend(
        [
            "",
            "## Cases",
            "",
            "| posture | trajectory | scale | pass | failed criteria | base z offset m | force error N | max pos err m | max planar slack m/s | max orient err rad | max angular slack rad/s | qdot sat frac | tail qdot util |",
            "| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            "| {posture} | {trajectory} | `{scale}` | `{passed}` | `{failed}` | `{offset}` | `{force}` | `{pos}` | `{planar_slack}` | `{orient}` | `{angular_slack}` | `{qdot_sat}` | `{tail_qdot}` |".format(
                posture=row["posture"],
                trajectory=row["trajectory"],
                scale=row["paper_time_scale"],
                passed=row["feasibility_pass"],
                failed=row["failed_criteria"] or "none",
                offset=row["calibrated_base_z_offset_m"],
                force=row["tail_mean_abs_force_error_N"],
                pos=row["max_tangential_position_error_m"],
                planar_slack=row["max_planar_velocity_slack_m_s"],
                orient=row["max_orientation_error_rad"],
                angular_slack=row["max_angular_velocity_slack_rad_s"],
                qdot_sat=row["qdot_saturation_fraction"],
                tail_qdot=row["tail_max_qdot_utilization"],
            )
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_git_state(run_root: pathlib.Path, *, args: argparse.Namespace) -> None:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
    dirty = status if status else "clean"
    content = "\n".join(
        [
            "# Git State",
            "",
            f"- Run root: `{display_path(run_root)}`",
            f"- Branch: `{branch}`",
            f"- Starting commit: `{commit}`",
            f"- Dirty state: `{dirty}`",
            "- Scope:",
            f"  Posture feasibility sweep for `{args.trajectories}` with time scales `{args.time_scales}`.",
            "- Orientation task:",
            f"  mode `{args.orientation_mode}`, priority `{args.orientation_priority_mode}`, kp `{args.orientation_kp}`, angular axis weight `{args.angular_axis_weight}`, angular slack weight `{args.angular_slack_weight}`.",
            "- Orientation gates:",
            f"  max orientation error `{args.max_orientation_error_rad}`, max angular slack `{args.max_angular_slack_rad_s}`.",
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
    parser.add_argument("--postures", default=";".join(DEFAULT_POSTURES))
    parser.add_argument("--trajectories", default=",".join(DEFAULT_TRAJECTORIES))
    parser.add_argument("--time-scales", default=",".join(str(x) for x in DEFAULT_TIME_SCALES))
    parser.add_argument("--duration-s", type=float, default=8.0)
    parser.add_argument("--target-force-N", type=float, default=5.0)
    parser.add_argument("--force-gain", type=float, default=5e-4)
    parser.add_argument("--r", type=float, default=0.5)
    parser.add_argument("--calibration-lower-offset-m", type=float, default=-0.01)
    parser.add_argument("--calibration-upper-offset-m", type=float, default=0.01)
    parser.add_argument("--calibration-tolerance-N", type=float, default=0.01)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--omega-rad-s", type=float, default=0.1)
    parser.add_argument("--planar-kp", type=float, default=0.5)
    parser.add_argument("--planar-slack-weight", type=float, default=1.0)
    parser.add_argument("--normal-slack-weight", type=float, default=10000.0)
    parser.add_argument("--slack-constraint-weight", type=float, default=1000.0)
    parser.add_argument("--normal-velocity-mode", choices=["world-z", "contact-normal"], default="world-z")
    parser.add_argument("--orientation-mode", choices=["none", "hold", "force-normal"], default="none")
    parser.add_argument("--orientation-priority-mode", choices=["weighted", "linear-primary"], default="weighted")
    parser.add_argument("--orientation-kp", type=float, default=1.0)
    parser.add_argument("--angular-axis-weight", type=float, default=1.0)
    parser.add_argument("--angular-slack-weight", type=float, default=1.0)
    parser.add_argument("--max-orientation-error-rad", type=float, default=None)
    parser.add_argument("--max-angular-slack-rad-s", type=float, default=None)
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()

    postures = parse_postures(args.postures)
    trajectories = parse_csv_strings(args.trajectories)
    time_scales = parse_csv_floats(args.time_scales)
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    run_root = (
        pathlib.Path(args.output_dir).resolve()
        if args.output_dir
        else ROOT / "runs" / "posture_feasibility_sweep" / run_id
    )
    run_root.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    cases: list[dict[str, Any]] = []
    posture_calibrations: list[dict[str, Any]] = []
    for posture in postures:
        try:
            calibration = calibrate_base_z_for_initial_q_target_force(
                model_path,
                initial_q=posture.q,
                target_force_N=args.target_force_N,
                lower_offset_m=args.calibration_lower_offset_m,
                upper_offset_m=args.calibration_upper_offset_m,
                tolerance_N=args.calibration_tolerance_N,
            )
        except ValueError as exc:
            posture_calibrations.append(
                {
                    "posture": posture.name,
                    "initial_q": posture.q,
                    "calibrated_base_z_offset_m": None,
                    "initial_force_N": None,
                    "initial_tcp_z_m": None,
                    "initial_contact_count": None,
                    "calibration_pass": False,
                    "calibration_error": str(exc),
                }
            )
            continue
        posture_calibrations.append(
            {
                "posture": posture.name,
                "initial_q": posture.q,
                "calibrated_base_z_offset_m": calibration.base_z_offset_m,
                "initial_force_N": calibration.normal_force_N,
                "initial_tcp_z_m": calibration.tcp_z_m,
                "initial_contact_count": calibration.contact_count,
                "calibration_pass": True,
                "calibration_error": None,
            }
        )
        for trajectory in trajectories:
            for time_scale in time_scales:
                case_dir = (
                    run_root
                    / posture.name
                    / f"{short_trajectory_name(trajectory)}_scale-{scale_label(time_scale)}"
                )
                case_dir.mkdir(parents=True, exist_ok=True)
                case = run_case(
                    args,
                    posture=posture,
                    base_z_offset_m=calibration.base_z_offset_m,
                    trajectory=trajectory,
                    time_scale=time_scale,
                    out_dir=case_dir,
                )
                row = build_summary_row(
                    case,
                    posture=posture,
                    calibrated_base_z_offset_m=calibration.base_z_offset_m,
                    initial_force_N=calibration.normal_force_N,
                    case_dir=case_dir,
                )
                cases.append(
                    {
                        "posture": posture.name,
                        "initial_q": posture.q,
                        "trajectory": trajectory,
                        "paper_time_scale": time_scale,
                        "case_dir": display_path(case_dir),
                        "metrics": case["metrics"],
                        "gate": case["gate"],
                        "command": case["command"],
                    }
                )
                rows.append(row)

    thresholds = build_thresholds(args)
    with (run_root / "summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "run_id": run_id,
        "run_root": display_path(run_root),
        "thresholds": thresholds.to_dict(),
        "posture_calibrations": posture_calibrations,
        "fastest_passing_scale_by_posture_and_trajectory": fastest_passing_scale(rows),
        "fastest_scale_passing_all_trajectories_by_posture": fastest_joint_scale(rows, trajectories),
        "rows": rows,
        "cases": cases,
    }
    with (run_root / "summary.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(summary, f, sort_keys=False, allow_unicode=True)
    with (run_root / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    write_summary_markdown(
        run_root / "summary.md",
        run_root=run_root,
        rows=rows,
        posture_calibrations=posture_calibrations,
        trajectories=trajectories,
        thresholds=thresholds,
    )
    write_git_state(run_root, args=args)

    print(run_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
