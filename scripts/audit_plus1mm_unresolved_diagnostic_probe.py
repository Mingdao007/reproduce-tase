#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Any

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
CURRENT_GATE_RAD = 0.119


DEFAULT_EXECUTION_AUDIT = (
    "runs/failed_diagnostic_robustness_experiment_audit/20260525T061328/metrics.yaml"
)
DEFAULT_EXPERIMENT_ROOT = (
    "runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments"
)


def rad_to_deg(value: float | None) -> float | None:
    if value is None:
        return None
    return float(value) * 180.0 / 3.141592653589793


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_git_state(out_dir: pathlib.Path, *, command: list[str]) -> None:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
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


def cell_by_id(execution_audit: dict[str, Any], cell_id: str) -> dict[str, Any]:
    for cell in execution_audit["cell_results"]:
        if cell["cell_id"] == cell_id:
            return cell
    raise KeyError(cell_id)


def first_case(metrics: dict[str, Any]) -> dict[str, Any]:
    cases = metrics.get("cases", [])
    if not cases:
        raise ValueError("metrics file has no cases")
    return cases[0]


def current_gate_weighted_cases(weighted_metrics: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in weighted_metrics["full_groups"]:
        if abs(float(group["orientation_gate_rad"]) - CURRENT_GATE_RAD) > 1e-12:
            continue
        for case in group["cases"]:
            rows.append(
                {
                    "group": group["name"],
                    "scenario": group["scenario"],
                    "paper_time_scale": float(group["paper_time_scale"]),
                    "orientation_gate_rad": float(group["orientation_gate_rad"]),
                    "stage_a_passed": bool(case["stage_a_passed"]),
                    "stitched_passed": bool(case["stitched_passed"]),
                    "handoff_pass_count": int(case["handoff_pass_count"]),
                    "handoff_trajectory_count": int(case["handoff_trajectory_count"]),
                    "stage_a_terminal_orientation_error_rad": float(
                        case["stage_a_terminal_orientation_error_rad"]
                    ),
                    "stage_b_max_orientation_error_rad": float(
                        case["stage_b_max_orientation_error_rad"]
                    ),
                    "stage_b_max_qdot_saturation_fraction": float(
                        case["stage_b_max_qdot_saturation_fraction"]
                    ),
                    "stage_b_failed_rows": [
                        {
                            "trajectory": row["trajectory"],
                            "failed_criteria": list(row["failed_criteria"]),
                        }
                        for row in case["stage_b_failed_rows"]
                    ],
                }
            )
    return rows


def boundary_rows(weighted_metrics: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for group in weighted_metrics["boundary_groups"]:
        aggregate = group["aggregate"]
        rows.append(
            {
                "group": group["name"],
                "paper_time_scale": float(group["paper_time_scale"]),
                "min_passing_orientation_gate_rad": aggregate["min_passing_orientation_gate_rad"],
                "max_failing_orientation_gate_rad": aggregate["max_failing_orientation_gate_rad"],
                "min_passing_minus_current_gate_rad": (
                    float(aggregate["min_passing_orientation_gate_rad"]) - CURRENT_GATE_RAD
                    if aggregate["min_passing_orientation_gate_rad"] is not None
                    else None
                ),
                "max_stage_b_orientation_error_rad": float(
                    aggregate["max_stage_b_orientation_error_rad"]
                ),
                "max_stage_b_qdot_saturation_fraction": float(
                    aggregate["max_stage_b_qdot_saturation_fraction"]
                ),
            }
        )
    return rows


def build_base_z_row(execution_cell: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    case = first_case(metrics)
    terminal = case["terminal"]
    orientation = float(terminal["orientation_error_rad"])
    return {
        "cell_id": "base_z_plus1mm",
        "status": execution_cell["status"],
        "closure_passed": bool(execution_cell["closure_passed"]),
        "diagnostic_class": "start_terminal_path_unrecovered",
        "base_z_offset_delta_mm": float(case["base_z_offset_delta_mm"]),
        "start_passed": bool(case["start"]["passed"]),
        "start_failed_criteria": list(case["start"]["failed_criteria"]),
        "terminal_passed": bool(terminal["passed"]),
        "terminal_failed_criteria": list(terminal["failed_criteria"]),
        "terminal_orientation_error_rad": orientation,
        "terminal_orientation_excess_over_current_gate_rad": orientation - CURRENT_GATE_RAD,
        "terminal_orientation_excess_over_current_gate_deg": rad_to_deg(
            orientation - CURRENT_GATE_RAD
        ),
        "path_geometry_recovered": case["path"] is not None,
        "duration_recovered_count": len(case["durations"]),
        "primary_blockers": [
            "start_contact_not_recovered",
            "terminal_orientation_over_gate",
            "path_geometry_not_recovered",
            "duration_not_recovered",
        ],
    }


def build_positive_fast_row(execution_cell: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    scenario = metrics["scenarios"][0]
    case = scenario["cases"][0]
    max_orientation = float(case["stage_b_max_orientation_error_rad"])
    max_gate = float(scenario["parameters"]["max_orientation_error_rad"])
    failed_rows = [
        {
            "trajectory": row["trajectory"],
            "failed_criteria": list(row["failed_criteria"]),
        }
        for row in case["stage_b_failed_rows"]
    ]
    return {
        "cell_id": "positive_fast_timing_0p0075",
        "status": execution_cell["status"],
        "closure_passed": bool(execution_cell["closure_passed"]),
        "diagnostic_class": "fast_timing_e2_qdot_and_orientation",
        "base_z_offset_delta_mm": float(case["base_z_offset_delta_mm"]),
        "paper_time_scale": float(scenario["parameters"]["paper_time_scale"]),
        "stage_a_passed": bool(case["stage_a_passed"]),
        "stitched_passed": bool(case["stitched_passed"]),
        "handoff_pass_count": int(case["handoff_pass_count"]),
        "handoff_trajectory_count": int(case["handoff_trajectory_count"]),
        "stage_b_failed_rows": failed_rows,
        "stage_b_max_qdot_saturation_fraction": float(
            case["stage_b_max_qdot_saturation_fraction"]
        ),
        "stage_b_max_tail_qdot_utilization": float(case["stage_b_max_tail_qdot_utilization"]),
        "stage_b_max_orientation_error_rad": max_orientation,
        "orientation_gate_rad": max_gate,
        "stage_b_orientation_excess_over_gate_rad": max_orientation - max_gate,
        "stage_b_orientation_excess_over_current_gate_rad": max_orientation - CURRENT_GATE_RAD,
        "primary_blockers": [
            "e2_qdot_saturation",
            "e2_tail_qdot_utilization",
            "e2_orientation_over_gate",
        ],
    }


def build_positive_orientation_row(
    execution_cell: dict[str, Any], metrics: dict[str, Any]
) -> dict[str, Any]:
    aggregate = metrics["aggregate"]
    current_case = next(
        case for case in metrics["cases"] if abs(float(case["orientation_gate_rad"]) - CURRENT_GATE_RAD) < 1e-12
    )
    max_orientation = float(aggregate["max_stage_b_orientation_error_rad"])
    min_passing = float(aggregate["min_passing_orientation_gate_rad"])
    return {
        "cell_id": "positive_orientation_gate_0p119",
        "status": execution_cell["status"],
        "closure_passed": bool(execution_cell["closure_passed"]),
        "diagnostic_class": "unweighted_orientation_margin",
        "base_z_offset_delta_mm": float(metrics["base_z_offset_delta_mm"]),
        "current_gate_rad": CURRENT_GATE_RAD,
        "current_gate_stage_a_passed": bool(current_case["stage_a_passed"]),
        "current_gate_stitched_passed": bool(current_case["stitched_passed"]),
        "current_gate_handoff_pass_count": int(current_case["handoff_pass_count"]),
        "current_gate_handoff_trajectory_count": int(current_case["handoff_trajectory_count"]),
        "current_gate_failed_rows": [
            {
                "trajectory": row["trajectory"],
                "failed_criteria": list(row["failed_criteria"]),
                "orientation_error_rad": float(row["orientation_error_rad"]),
            }
            for row in current_case["stage_b_orientation_rows"]
            if row["failed_criteria"]
        ],
        "min_passing_orientation_gate_rad": min_passing,
        "max_failing_orientation_gate_rad": float(aggregate["max_failing_orientation_gate_rad"]),
        "min_passing_minus_current_gate_rad": min_passing - CURRENT_GATE_RAD,
        "stage_a_terminal_orientation_error_rad": float(
            aggregate["max_stage_a_terminal_orientation_error_rad"]
        ),
        "stage_b_max_orientation_error_rad": max_orientation,
        "stage_b_orientation_excess_over_current_gate_rad": max_orientation - CURRENT_GATE_RAD,
        "stage_b_max_qdot_saturation_fraction": float(
            current_case["stage_b_max_qdot_saturation_fraction"]
        ),
        "primary_blockers": [
            "current_gate_stage_a_terminal_orientation",
            "current_gate_stage_b_orientation",
            "replacement_gate_not_accepted",
        ],
    }


def build_weighted_row(execution_cell: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    current_cases = current_gate_weighted_cases(metrics)
    boundaries = boundary_rows(metrics)
    max_stage_b_orientation = max(case["stage_b_max_orientation_error_rad"] for case in current_cases)
    max_qdot = max(case["stage_b_max_qdot_saturation_fraction"] for case in current_cases)
    min_passing = [
        float(row["min_passing_orientation_gate_rad"])
        for row in boundaries
        if row["min_passing_orientation_gate_rad"] is not None
    ]
    return {
        "cell_id": "weighted_plus1mm_0p119_gate",
        "status": execution_cell["status"],
        "closure_passed": bool(execution_cell["closure_passed"]),
        "diagnostic_class": "weighted_orientation_margin_without_qdot_saturation",
        "current_gate_rad": CURRENT_GATE_RAD,
        "current_gate_case_count": len(current_cases),
        "current_gate_failed_count": sum(1 for case in current_cases if not case["stitched_passed"]),
        "current_gate_cases": current_cases,
        "current_gate_max_stage_b_orientation_error_rad": max_stage_b_orientation,
        "current_gate_stage_b_orientation_excess_over_current_gate_rad": (
            max_stage_b_orientation - CURRENT_GATE_RAD
        ),
        "current_gate_max_qdot_saturation_fraction": max_qdot,
        "diagnostic_boundaries": boundaries,
        "diagnostic_min_passing_gates_rad": min_passing,
        "max_min_passing_minus_current_gate_rad": (
            max(min_passing) - CURRENT_GATE_RAD if min_passing else None
        ),
        "primary_blockers": [
            "current_gate_stage_a_terminal_orientation",
            "current_gate_stage_b_orientation",
            "replacement_gate_not_accepted",
        ],
    }


def build_payload(
    *,
    execution_audit_path: pathlib.Path,
    experiment_root: pathlib.Path,
) -> dict[str, Any]:
    execution_audit = load_yaml(execution_audit_path)
    base_metrics = load_yaml(experiment_root / "base_z_plus1mm" / "metrics.yaml")
    positive_fast_metrics = load_yaml(experiment_root / "positive_fast_timing_0p0075" / "metrics.yaml")
    positive_orientation_metrics = load_yaml(
        experiment_root / "positive_orientation_gate_0p119" / "metrics.yaml"
    )
    weighted_metrics = load_yaml(experiment_root / "weighted_plus1mm_0p119_gate" / "metrics.yaml")

    base_z = build_base_z_row(cell_by_id(execution_audit, "base_z_plus1mm"), base_metrics)
    positive_fast = build_positive_fast_row(
        cell_by_id(execution_audit, "positive_fast_timing_0p0075"),
        positive_fast_metrics,
    )
    positive_orientation = build_positive_orientation_row(
        cell_by_id(execution_audit, "positive_orientation_gate_0p119"),
        positive_orientation_metrics,
    )
    weighted = build_weighted_row(
        cell_by_id(execution_audit, "weighted_plus1mm_0p119_gate"),
        weighted_metrics,
    )
    cell_rows = [base_z, positive_fast, positive_orientation, weighted]
    qdot_limited = [
        row["cell_id"]
        for row in cell_rows
        if any("qdot" in blocker for blocker in row["primary_blockers"])
    ]
    orientation_limited = [
        row["cell_id"]
        for row in cell_rows
        if any("orientation" in blocker for blocker in row["primary_blockers"])
    ]
    unresolved = [row["cell_id"] for row in cell_rows if not row["closure_passed"]]

    payload = {
        "run_source": "v104 plus1mm unresolved diagnostic probe",
        "source_files": {
            "execution_audit": str(execution_audit_path),
            "experiment_root": str(experiment_root),
            "base_z_plus1mm": str(experiment_root / "base_z_plus1mm" / "metrics.yaml"),
            "positive_fast_timing_0p0075": str(
                experiment_root / "positive_fast_timing_0p0075" / "metrics.yaml"
            ),
            "positive_orientation_gate_0p119": str(
                experiment_root / "positive_orientation_gate_0p119" / "metrics.yaml"
            ),
            "weighted_plus1mm_0p119_gate": str(
                experiment_root / "weighted_plus1mm_0p119_gate" / "metrics.yaml"
            ),
        },
        "current_gate_rad": CURRENT_GATE_RAD,
        "execution_audit_summary": execution_audit["summary"],
        "summary": {
            "planned_failed_cell_count": int(execution_audit["summary"]["cell_count"]),
            "executed_cell_count": int(execution_audit["summary"]["executed_cell_count"]),
            "closed_cell_count": int(execution_audit["summary"]["closed_cell_count"]),
            "not_executed_cell_count": int(execution_audit["summary"]["not_executed_cell_count"]),
            "unresolved_cell_count": len(unresolved),
            "unresolved_cell_ids": unresolved,
            "qdot_limited_cell_ids": qdot_limited,
            "orientation_limited_cell_ids": orientation_limited,
            "current_gate_still_blocks": True,
            "replacement_gate_accepted": False,
            "probe_closes_failed_cells": False,
        },
        "cell_rows": cell_rows,
        "ranked_orientation_excess_over_current_gate": sorted(
            [
                {
                    "cell_id": "base_z_plus1mm",
                    "quantity": "terminal_orientation",
                    "excess_rad": base_z["terminal_orientation_excess_over_current_gate_rad"],
                    "excess_deg": base_z["terminal_orientation_excess_over_current_gate_deg"],
                },
                {
                    "cell_id": "positive_fast_timing_0p0075",
                    "quantity": "stage_b_max_orientation",
                    "excess_rad": positive_fast[
                        "stage_b_orientation_excess_over_current_gate_rad"
                    ],
                    "excess_deg": rad_to_deg(
                        positive_fast["stage_b_orientation_excess_over_current_gate_rad"]
                    ),
                },
                {
                    "cell_id": "positive_orientation_gate_0p119",
                    "quantity": "stage_b_max_orientation",
                    "excess_rad": positive_orientation[
                        "stage_b_orientation_excess_over_current_gate_rad"
                    ],
                    "excess_deg": rad_to_deg(
                        positive_orientation["stage_b_orientation_excess_over_current_gate_rad"]
                    ),
                },
                {
                    "cell_id": "weighted_plus1mm_0p119_gate",
                    "quantity": "stage_b_max_orientation",
                    "excess_rad": weighted[
                        "current_gate_stage_b_orientation_excess_over_current_gate_rad"
                    ],
                    "excess_deg": rad_to_deg(
                        weighted[
                            "current_gate_stage_b_orientation_excess_over_current_gate_rad"
                        ]
                    ),
                },
            ],
            key=lambda row: row["excess_rad"],
            reverse=True,
        ),
        "claim_boundary": {
            "offline_diagnostic_probe_only": True,
            "probe_closes_failed_cells": False,
            "do_not_mark_goal_complete": True,
            "robustness_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "contact_calibration_claim": False,
            "orientation_gate_acceptance": False,
            "hardware_readiness": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
        },
        "next_offline_actions": [
            "Do not upgrade any v99 failed cell from this post-hoc probe.",
            "Separate the base_z_plus1mm start-contact miss from terminal orientation before another recovery claim.",
            "Treat positive_fast_timing_0p0075 as the only remaining +1.0 mm row with a qdot-saturation blocker.",
            "Treat positive_orientation_gate_0p119 and weighted_plus1mm_0p119_gate as gate-margin rows until measured geometry or an accepted diagnostic gate exists.",
            "Keep live read-only SOP work blocked until explicit user approval exists for the exact step.",
        ],
        "warnings": [
            "post-hoc offline audit of existing v100-v103 metrics only",
            "does not rerun MuJoCo or change controller defaults",
            "does not accept a replacement orientation gate",
            "does not calibrate contact geometry or force frames",
            "not strict paper-equivalent feasibility",
            "not a robustness proof",
            "not hardware-ready",
        ],
    }
    return payload


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Plus1mm Unresolved Diagnostic Probe Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Planned failed cells: `{summary['planned_failed_cell_count']}`",
        f"- Executed cells: `{summary['executed_cell_count']}`",
        f"- Closed cells: `{summary['closed_cell_count']}`",
        f"- Not-executed cells: `{summary['not_executed_cell_count']}`",
        f"- Unresolved cells: `{summary['unresolved_cell_count']}`",
        f"- Qdot-limited cells: `{', '.join(summary['qdot_limited_cell_ids']) or 'none'}`",
        f"- Orientation-limited cells: `{', '.join(summary['orientation_limited_cell_ids']) or 'none'}`",
        "",
        "## Cell Signatures",
        "",
        "| cell | class | closure | key margin | qdot sat | blockers |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in payload["cell_rows"]:
        if row["cell_id"] == "base_z_plus1mm":
            margin = row["terminal_orientation_excess_over_current_gate_rad"]
            qdot = "n/a"
        elif row["cell_id"] == "positive_fast_timing_0p0075":
            margin = row["stage_b_orientation_excess_over_gate_rad"]
            qdot = row["stage_b_max_qdot_saturation_fraction"]
        elif row["cell_id"] == "positive_orientation_gate_0p119":
            margin = row["stage_b_orientation_excess_over_current_gate_rad"]
            qdot = row["stage_b_max_qdot_saturation_fraction"]
        else:
            margin = row["current_gate_stage_b_orientation_excess_over_current_gate_rad"]
            qdot = row["current_gate_max_qdot_saturation_fraction"]
        lines.append(
            "| `{cell}` | `{klass}` | `{closure}` | `{margin}` | `{qdot}` | `{blockers}` |".format(
                cell=row["cell_id"],
                klass=row["diagnostic_class"],
                closure=row["closure_passed"],
                margin=margin,
                qdot=qdot,
                blockers=", ".join(row["primary_blockers"]),
            )
        )

    lines.extend(
        [
            "",
            "## Ranked Orientation Excess Over Current Gate",
            "",
            "| cell | quantity | excess rad | excess deg |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    for row in payload["ranked_orientation_excess_over_current_gate"]:
        lines.append(
            "| `{cell}` | `{quantity}` | `{rad}` | `{deg}` |".format(
                cell=row["cell_id"],
                quantity=row["quantity"],
                rad=row["excess_rad"],
                deg=row["excess_deg"],
            )
        )

    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The four v99 failed cells are all executed and all remain unresolved.",
            "- The only `+1.0 mm` row with a qdot-saturation blocker is the unweighted fast-timing `paper_time_scale = 0.0075` case.",
            "- The orientation-gate rows remain above the current `0.119 rad` gate, and the diagnostic replacement gates are not accepted.",
            "- This is post-hoc offline bookkeeping over existing metrics. It does not close a cell, calibrate contact geometry, or authorize hardware work.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution-audit", default=DEFAULT_EXECUTION_AUDIT)
    parser.add_argument("--experiment-root", default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "plus1mm_unresolved_diagnostic_probe" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(
        execution_audit_path=(ROOT / args.execution_audit).resolve(),
        experiment_root=(ROOT / args.experiment_root).resolve(),
    )
    payload["run_id"] = run_id
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
