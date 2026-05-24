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

from audit_stage_a_base_z_recovery import write_git_state


CRITICAL_FULL_GROUPS = [
    "time0p0075_gate0p119:weighted_kp0_normal1",
    "time0p0075_gate0p119:weighted_kp0_normal30",
    "time0p01_gate0p119:weighted_kp0_normal1",
    "time0p01_gate0p119:weighted_kp0_normal30",
]

CRITICAL_BOUNDARY_GROUPS = [
    "gate_boundary_plus1mm_time_0p0075",
    "gate_boundary_plus1mm_time_0p01",
]


def rad_to_deg(value: float | None) -> float | None:
    if value is None:
        return None
    return float(value) * 180.0 / 3.141592653589793


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def group_by_name(groups: list[dict[str, Any]], name: str) -> dict[str, Any]:
    for group in groups:
        if group["name"] == name:
            return group
    raise KeyError(name)


def case_by_variant_and_delta(
    cases: list[dict[str, Any]],
    *,
    variant: str,
    delta_mm: float,
) -> dict[str, Any]:
    for case in cases:
        if case["variant"] == variant and abs(float(case["base_z_offset_delta_mm"]) - delta_mm) < 1e-9:
            return case
    raise KeyError(f"{variant}:{delta_mm}")


def orientation_margin_row(group: dict[str, Any], *, gate_rad: float) -> dict[str, Any]:
    aggregate = group["aggregate"]
    stage_a_orientation = float(aggregate["max_stage_a_terminal_orientation_error_rad"])
    stage_b_orientation = float(aggregate["max_stage_b_orientation_error_rad"])
    return {
        "group": group["name"],
        "paper_time_scale": float(group["paper_time_scale"]),
        "scenario": group["scenario"],
        "gate_rad": float(gate_rad),
        "stitched_pass_count": int(aggregate["stitched_pass_count"]),
        "case_count": int(aggregate["case_count"]),
        "max_positive_stitched_pass_delta_mm": aggregate["max_positive_stitched_pass_delta_mm"],
        "stage_a_all_passed": bool(aggregate["stage_a_all_passed"]),
        "stage_a_terminal_orientation_rad": stage_a_orientation,
        "stage_b_max_orientation_rad": stage_b_orientation,
        "stage_a_excess_over_gate_rad": stage_a_orientation - float(gate_rad),
        "stage_b_excess_over_gate_rad": stage_b_orientation - float(gate_rad),
        "stage_b_minus_stage_a_rad": stage_b_orientation - stage_a_orientation,
        "stage_a_excess_over_gate_deg": rad_to_deg(stage_a_orientation - float(gate_rad)),
        "stage_b_excess_over_gate_deg": rad_to_deg(stage_b_orientation - float(gate_rad)),
        "stage_b_minus_stage_a_deg": rad_to_deg(stage_b_orientation - stage_a_orientation),
        "failing_cases": list(aggregate["failing_cases"]),
        "max_stage_b_qdot_saturation_fraction": float(
            aggregate["max_stage_b_qdot_saturation_fraction"]
        ),
        "max_stage_b_tail_qdot_utilization": float(aggregate["max_stage_b_tail_qdot_utilization"]),
        "max_stage_b_tail_force_error_N": float(aggregate["max_stage_b_tail_force_error_N"]),
    }


