#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from audit_positive_stitched_sensitivity import summarize_case
from audit_stage_a_base_z_recovery import run_child, write_git_state
from evaluate_stitched_stage_a_handoff import read_path_csv
from tase_repro.base_z_recovery import base_z_delta_label


TRAJECTORY_ORDER = ["e1-cycloid", "e2-figure-eight", "e3-circle", "e4-cardioid"]

DEFAULT_SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "linear_kp0",
        "orientation_priority_mode": "linear_primary",
        "orientation_kp": 0.0,
        "normal_axis_weight": 1.0,
        "description": "v72/v77-style linear-primary baseline with no Stage B orientation feedback.",
    },
    {
        "name": "linear_kp0p003",
        "orientation_priority_mode": "linear_primary",
        "orientation_kp": 0.003,
        "normal_axis_weight": 1.0,
        "description": "linear-primary orientation feedback that corrects orientation but saturates qdot in v78.",
    },
    {
        "name": "linear_kp0p003_posture0p001",
        "orientation_priority_mode": "linear_primary",
        "orientation_kp": 0.003,
        "normal_axis_weight": 1.0,
        "joint_posture_weight": 0.001,
        "description": "linear-primary orientation feedback plus handoff-posture regularization.",
    },
    {
        "name": "planar_normal10_kp0p001",
        "orientation_priority_mode": "planar_primary",
        "orientation_kp": 0.001,
        "normal_axis_weight": 10.0,
        "description": "planar-primary probe with too little normal-force secondary weighting.",
    },
    {
        "name": "planar_normal30_kp0p001",
        "orientation_priority_mode": "planar_primary",
        "orientation_kp": 0.001,
        "normal_axis_weight": 30.0,
        "description": "planar-primary candidate that balanced orientation, qdot, and force in quick E2 probing.",
    },
    {
        "name": "planar_normal30_kp0p002",
        "orientation_priority_mode": "planar_primary",
        "orientation_kp": 0.002,
        "normal_axis_weight": 30.0,
        "description": "slightly stronger planar-primary candidate.",
    },
    {
        "name": "planar_normal100_kp0p001",
        "orientation_priority_mode": "planar_primary",
        "orientation_kp": 0.001,
        "normal_axis_weight": 100.0,
        "description": "planar-primary probe with high normal weighting that moves back toward the orientation boundary.",
    },
]


def value_label(prefix: str, value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".").replace(".", "p")
    return f"{prefix}_{text}"


def write_stage_a_config(
    *,
    out_dir: pathlib.Path,
    source_config: pathlib.Path,
    orientation_gate_rad: float,
) -> pathlib.Path:
    config = yaml.safe_load(source_config.read_text(encoding="utf-8"))
    target = config["selected_stage_a_target"]
    target["diagnostic_gate"]["max_terminal_orientation_error_rad"] = float(orientation_gate_rad)
    config["v79_stage_b_priority_recovery_scope"] = {
        "source_config": str(source_config),
        "max_terminal_orientation_error_rad": float(orientation_gate_rad),
        "claim_scope": "run-local Stage A orientation gate for Stage B priority-formulation probe only",
    }
    if "v70_relaxed_orientation_scope" in config:
        config["v70_relaxed_orientation_scope"]["max_terminal_orientation_error_rad"] = float(
            orientation_gate_rad
        )

    config_dir = out_dir / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    gate_config = config_dir / (
        f"{value_label('orientation_gate', orientation_gate_rad)}_stage_a_target_config.yaml"
    )
    with gate_config.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)
    return gate_config


def source_path_csv(source_run: pathlib.Path, delta_m: float) -> pathlib.Path:
    return source_run / "cases" / base_z_delta_label(delta_m) / "path" / "path.csv"


def handoff_posture_text(source_run: pathlib.Path, delta_m: float) -> str:
    q_path = read_path_csv(source_path_csv(source_run, delta_m))
    return ",".join(f"{float(value):.17g}" for value in q_path[-1])


