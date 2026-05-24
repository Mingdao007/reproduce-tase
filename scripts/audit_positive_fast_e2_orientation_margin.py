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
sys.path.insert(0, str(SCRIPT_DIR))

from audit_stage_a_base_z_recovery import run_child, write_git_state
from tase_repro.base_z_recovery import base_z_delta_label


SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "linear_kp0_normal1",
        "orientation_priority_mode": "linear_primary",
        "orientation_kp": 0.0,
        "normal_axis_weight": 1.0,
        "description": "v105 failing linear-primary E2 baseline.",
    },
    {
        "name": "linear_kp0p003_normal1",
        "orientation_priority_mode": "linear_primary",
        "orientation_kp": 0.003,
        "normal_axis_weight": 1.0,
        "description": "linear-primary feedback probe from v78/v79.",
    },
    {
        "name": "planar_normal30_kp0p001",
        "orientation_priority_mode": "planar_primary",
        "orientation_kp": 0.001,
        "normal_axis_weight": 30.0,
        "description": "v79 planar-primary lower-gain candidate.",
    },
    {
        "name": "planar_normal30_kp0p002",
        "orientation_priority_mode": "planar_primary",
        "orientation_kp": 0.002,
        "normal_axis_weight": 30.0,
        "description": "v79 planar-primary higher-gain candidate.",
    },
    {
        "name": "weighted_kp0_normal1",
        "orientation_priority_mode": "weighted",
        "orientation_kp": 0.0,
        "normal_axis_weight": 1.0,
        "description": "v82 weighted zero-angular-command candidate.",
    },
    {
        "name": "weighted_kp0_normal30",
        "orientation_priority_mode": "weighted",
        "orientation_kp": 0.0,
        "normal_axis_weight": 30.0,
        "description": "v82 weighted zero-angular-command candidate with normal weight 30.",
    },
]


def value_label(prefix: str, value: float) -> str:
    text = f"{float(value):.8g}".replace("-", "m").replace(".", "p")
    return f"{prefix}_{text}"


def e2_command(
    *,
    out_dir: pathlib.Path,
    source_run: pathlib.Path,
    delta_m: float,
    stage_a_duration_s: float,
    paper_time_scale: float,
    qdot_limit_rad_s: float,
    max_orientation_error_rad: float,
    scenario: dict[str, Any],
) -> list[str]:
    case_name = base_z_delta_label(delta_m)
    return [
        sys.executable,
        str(ROOT / "scripts" / "evaluate_stitched_stage_a_handoff.py"),
        "--output-dir",
        str(out_dir),
        "--stage-a-target-config",
        str(source_run / "relaxed_stage_a_target_config.yaml"),
        "--source-path-csv",
        str(source_run / "cases" / case_name / "path" / "path.csv"),
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
        "--trajectories",
        "e2-figure-eight",
    ]


def summarize_case(
    *,
    delta_m: float,
    scenario: dict[str, Any],
    metrics: dict[str, Any],
    orientation_gate_rad: float,
) -> dict[str, Any]:
    rows = metrics["stage_b"]["rows"]
    if len(rows) != 1 or rows[0]["trajectory"] != "e2-figure-eight":
        raise ValueError("expected exactly one e2-figure-eight row")
    row = rows[0]
    gate = row["feasibility_gate"]
    target = row["target_pair_metrics"]
    orientation = float(target["max_orientation_error_rad"])
    return {
        "scenario": str(scenario["name"]),
        "description": str(scenario["description"]),
        "base_z_offset_delta_m": float(delta_m),
        "base_z_offset_delta_mm": 1000.0 * float(delta_m),
        "orientation_priority_mode": str(scenario["orientation_priority_mode"]),
        "orientation_kp": float(scenario["orientation_kp"]),
        "normal_axis_weight": float(scenario["normal_axis_weight"]),
        "paper_time_scale": float(metrics["paper_time_scale"]),
        "qdot_limit_rad_s": float(metrics["qdot_limit_rad_s"]),
        "stage_a_duration_s": float(metrics["stage_a_duration_s"]),
        "stage_a_passed": bool(metrics["stage_a"]["stage_a_gate"]["passed"]),
        "e2_passed": bool(gate["feasibility_pass"]),
        "failed_criteria": list(gate["failed_criteria"]),
        "orientation_gate_rad": float(orientation_gate_rad),
        "orientation_error_rad": orientation,
        "orientation_excess_over_gate_rad": orientation - float(orientation_gate_rad),
        "qdot_saturation_fraction": float(target["qdot_saturation_fraction"]),
        "tail_max_qdot_utilization": float(target["tail_max_qdot_utilization"]),
        "max_qdot_utilization": float(target["max_qdot_utilization"]),
        "max_abs_qdot_rad_s": float(target["max_abs_qdot_rad_s"]),
        "tail_mean_abs_force_error_N": float(target["tail_mean_abs_force_error_N"]),
        "max_tangential_position_error_m": float(target["max_tangential_position_error_m"]),
        "max_abs_normal_velocity_slack_m_s": float(target["max_abs_normal_velocity_slack_m_s"]),
        "max_angular_velocity_slack_rad_s": float(target["max_angular_velocity_slack_rad_s"]),
        "contact_present_fraction": float(target["contact_present_fraction"]),
        "source_path_csv": str(metrics["source_path_csv"]),
    }


