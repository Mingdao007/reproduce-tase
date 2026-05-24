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

from audit_stage_a_base_z_bracket import parse_float_list
from audit_stage_a_base_z_recovery import run_child, write_git_state
from tase_repro.base_z_recovery import base_z_delta_label


TRAJECTORY_ORDER = ["e1-cycloid", "e2-figure-eight", "e3-circle", "e4-cardioid"]

DEFAULTS: dict[str, float] = {
    "stage_a_duration_s": 15.0,
    "paper_time_scale": 0.005,
    "qdot_limit_rad_s": 0.15,
    "max_orientation_error_rad": 0.12,
}

DEFAULT_SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "nominal_v72",
        "parameters": {},
        "description": "v72 recovered positive stitched policy.",
    },
    {
        "name": "stage_a_14p5s",
        "parameters": {"stage_a_duration_s": 14.5},
        "description": "Shorter Stage A replay duration with nominal Stage B settings.",
    },
    {
        "name": "qdot012_stage_a18s",
        "parameters": {"qdot_limit_rad_s": 0.12, "stage_a_duration_s": 18.0},
        "description": "Reduced qdot limit with longer Stage A replay to preserve path tracking.",
    },
    {
        "name": "paper_time_scale_0p0075",
        "parameters": {"paper_time_scale": 0.0075},
        "description": "Faster Stage B trajectory timing than the v72 recovery value.",
    },
    {
        "name": "orientation_gate_0p119",
        "parameters": {
            "stage_a_orientation_gate_rad": 0.119,
            "max_orientation_error_rad": 0.119,
        },
        "description": "Tightened run-local Stage A terminal gate and Stage B orientation gate.",
    },
]


def scenario_by_name() -> dict[str, dict[str, Any]]:
    return {str(scenario["name"]): scenario for scenario in DEFAULT_SCENARIOS}


def selected_scenarios(names: str) -> list[dict[str, Any]]:
    if names == "all":
        return DEFAULT_SCENARIOS
    available = scenario_by_name()
    selected = []
    for name in [part.strip() for part in names.split(",") if part.strip()]:
        if name not in available:
            raise ValueError(f"unknown scenario {name!r}; available: {', '.join(sorted(available))}")
        selected.append(available[name])
    if not selected:
        raise ValueError("at least one scenario is required")
    return selected


def effective_parameters(parameters: dict[str, Any]) -> dict[str, float]:
    merged = dict(DEFAULTS)
    for key, value in parameters.items():
        if key == "stage_a_orientation_gate_rad":
            continue
        if key not in DEFAULTS:
            raise ValueError(f"unsupported scenario parameter: {key}")
        merged[key] = float(value)
    return merged


def write_stage_a_config_for_scenario(
    *,
    out_dir: pathlib.Path,
    source_config: pathlib.Path,
    scenario_name: str,
    parameters: dict[str, Any],
) -> pathlib.Path:
    orientation_gate = parameters.get("stage_a_orientation_gate_rad")
    if orientation_gate is None:
        return source_config

    config = yaml.safe_load(source_config.read_text(encoding="utf-8"))
    target = config["selected_stage_a_target"]
    target["diagnostic_gate"]["max_terminal_orientation_error_rad"] = float(orientation_gate)
    config.setdefault("v73_positive_stitched_sensitivity_scope", {})
    config["v73_positive_stitched_sensitivity_scope"] = {
        "scenario": scenario_name,
        "source_config": str(source_config),
        "max_terminal_orientation_error_rad": float(orientation_gate),
        "claim_scope": "run-local sensitivity config only",
    }
    if "v70_relaxed_orientation_scope" in config:
        config["v70_relaxed_orientation_scope"]["max_terminal_orientation_error_rad"] = float(orientation_gate)

    config_dir = out_dir / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    scenario_config = config_dir / f"{scenario_name}_stage_a_target_config.yaml"
    with scenario_config.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)
    return scenario_config


def stitched_command(
    *,
    out_dir: pathlib.Path,
    source_run: pathlib.Path,
    stage_a_target_config: pathlib.Path,
    delta_m: float,
    parameters: dict[str, float],
) -> list[str]:
    case_name = base_z_delta_label(delta_m)
    return [
        sys.executable,
        str(ROOT / "scripts" / "evaluate_stitched_stage_a_handoff.py"),
        "--output-dir",
        str(out_dir),
        "--stage-a-target-config",
        str(stage_a_target_config),
        "--source-path-csv",
        str(source_run / "cases" / case_name / "path" / "path.csv"),
        "--base-z-offset-delta-m",
        f"{float(delta_m):.17g}",
        "--stage-a-duration-s",
        f"{parameters['stage_a_duration_s']:.17g}",
        "--paper-time-scale",
        f"{parameters['paper_time_scale']:.17g}",
        "--qdot-limit-rad-s",
        f"{parameters['qdot_limit_rad_s']:.17g}",
        "--max-orientation-error-rad",
        f"{parameters['max_orientation_error_rad']:.17g}",
    ]