def stitched_command(
    *,
    out_dir: pathlib.Path,
    source_run: pathlib.Path,
    stage_a_target_config: pathlib.Path,
    delta_m: float,
    stage_a_duration_s: float,
    paper_time_scale: float,
    qdot_limit_rad_s: float,
    max_orientation_error_rad: float,
    scenario: dict[str, Any],
    posture_target_q: str,
) -> list[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "evaluate_stitched_stage_a_handoff.py"),
        "--output-dir",
        str(out_dir),
        "--stage-a-target-config",
        str(stage_a_target_config),
        "--source-path-csv",
        str(source_path_csv(source_run, delta_m)),
        "--base-z-offset-delta-m",
        f"{float(delta_m):.17g}",
        "--stage-a-duration-s",
        f"{float(stage_a_duration_s):.17g}",
        "--paper-time-scale",
        f"{float(paper_time_scale):.17g}",
        "--qdot-limit-rad-s",
        f"{float(qdot_limit_rad_s):.17g}",
        "--max-orientation-error-rad",
        f"{float(max_orientation_error_rad):.17g}",
        "--orientation-priority-mode",
        str(scenario["orientation_priority_mode"]),
        "--orientation-kp",
        f"{float(scenario['orientation_kp']):.17g}",
        "--normal-axis-weight",
        f"{float(scenario['normal_axis_weight']):.17g}",
    ]
    posture_weight = float(scenario.get("joint_posture_weight", 0.0))
    if posture_weight > 0.0:
        command.extend(
            [
                "--joint-posture-target-q",
                posture_target_q,
                "--joint-posture-kp",
                f"{float(scenario.get('joint_posture_kp', 1.0)):.17g}",
                "--joint-posture-weight",
                f"{posture_weight:.17g}",
                "--max-joint-posture-velocity-rad-s",
                f"{float(scenario.get('max_joint_posture_velocity_rad_s', 0.05)):.17g}",
            ]
        )
    return command