def high_end_terminal_slope_rad_per_mm(cases: list[dict[str, Any]], *, variant: str) -> float:
    delta075 = case_by_variant_and_delta(cases, variant=variant, delta_mm=0.75)
    delta100 = case_by_variant_and_delta(cases, variant=variant, delta_mm=1.0)
    return (
        float(delta100["full_rotation_error_rad"]) - float(delta075["full_rotation_error_rad"])
    ) / 0.25


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Weighted Orientation Model Sensitivity Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        "## Critical V83 Rows",
        "",
        "| group | pass | Stage A orientation | Stage B orientation | Stage B excess over 0.119 | qdot sat | tail qdot |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["critical_full_rows"]:
        lines.append(
            "| `{group}` | `{passed}/{count}` | `{stage_a}` | `{stage_b}` | `{excess}` | `{qdot}` | `{tail_qdot}` |".format(
                group=row["group"],
                passed=row["stitched_pass_count"],
                count=row["case_count"],
                stage_a=row["stage_a_terminal_orientation_rad"],
                stage_b=row["stage_b_max_orientation_rad"],
                excess=row["stage_b_excess_over_gate_rad"],
                qdot=row["max_stage_b_qdot_saturation_fraction"],
                tail_qdot=row["max_stage_b_tail_qdot_utilization"],
            )
        )

    lines.extend(
        [
            "",
            "## Gate Boundary",
            "",
            "| group | min passing gate | max failing gate | Stage B max orientation |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in payload["gate_boundary_rows"]:
        lines.append(
            "| `{group}` | `{min_pass}` | `{max_fail}` | `{orientation}` |".format(
                group=row["group"],
                min_pass=row["min_passing_orientation_gate_rad"],
                max_fail=row["max_failing_orientation_gate_rad"],
                orientation=row["max_stage_b_orientation_error_rad"],
            )
        )

    proxy = payload["terminal_model_sensitivity"]
    lines.extend(
        [
            "",
            "## Terminal Model Sensitivity",
            "",
            f"- Contact-point +1.0 mm terminal orientation: `{proxy['contact_point_plus1mm_orientation_rad']}` rad",
            f"- Legacy-center +1.0 mm terminal orientation: `{proxy['legacy_center_plus1mm_orientation_rad']}` rad",
            f"- Geometry-convention orientation delta: `{proxy['contact_point_minus_legacy_center_plus1mm_rad']}` rad",
            f"- High-end terminal slope proxy: `{proxy['contact_point_high_end_slope_rad_per_mm']}` rad/mm",
            "",
            "## Interpretation",
            "",
            "- The v83 `0.119 rad` failures are orientation-margin failures; qdot saturation is `0.0` in the critical weighted rows.",
            "- The remaining Stage B excess over `0.119 rad` is less than `0.00057 rad` (`0.033 deg`).",
            "- The contact-point versus legacy-center geometry convention changes the +1.0 mm terminal orientation by about `0.024 rad`, much larger than the remaining v83 margin.",
            "- This is a sensitivity/attribution audit only. It is not a recovery, calibration, robustness proof, paper-equivalent claim, or hardware-ready result.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--v83-metrics",
        default="runs/weighted_gate_time_matrix/20260524T232637/metrics.yaml",
    )
    parser.add_argument(
        "--v69-metrics",
        default="runs/positive_terminal_orientation/20260524T171705/metrics.yaml",
    )
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    v83_path = (ROOT / args.v83_metrics).resolve()
    v69_path = (ROOT / args.v69_metrics).resolve()
    v83 = load_yaml(v83_path)
    v69 = load_yaml(v69_path)

    gate_rad = 0.119
    critical_full_rows = [
        orientation_margin_row(group_by_name(v83["full_groups"], name), gate_rad=gate_rad)
        for name in CRITICAL_FULL_GROUPS
    ]

    gate_boundary_rows = []
    for name in CRITICAL_BOUNDARY_GROUPS:
        group = group_by_name(v83["boundary_groups"], name)
        aggregate = group["aggregate"]
        gate_boundary_rows.append(
            {
                "group": name,
                "paper_time_scale": float(group["paper_time_scale"]),
                "min_passing_orientation_gate_rad": aggregate["min_passing_orientation_gate_rad"],
                "max_failing_orientation_gate_rad": aggregate["max_failing_orientation_gate_rad"],
                "max_stage_a_terminal_orientation_error_rad": aggregate[
                    "max_stage_a_terminal_orientation_error_rad"
                ],
                "max_stage_b_orientation_error_rad": aggregate[
                    "max_stage_b_orientation_error_rad"
                ],
                "min_passing_minus_0p119_rad": (
                    float(aggregate["min_passing_orientation_gate_rad"]) - gate_rad
                    if aggregate["min_passing_orientation_gate_rad"] is not None
                    else None
                ),
                "min_passing_minus_0p119_deg": rad_to_deg(
                    float(aggregate["min_passing_orientation_gate_rad"]) - gate_rad
                    if aggregate["min_passing_orientation_gate_rad"] is not None
                    else None
                ),
            }
        )

    contact_plus1 = case_by_variant_and_delta(v69["cases"], variant="contact_point", delta_mm=1.0)
    legacy_plus1 = case_by_variant_and_delta(v69["cases"], variant="legacy_center", delta_mm=1.0)
    slope = high_end_terminal_slope_rad_per_mm(v69["cases"], variant="contact_point")
    max_stage_b_excess = max(row["stage_b_excess_over_gate_rad"] for row in critical_full_rows)
    terminal_sensitivity = {
        "contact_point_plus1mm_orientation_rad": float(contact_plus1["full_rotation_error_rad"]),
        "legacy_center_plus1mm_orientation_rad": float(legacy_plus1["full_rotation_error_rad"]),
        "contact_point_minus_legacy_center_plus1mm_rad": float(
            contact_plus1["full_rotation_error_rad"] - legacy_plus1["full_rotation_error_rad"]
        ),
        "contact_point_minus_legacy_center_plus1mm_deg": rad_to_deg(
            float(contact_plus1["full_rotation_error_rad"] - legacy_plus1["full_rotation_error_rad"])
        ),
        "contact_point_high_end_slope_rad_per_mm": slope,
        "max_stage_b_excess_equivalent_base_z_mm": max_stage_b_excess / slope,
        "stage_a_terminal_excess_equivalent_base_z_mm": (
            float(contact_plus1["full_rotation_error_rad"]) - gate_rad
        )
        / slope,
    }

    payload = {
        "run_source": "v84 weighted orientation model sensitivity",
        "v83_metrics": str(v83_path),
        "v69_metrics": str(v69_path),
        "orientation_gate_rad": gate_rad,
        "critical_full_rows": critical_full_rows,
        "gate_boundary_rows": gate_boundary_rows,
        "terminal_model_sensitivity": terminal_sensitivity,
        "warnings": [
            "post-hoc sensitivity/attribution audit only",
            "does not rerun MuJoCo with a calibrated physical model",
            "does not change controller defaults",
            "does not recover the 0.119 rad gate",
            "not strict paper-equivalent feasibility",
            "not contact-model calibration",
            "not hardware-ready",
        ],
    }

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "weighted_orientation_model_sensitivity" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
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