def stage_a_failed_criteria(metrics: dict[str, Any]) -> list[str]:
    stage_a = metrics["stage_a"]
    criteria = stage_a["stage_a_gate"]["criteria"]
    terminal_gate = stage_a["terminal_gate"]
    terminal_criteria = terminal_gate["criteria"]
    failed = []
    if criteria["target_contact_present_fraction"] < 1.0:
        failed.append("target_contact_present_fraction")
    if criteria["max_force_error_N"] > terminal_criteria["terminal_force_error_N"]["threshold"]:
        failed.append("max_force_error_N")
    if criteria["max_scheduled_xy_error_m"] > terminal_criteria["terminal_xy_error_m"]["threshold"]:
        failed.append("max_scheduled_xy_error_m")
    if (
        criteria["max_scheduled_orientation_error_rad"]
        > terminal_criteria["terminal_force_normal_orientation_error_rad"]["threshold"]
    ):
        failed.append("max_scheduled_orientation_error_rad")
    if criteria["max_abs_qdot_rad_s"] > float(metrics["qdot_limit_rad_s"]) + 1e-12:
        failed.append("max_abs_qdot_rad_s")
    if criteria["final_tracking_error_norm_rad"] > 1e-9:
        failed.append("final_tracking_error_norm_rad")
    if not terminal_gate["passed"]:
        terminal_failed = terminal_gate.get("failed_criteria", [])
        failed.extend(f"terminal_gate:{name}" for name in terminal_failed)
    return failed


def summarize_case(delta_m: float, metrics: dict[str, Any]) -> dict[str, Any]:
    stage_b_rows = metrics["stage_b"]["rows"]
    stage_b_failed = [
        {
            "trajectory": row["trajectory"],
            "failed_criteria": list(row["feasibility_gate"]["failed_criteria"]),
        }
        for row in stage_b_rows
        if not row["feasibility_gate"]["feasibility_pass"]
    ]
    stage_a = metrics["stage_a"]
    terminal_gate = stage_a["terminal_gate"]
    stage_a_gate = stage_a["stage_a_gate"]
    tracking = stage_a["tracking"]
    evaluation = stage_a["evaluation"]
    stage_b_pass_count = int(metrics["stitched_gate"]["handoff_pass_count"])
    stage_b_count = int(metrics["stitched_gate"]["handoff_trajectory_count"])
    max_qdot_saturation = max(row["target_pair_metrics"]["qdot_saturation_fraction"] for row in stage_b_rows)
    max_tail_qdot = max(row["target_pair_metrics"]["tail_max_qdot_utilization"] for row in stage_b_rows)
    max_orientation = max(row["target_pair_metrics"]["max_orientation_error_rad"] for row in stage_b_rows)
    max_force = max(row["target_pair_metrics"]["tail_mean_abs_force_error_N"] for row in stage_b_rows)
    max_xy = max(row["target_pair_metrics"]["max_tangential_position_error_m"] for row in stage_b_rows)
    return {
        "case": base_z_delta_label(delta_m),
        "base_z_offset_delta_m": float(delta_m),
        "base_z_offset_delta_mm": 1000.0 * float(delta_m),
        "stage_a_passed": bool(metrics["stitched_gate"]["stage_a_passed"]),
        "stage_a_terminal_gate_passed": bool(terminal_gate["passed"]),
        "stage_a_terminal_failed_criteria": list(terminal_gate.get("failed_criteria", [])),
        "stage_a_failed_criteria": stage_a_failed_criteria(metrics),
        "stage_a_gate_criteria": stage_a_gate["criteria"],
        "stitched_passed": bool(metrics["stitched_gate"]["passed"]),
        "handoff_pass_count": stage_b_pass_count,
        "handoff_trajectory_count": stage_b_count,
        "stage_b_failed_rows": stage_b_failed,
        "stage_a_max_qdot_rad_s": float(tracking["max_abs_qdot_rad_s"]),
        "stage_a_qdot_saturation_fraction": float(tracking["qdot_saturation_fraction"]),
        "stage_a_final_tracking_error_norm_rad": float(tracking["final_tracking_error_norm_rad"]),
        "stage_a_terminal_force_error_N": float(evaluation["terminal_force_error_N"]),
        "stage_a_terminal_xy_error_m": float(evaluation["terminal_reference_xy_error_m"]),
        "stage_a_terminal_orientation_error_rad": float(
            evaluation["terminal_force_normal_orientation_error_rad"]
        ),
        "stage_b_max_qdot_saturation_fraction": float(max_qdot_saturation),
        "stage_b_max_tail_qdot_utilization": float(max_tail_qdot),
        "stage_b_max_orientation_error_rad": float(max_orientation),
        "stage_b_max_tail_force_error_N": float(max_force),
        "stage_b_max_xy_error_m": float(max_xy),
        "source_path_csv": str(metrics["source_path_csv"]),
    }