def aggregate_cases(cases: list[dict[str, Any]], *, orientation_gate_rad: float) -> dict[str, Any]:
    passing = [case for case in cases if case["stage_a_passed"] and case["e2_passed"]]
    orientation_clear = [case for case in cases if case["orientation_error_rad"] <= orientation_gate_rad]
    qdot_clear = [case for case in cases if case["qdot_saturation_fraction"] <= 0.01]
    tail_qdot_clear = [case for case in cases if case["tail_max_qdot_utilization"] <= 0.98]
    best_orientation = min(cases, key=lambda case: case["orientation_error_rad"])
    return {
        "scenario_count": len(cases),
        "e2_pass_count": len(passing),
        "e2_fail_count": len(cases) - len(passing),
        "passing_scenarios": [case["scenario"] for case in passing],
        "orientation_clear_scenarios": [case["scenario"] for case in orientation_clear],
        "qdot_clear_scenarios": [case["scenario"] for case in qdot_clear],
        "tail_qdot_clear_scenarios": [case["scenario"] for case in tail_qdot_clear],
        "best_orientation_scenario": best_orientation["scenario"],
        "min_orientation_error_rad": best_orientation["orientation_error_rad"],
        "min_orientation_excess_over_gate_rad": best_orientation["orientation_excess_over_gate_rad"],
        "max_orientation_error_rad": max(case["orientation_error_rad"] for case in cases),
        "max_qdot_saturation_fraction": max(case["qdot_saturation_fraction"] for case in cases),
        "min_qdot_saturation_fraction": min(case["qdot_saturation_fraction"] for case in cases),
        "max_tail_qdot_utilization": max(case["tail_max_qdot_utilization"] for case in cases),
        "min_tail_qdot_utilization": min(case["tail_max_qdot_utilization"] for case in cases),
        "max_tail_force_error_N": max(case["tail_mean_abs_force_error_N"] for case in cases),
        "min_tail_force_error_N": min(case["tail_mean_abs_force_error_N"] for case in cases),
    }


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    lines = [
        "# Positive Fast E2 Orientation-Margin Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Scenario count: `{aggregate['scenario_count']}`",
        f"- E2 pass count: `{aggregate['e2_pass_count']} / {aggregate['scenario_count']}`",
        f"- Passing scenarios: `{', '.join(aggregate['passing_scenarios']) or 'none'}`",
        f"- Best orientation scenario: `{aggregate['best_orientation_scenario']}`",
        f"- Minimum orientation error: `{aggregate['min_orientation_error_rad']}`",
        "",
        "| scenario | priority | normal weight | orientation_kp | E2 pass | failed criteria | orientation | qdot sat | tail qdot | force err |",
        "| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for case in cases:
        lines.append(
            "| `{scenario}` | `{priority}` | `{normal}` | `{kp}` | `{passed}` | `{failed}` | `{orientation}` | `{qdot}` | `{tail_qdot}` | `{force}` |".format(
                scenario=case["scenario"],
                priority=case["orientation_priority_mode"],
                normal=case["normal_axis_weight"],
                kp=case["orientation_kp"],
                passed=case["e2_passed"],
                failed=";".join(case["failed_criteria"]) or "none",
                orientation=case["orientation_error_rad"],
                qdot=case["qdot_saturation_fraction"],
                tail_qdot=case["tail_max_qdot_utilization"],
                force=case["tail_mean_abs_force_error_N"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The probe keeps `paper_time_scale = 0.0075`, `qdot_limit = 0.15 rad/s`, and the run-local `0.12 rad` orientation gate fixed.",
            "- Passing rows are diagnostic priority-formulation evidence only; they do not make a canonical controller change or close the v99 failed cell.",
            "- Any stronger claim still needs full failed-cell audit coverage and the unresolved contact/gate calibration blockers remain open.",
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
    parser.add_argument("--paper-time-scale", type=float, default=0.0075)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--max-orientation-error-rad", type=float, default=0.12)
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    delta_m = float(args.base_z_delta_mm) / 1000.0
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "positive_fast_e2_orientation_margin" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = []
    for scenario in SCENARIOS:
        scenario_name = str(scenario["name"])
        case_dir = out_dir / "scenarios" / scenario_name
        case_dir.mkdir(parents=True, exist_ok=True)
        metrics = run_child(
            e2_command(
                out_dir=case_dir,
                source_run=source_run,
                delta_m=delta_m,
                stage_a_duration_s=args.stage_a_duration_s,
                paper_time_scale=args.paper_time_scale,
                qdot_limit_rad_s=args.qdot_limit_rad_s,
                max_orientation_error_rad=args.max_orientation_error_rad,
                scenario=scenario,
            ),
            out_dir=case_dir,
        )
        cases.append(
            summarize_case(
                delta_m=delta_m,
                scenario=scenario,
                metrics=metrics,
                orientation_gate_rad=args.max_orientation_error_rad,
            )
        )

    aggregate = aggregate_cases(cases, orientation_gate_rad=args.max_orientation_error_rad)
    payload = {
        "run_id": run_id,
        "source": "v106 positive fast-timing E2 orientation-margin priority probe",
        "source_run": str(source_run),
        "relaxed_stage_a_target_config": str(source_run / "relaxed_stage_a_target_config.yaml"),
        "base_z_offset_delta_m": delta_m,
        "base_z_offset_delta_mm": float(args.base_z_delta_mm),
        "stage_a_duration_s": float(args.stage_a_duration_s),
        "stage_b_trajectory": "e2-figure-eight",
        "paper_time_scale": float(args.paper_time_scale),
        "qdot_limit_rad_s": float(args.qdot_limit_rad_s),
        "orientation_gate_rad": float(args.max_orientation_error_rad),
        "scenarios": SCENARIOS,
        "aggregate": aggregate,
        "cases": cases,
        "claim_boundary": {
            "e2_only_probe": True,
            "failed_cell_closed": False,
            "canonical_controller_change": False,
            "orientation_gate_relaxed": False,
            "robustness_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "hardware_readiness": False,
        },
        "warnings": [
            "diagnostic-label E2-only priority probe",
            "does not rerun the full E1-E4 failed-cell audit",
            "not a canonical controller change",
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