def stage_b_rows(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in metrics["stage_b"]["rows"]:
        target = row["target_pair_metrics"]
        gate = row["feasibility_gate"]
        rows.append(
            {
                "trajectory": row["trajectory"],
                "passed": bool(gate["feasibility_pass"]),
                "failed_criteria": gate["failed_criteria"],
                "orientation_error_rad": float(target["max_orientation_error_rad"]),
                "qdot_saturation_fraction": float(target["qdot_saturation_fraction"]),
                "tail_max_qdot_utilization": float(target["tail_max_qdot_utilization"]),
                "tail_mean_abs_force_error_N": float(target["tail_mean_abs_force_error_N"]),
                "max_tangential_position_error_m": float(target["max_tangential_position_error_m"]),
                "max_abs_normal_velocity_slack_m_s": float(target["max_abs_normal_velocity_slack_m_s"]),
                "max_angular_velocity_slack_rad_s": float(target["max_angular_velocity_slack_rad_s"]),
            }
        )
    return rows


def aggregate_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    passing = [case for case in cases if case["stitched_passed"]]
    return {
        "scenario_count": len(cases),
        "stitched_pass_count": len(passing),
        "stitched_fail_count": len(cases) - len(passing),
        "passing_scenarios": [case["scenario"] for case in passing],
        "stage_a_all_passed": all(case["stage_a_passed"] for case in cases),
        "max_stage_b_orientation_error_rad": max(case["stage_b_max_orientation_error_rad"] for case in cases),
        "min_stage_b_orientation_error_rad": min(case["stage_b_max_orientation_error_rad"] for case in cases),
        "max_stage_b_qdot_saturation_fraction": max(
            case["stage_b_max_qdot_saturation_fraction"] for case in cases
        ),
        "min_stage_b_qdot_saturation_fraction": min(
            case["stage_b_max_qdot_saturation_fraction"] for case in cases
        ),
        "max_stage_b_tail_force_error_N": max(case["stage_b_max_tail_force_error_N"] for case in cases),
        "min_stage_b_tail_force_error_N": min(case["stage_b_max_tail_force_error_N"] for case in cases),
    }


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    lines = [
        "# Stage B Priority Recovery Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Scenario count: `{aggregate['scenario_count']}`",
        f"- Stitched pass count: `{aggregate['stitched_pass_count']} / {aggregate['scenario_count']}`",
        f"- Passing scenarios: `{', '.join(aggregate['passing_scenarios']) or 'none'}`",
        f"- Stage A passed every scenario: `{aggregate['stage_a_all_passed']}`",
        "",
        "| scenario | priority | normal weight | orientation_kp | posture weight | stitched | Stage B pass | max orientation | max qdot sat | max tail qdot | max force err | failed rows |",
        "| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for case in cases:
        failed_rows = [
            f"{row['trajectory']}:{','.join(row['failed_criteria'])}"
            for row in case["stage_b_rows"]
            if row["failed_criteria"]
        ]
        lines.append(
            "| `{scenario}` | `{priority}` | `{normal}` | `{kp}` | `{posture}` | `{stitched}` | `{handoff}/{count}` | `{orientation}` | `{qdot}` | `{tail_qdot}` | `{force}` | `{failed}` |".format(
                scenario=case["scenario"],
                priority=case["orientation_priority_mode"],
                normal=case["normal_axis_weight"],
                kp=case["orientation_kp"],
                posture=case["joint_posture_weight"],
                stitched=case["stitched_passed"],
                handoff=case["handoff_pass_count"],
                count=case["handoff_trajectory_count"],
                orientation=case["stage_b_max_orientation_error_rad"],
                qdot=case["stage_b_max_qdot_saturation_fraction"],
                tail_qdot=case["stage_b_max_tail_qdot_utilization"],
                force=case["stage_b_max_tail_force_error_N"],
                failed="; ".join(failed_rows) or "none",
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- Linear-primary orientation feedback still trades orientation correction against qdot saturation, and handoff-posture regularization preserves qdot by giving up the orientation correction.",
            "- Planar-primary priority with too little normal secondary weighting gives up force tracking.",
            "- Planar-primary priority with normal-axis weight `30` recovers the full E1-E4 `+1.0 mm` tightened-gate diagnostic row at the tested `0.11995 rad` gate.",
            "- This is a targeted priority-formulation recovery, not a robustness proof or hardware-ready claim.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-run",
        default="runs/positive_relaxed_orientation_recovery/20260524T172909",
    )
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--base-z-delta-mm", type=float, default=1.0)
    parser.add_argument("--stage-a-duration-s", type=float, default=15.0)
    parser.add_argument("--paper-time-scale", type=float, default=0.005)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--orientation-gate-rad", type=float, default=0.11995)
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    source_config = source_run / "relaxed_stage_a_target_config.yaml"
    delta_m = float(args.base_z_delta_mm) / 1000.0
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "stage_b_priority_recovery" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    stage_a_target_config = write_stage_a_config(
        out_dir=out_dir,
        source_config=source_config,
        orientation_gate_rad=args.orientation_gate_rad,
    )
    posture_target_q = handoff_posture_text(source_run, delta_m)

    cases = []
    for scenario in DEFAULT_SCENARIOS:
        scenario_name = str(scenario["name"])
        case_dir = out_dir / "scenarios" / scenario_name
        case_dir.mkdir(parents=True, exist_ok=True)
        metrics = run_child(
            stitched_command(
                out_dir=case_dir,
                source_run=source_run,
                stage_a_target_config=stage_a_target_config,
                delta_m=delta_m,
                stage_a_duration_s=args.stage_a_duration_s,
                paper_time_scale=args.paper_time_scale,
                qdot_limit_rad_s=args.qdot_limit_rad_s,
                max_orientation_error_rad=args.orientation_gate_rad,
                scenario=scenario,
                posture_target_q=posture_target_q,
            ),
            out_dir=case_dir,
        )
        case = summarize_case(delta_m, metrics)
        rows = stage_b_rows(metrics)
        case.update(
            {
                "scenario": scenario_name,
                "description": str(scenario["description"]),
                "orientation_priority_mode": str(scenario["orientation_priority_mode"]),
                "orientation_kp": float(scenario["orientation_kp"]),
                "normal_axis_weight": float(scenario["normal_axis_weight"]),
                "joint_posture_weight": float(scenario.get("joint_posture_weight", 0.0)),
                "stage_a_target_config": str(stage_a_target_config),
                "stage_b_rows": rows,
                "stage_b_max_orientation_error_rad": max(row["orientation_error_rad"] for row in rows),
                "stage_b_max_qdot_saturation_fraction": max(
                    row["qdot_saturation_fraction"] for row in rows
                ),
                "stage_b_max_tail_qdot_utilization": max(row["tail_max_qdot_utilization"] for row in rows),
                "stage_b_max_tail_force_error_N": max(row["tail_mean_abs_force_error_N"] for row in rows),
            }
        )
        cases.append(case)

    aggregate = aggregate_cases(cases)
    payload = {
        "run_id": run_id,
        "source": "v79 focused Stage B priority-formulation recovery audit for the +1.0 mm tightened-orientation boundary",
        "source_run": str(source_run),
        "source_stage_a_target_config": str(source_config),
        "stage_a_target_config": str(stage_a_target_config),
        "base_z_offset_delta_m": delta_m,
        "base_z_offset_delta_mm": float(args.base_z_delta_mm),
        "stage_a_duration_s": float(args.stage_a_duration_s),
        "paper_time_scale": float(args.paper_time_scale),
        "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
        "orientation_gate_rad": float(args.orientation_gate_rad),
        "trajectories": TRAJECTORY_ORDER,
        "scenarios": DEFAULT_SCENARIOS,
        "aggregate": aggregate,
        "cases": cases,
        "warnings": [
            "diagnostic-label Stage B priority-formulation recovery audit only",
            "uses run-local copied Stage A target config",
            "not a canonical config change",
            "not strict paper-equivalent feasibility",
            "not a formal robustness proof",
            "not contact-model calibration",
            "not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    write_summary(out_dir, aggregate, cases)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