def aggregate_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    passed = [case["case"] for case in cases if case["stitched_passed"]]
    failed = [case["case"] for case in cases if not case["stitched_passed"]]
    passed_deltas = [case["base_z_offset_delta_mm"] for case in cases if case["stitched_passed"]]
    stage_a_passed = [case["case"] for case in cases if case["stage_a_passed"]]
    return {
        "case_count": len(cases),
        "stitched_pass_count": len(passed),
        "stitched_fail_count": len(failed),
        "stage_a_pass_count": len(stage_a_passed),
        "passing_cases": passed,
        "failing_cases": failed,
        "all_cases_passed": len(passed) == len(cases) and bool(cases),
        "max_positive_stitched_pass_delta_mm": max(passed_deltas) if passed_deltas else None,
        "max_stage_a_terminal_orientation_error_rad": max(
            case["stage_a_terminal_orientation_error_rad"] for case in cases
        ),
        "max_stage_b_qdot_saturation_fraction": max(
            case["stage_b_max_qdot_saturation_fraction"] for case in cases
        ),
        "max_stage_b_tail_qdot_utilization": max(case["stage_b_max_tail_qdot_utilization"] for case in cases),
        "max_stage_b_orientation_error_rad": max(case["stage_b_max_orientation_error_rad"] for case in cases),
    }


def aggregate_scenarios(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    matrix_case_count = sum(scenario["aggregate"]["case_count"] for scenario in scenarios)
    matrix_pass_count = sum(scenario["aggregate"]["stitched_pass_count"] for scenario in scenarios)
    failing_scenarios = [
        scenario["scenario"]
        for scenario in scenarios
        if not scenario["aggregate"]["all_cases_passed"]
    ]
    return {
        "scenario_count": len(scenarios),
        "matrix_case_count": matrix_case_count,
        "matrix_stitched_pass_count": matrix_pass_count,
        "matrix_stitched_fail_count": matrix_case_count - matrix_pass_count,
        "scenario_all_pass_count": len(scenarios) - len(failing_scenarios),
        "failing_scenarios": failing_scenarios,
        "all_scenarios_passed": not failing_scenarios and bool(scenarios),
    }


def run_scenario(
    scenario: dict[str, Any],
    *,
    out_dir: pathlib.Path,
    source_run: pathlib.Path,
    deltas_m: list[float],
) -> dict[str, Any]:
    name = str(scenario["name"])
    parameters_raw = dict(scenario.get("parameters", {}))
    parameters = effective_parameters(parameters_raw)
    source_config = source_run / "relaxed_stage_a_target_config.yaml"
    stage_a_target_config = write_stage_a_config_for_scenario(
        out_dir=out_dir,
        source_config=source_config,
        scenario_name=name,
        parameters=parameters_raw,
    )
    cases = []
    scenario_dir = out_dir / "scenarios" / name
    for delta_m in deltas_m:
        case_name = base_z_delta_label(delta_m)
        case_dir = scenario_dir / "cases" / case_name
        case_dir.mkdir(parents=True, exist_ok=True)
        metrics = run_child(
            stitched_command(
                out_dir=case_dir,
                source_run=source_run,
                stage_a_target_config=stage_a_target_config,
                delta_m=delta_m,
                parameters=parameters,
            ),
            out_dir=case_dir,
        )
        cases.append(summarize_case(delta_m, metrics))

    aggregate = aggregate_cases(cases)
    return {
        "scenario": name,
        "description": scenario["description"],
        "parameters": parameters,
        "stage_a_orientation_gate_rad": parameters_raw.get("stage_a_orientation_gate_rad"),
        "stage_a_target_config": str(stage_a_target_config),
        "aggregate": aggregate,
        "cases": cases,
    }


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], scenarios: list[dict[str, Any]]) -> None:
    lines = [
        "# Positive Stitched Sensitivity Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Scenario count: `{aggregate['scenario_count']}`",
        f"- Matrix stitched pass count: `{aggregate['matrix_stitched_pass_count']} / {aggregate['matrix_case_count']}`",
        f"- All-pass scenarios: `{aggregate['scenario_all_pass_count']} / {aggregate['scenario_count']}`",
        f"- Failing scenarios: `{', '.join(aggregate['failing_scenarios']) or 'none'}`",
        "",
        "| scenario | pass count | Stage A pass count | max pass delta mm | max Stage A terminal orientation | max Stage B orientation | max Stage B qdot sat | failing deltas |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for scenario in scenarios:
        scenario_aggregate = scenario["aggregate"]
        failing = ", ".join(scenario_aggregate["failing_cases"]) or "none"
        lines.append(
            "| `{scenario}` | `{passed}/{count}` | `{stage_a}/{count}` | `{delta}` | `{stage_a_orientation}` | `{stage_b_orientation}` | `{qdot}` | `{failing}` |".format(
                scenario=scenario["scenario"],
                passed=scenario_aggregate["stitched_pass_count"],
                count=scenario_aggregate["case_count"],
                stage_a=scenario_aggregate["stage_a_pass_count"],
                delta=scenario_aggregate["max_positive_stitched_pass_delta_mm"],
                stage_a_orientation=scenario_aggregate["max_stage_a_terminal_orientation_error_rad"],
                stage_b_orientation=scenario_aggregate["max_stage_b_orientation_error_rad"],
                qdot=scenario_aggregate["max_stage_b_qdot_saturation_fraction"],
                failing=failing,
            )
        )

    lines.extend(
        [
            "",
            "Failure Detail:",
            "",
            "| scenario | delta mm | stitched | Stage A | Stage B pass | Stage A terminal orientation | Stage B max orientation | failed Stage A criteria | failed Stage B rows |",
            "| --- | ---: | --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for scenario in scenarios:
        for case in scenario["cases"]:
            if case["stitched_passed"]:
                continue
            failed_stage_b = ";".join(
                f"{row['trajectory']}:{','.join(row['failed_criteria'])}"
                for row in case["stage_b_failed_rows"]
            )
            lines.append(
                "| `{scenario}` | `{delta}` | `{stitched}` | `{stage_a}` | `{handoff}/{count}` | `{stage_a_orientation}` | `{stage_b_orientation}` | `{stage_a_failed}` | `{stage_b_failed}` |".format(
                    scenario=scenario["scenario"],
                    delta=case["base_z_offset_delta_mm"],
                    stitched=case["stitched_passed"],
                    stage_a=case["stage_a_passed"],
                    handoff=case["handoff_pass_count"],
                    count=case["handoff_trajectory_count"],
                    stage_a_orientation=case["stage_a_terminal_orientation_error_rad"],
                    stage_b_orientation=case["stage_b_max_orientation_error_rad"],
                    stage_a_failed=",".join(case["stage_a_failed_criteria"]) or "none",
                    stage_b_failed=failed_stage_b or "none",
                )
            )

    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- Passing rows preserve the v72 positive stitched diagnostic result only under the listed perturbation.",
            "- Failing rows bound the v72 recovery and prevent a robustness or paper-equivalent claim.",
            "- This audit remains simulation-only and does not authorize hardware motion or configuration changes.",
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
    parser.add_argument("--base-z-deltas-mm", default="0.05,0.1,0.15,0.2,0.25,0.5,0.75,1.0")
    parser.add_argument("--scenarios", default="all")
    args = parser.parse_args()

    source_run = (ROOT / args.source_run).resolve()
    deltas_m = [value / 1000.0 for value in parse_float_list(args.base_z_deltas_mm)]
    scenarios_to_run = selected_scenarios(args.scenarios)
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "positive_stitched_sensitivity" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    scenarios = [
        run_scenario(
            scenario,
            out_dir=out_dir,
            source_run=source_run,
            deltas_m=deltas_m,
        )
        for scenario in scenarios_to_run
    ]
    aggregate = aggregate_scenarios(scenarios)
    payload = {
        "run_id": run_id,
        "source": "v72 positive stitched recovery sensitivity around v70 relaxed terminal/path setup",
        "source_run": str(source_run),
        "relaxed_stage_a_target_config": str(source_run / "relaxed_stage_a_target_config.yaml"),
        "default_parameters": DEFAULTS,
        "trajectories": TRAJECTORY_ORDER,
        "aggregate": aggregate,
        "scenarios": scenarios,
        "warnings": [
            "diagnostic-label positive stitched sensitivity audit only",
            "uses the v70 run-local relaxed orientation target config or run-local copies",
            "not a canonical config change",
            "not strict paper-equivalent feasibility",
            "not a formal robustness proof",
            "not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    write_summary(out_dir, aggregate, scenarios)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
