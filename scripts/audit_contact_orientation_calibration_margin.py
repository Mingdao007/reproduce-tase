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


def boundary_row_by_scale(rows: list[dict[str, Any]], scale: float) -> dict[str, Any]:
    for row in rows:
        if abs(float(row["paper_time_scale"]) - scale) < 1e-12:
            return row
    raise KeyError(scale)


def summarize_source(path: pathlib.Path, metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": str(path),
        "run_id": metrics.get("run_id"),
        "source": metrics.get("source") or metrics.get("run_source"),
    }


def critical_row(row: dict[str, Any]) -> dict[str, Any]:
    stage_a_excess = float(row["stage_a_excess_over_gate_rad"])
    stage_b_excess = float(row["stage_b_excess_over_gate_rad"])
    return {
        "group": row["group"],
        "paper_time_scale": float(row["paper_time_scale"]),
        "scenario": row["scenario"],
        "base_z_offset_delta_mm": 1.0,
        "gate_rad": float(row["gate_rad"]),
        "stitched_pass_count": int(row["stitched_pass_count"]),
        "case_count": int(row["case_count"]),
        "stage_a_all_passed": bool(row["stage_a_all_passed"]),
        "stage_a_terminal_orientation_rad": float(row["stage_a_terminal_orientation_rad"]),
        "stage_a_excess_over_gate_rad": stage_a_excess,
        "stage_a_excess_over_gate_deg": rad_to_deg(stage_a_excess),
        "stage_b_max_orientation_rad": float(row["stage_b_max_orientation_rad"]),
        "stage_b_excess_over_gate_rad": stage_b_excess,
        "stage_b_excess_over_gate_deg": rad_to_deg(stage_b_excess),
        "stage_b_minus_stage_a_rad": float(row["stage_b_minus_stage_a_rad"]),
        "stage_b_minus_stage_a_deg": float(row["stage_b_minus_stage_a_deg"]),
        "failing_cases": list(row["failing_cases"]),
        "max_stage_b_qdot_saturation_fraction": float(
            row["max_stage_b_qdot_saturation_fraction"]
        ),
        "max_stage_b_tail_qdot_utilization": float(row["max_stage_b_tail_qdot_utilization"]),
        "max_stage_b_tail_force_error_N": float(row["max_stage_b_tail_force_error_N"]),
    }


def gate_option(
    *,
    gate_rad: float,
    recovered: bool,
    evidence_scope: str,
    evidence: str,
    accepted_as_replacement_gate: bool = False,
) -> dict[str, Any]:
    return {
        "gate_rad": float(gate_rad),
        "recovered": bool(recovered),
        "evidence_scope": evidence_scope,
        "evidence": evidence,
        "accepted_as_replacement_gate": bool(accepted_as_replacement_gate),
        "replacement_gate_justified_by_existing_metrics": False,
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Contact Orientation Calibration Margin Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        "## Critical Rows",
        "",
        "| group | time scale | Stage A orientation | Stage B orientation | Stage B excess over 0.119 | qdot sat | tail qdot |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["critical_rows"]:
        lines.append(
            "| `{group}` | `{scale}` | `{stage_a}` | `{stage_b}` | `{excess}` | `{qdot}` | `{tail}` |".format(
                group=row["group"],
                scale=row["paper_time_scale"],
                stage_a=row["stage_a_terminal_orientation_rad"],
                stage_b=row["stage_b_max_orientation_rad"],
                excess=row["stage_b_excess_over_gate_rad"],
                qdot=row["max_stage_b_qdot_saturation_fraction"],
                tail=row["max_stage_b_tail_qdot_utilization"],
            )
        )

    correction = payload["equivalent_corrections"]
    lines.extend(
        [
            "",
            "## Equivalent Correction",
            "",
            f"- Required normal rotation: `{correction['required_normal_rotation_rad']}` rad (`{correction['required_normal_rotation_deg']}` deg).",
            f"- Equivalent base-z/contact-point correction under the terminal slope proxy: `{correction['equivalent_base_z_or_contact_point_mm']}` mm (`{correction['equivalent_base_z_or_contact_point_um']}` um).",
            f"- Contact-point versus legacy-center convention shift: `{correction['contact_point_vs_legacy_center_delta_rad']}` rad.",
            f"- Residual margin is `{correction['contact_convention_shift_to_required_rotation_ratio']}` times smaller than that convention shift.",
            "",
            "## Gate Options",
            "",
            "| option | gate | recovered by existing metric | accepted replacement gate | scope |",
            "| --- | ---: | --- | --- | --- |",
        ]
    )
    for name, option in payload["gate_options"].items():
        lines.append(
            "| `{name}` | `{gate}` | `{recovered}` | `{accepted}` | {scope} |".format(
                name=name,
                gate=option["gate_rad"],
                recovered=option["recovered"],
                accepted=option["accepted_as_replacement_gate"],
                scope=option["evidence_scope"],
            )
        )

    lines.extend(
        [
            "",
            "## Answers",
            "",
        ]
    )
    for item in payload["v85_objective_answers"]:
        lines.append(f"- {item['question']}: {item['answer']}")

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- This is a calibration/definition margin audit only.",
            "- It does not recover the `+1.0 mm`, `0.119 rad` gate.",
            "- It does not accept a relaxed diagnostic gate.",
            "- It does not calibrate the contact model, prove robustness, prove strict paper-equivalent feasibility, or authorize hardware motion/configuration.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--v84-metrics",
        default="runs/weighted_orientation_model_sensitivity/20260524T233945/metrics.yaml",
    )
    parser.add_argument(
        "--v83-metrics",
        default="runs/weighted_gate_time_matrix/20260524T232637/metrics.yaml",
    )
    parser.add_argument(
        "--v69-metrics",
        default="runs/positive_terminal_orientation/20260524T171705/metrics.yaml",
    )
    parser.add_argument(
        "--v77-metrics",
        default="runs/positive_orientation_gate_boundary/20260524T221842/metrics.yaml",
    )
    parser.add_argument(
        "--acceptance-config",
        default="configs/ur10e_adapted_acceptance.yaml",
    )
    parser.add_argument(
        "--stage-a-target-config",
        default="configs/ur10e_adapted_stage_a_target.yaml",
    )
    parser.add_argument(
        "--contact-config",
        default="configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml",
    )
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    source_paths = {
        "weighted_orientation_model_sensitivity": (ROOT / args.v84_metrics).resolve(),
        "weighted_gate_time_matrix": (ROOT / args.v83_metrics).resolve(),
        "positive_terminal_orientation": (ROOT / args.v69_metrics).resolve(),
        "positive_orientation_gate_boundary": (ROOT / args.v77_metrics).resolve(),
        "ur10e_adapted_acceptance": (ROOT / args.acceptance_config).resolve(),
        "ur10e_adapted_stage_a_target": (ROOT / args.stage_a_target_config).resolve(),
        "mujoco_ur10e_tilted_plane_tcp_contact_point": (ROOT / args.contact_config).resolve(),
    }
    v84 = load_yaml(source_paths["weighted_orientation_model_sensitivity"])
    v83 = load_yaml(source_paths["weighted_gate_time_matrix"])
    v69 = load_yaml(source_paths["positive_terminal_orientation"])
    v77 = load_yaml(source_paths["positive_orientation_gate_boundary"])
    acceptance = load_yaml(source_paths["ur10e_adapted_acceptance"])
    stage_a_target = load_yaml(source_paths["ur10e_adapted_stage_a_target"])
    contact_config = load_yaml(source_paths["mujoco_ur10e_tilted_plane_tcp_contact_point"])

    current_gate_rad = float(v84["orientation_gate_rad"])
    rows = [critical_row(row) for row in v84["critical_full_rows"]]
    hardest = max(rows, key=lambda row: row["stage_b_excess_over_gate_rad"])
    max_stage_b_excess = float(hardest["stage_b_excess_over_gate_rad"])
    max_stage_a_excess = max(float(row["stage_a_excess_over_gate_rad"]) for row in rows)

    terminal = v84["terminal_model_sensitivity"]
    terminal_slope_rad_per_mm = float(terminal["contact_point_high_end_slope_rad_per_mm"])
    geometry_delta_rad = float(terminal["contact_point_minus_legacy_center_plus1mm_rad"])
    equivalent_mm = max_stage_b_excess / terminal_slope_rad_per_mm
    equivalent_stage_a_mm = max_stage_a_excess / terminal_slope_rad_per_mm

    boundary_00075 = boundary_row_by_scale(v84["gate_boundary_rows"], 0.0075)
    boundary_001 = boundary_row_by_scale(v84["gate_boundary_rows"], 0.01)
    full_11995_normal1 = group_by_name(
        v83["full_groups"], "time0p01_gate0p11995:weighted_kp0_normal1"
    )
    full_11995_normal30 = group_by_name(
        v83["full_groups"], "time0p01_gate0p11995:weighted_kp0_normal30"
    )

    required_normal_rotation_rad = max_stage_b_excess
    gate_options = {
        "current_0p119": gate_option(
            gate_rad=current_gate_rad,
            recovered=False,
            evidence_scope="full positive-delta weighted matrix at +1.0 mm",
            evidence="critical v83/v84 rows pass 7 / 8 and fail the +1.0 mm row",
        ),
        "v83_min_passing_time0p0075": gate_option(
            gate_rad=float(boundary_00075["min_passing_orientation_gate_rad"]),
            recovered=True,
            evidence_scope="focused +1.0 mm gate-boundary row at paper_time_scale = 0.0075",
            evidence="v83 boundary row first passes at this discrete gate",
        ),
        "v83_min_passing_time0p01": gate_option(
            gate_rad=float(boundary_001["min_passing_orientation_gate_rad"]),
            recovered=True,
            evidence_scope="focused +1.0 mm gate-boundary row at paper_time_scale = 0.01",
            evidence="v83 boundary row first passes at this discrete gate",
        ),
        "diagnostic_0p11995": gate_option(
            gate_rad=0.11995,
            recovered=True,
            evidence_scope="full positive-delta weighted matrix at paper_time_scale = 0.01",
            evidence=(
                "v83 weighted_kp0_normal1 and weighted_kp0_normal30 each pass "
                f"{full_11995_normal1['aggregate']['stitched_pass_count']} / "
                f"{full_11995_normal1['aggregate']['case_count']} and "
                f"{full_11995_normal30['aggregate']['stitched_pass_count']} / "
                f"{full_11995_normal30['aggregate']['case_count']}"
            ),
        ),
    }

    measurement_requirements = [
        "measured mounted-stack TCP/contact point from robot flange or design flange datum",
        "verified contact sphere/patch convention and whether the 85 mm EOAT datum is center or surface",
        "plane/contact normal measured in the robot base frame",
        "force sensor zero, frame, compensation, and UR RTDE versus OnRobot source reconciliation",
        "accepted diagnostic orientation definition that states whether force-normal-only or full frame rotation is the gate",
    ]

    calibration_scale = {
        "accepted_measurement_noise_budget_exists": False,
        "required_rotation_is_below_unmeasured_model_convention_shift": True,
        "required_rotation_fraction_of_contact_convention_shift": (
            required_normal_rotation_rad / geometry_delta_rad
        ),
        "required_equivalent_mm_fraction_of_plus1mm_perturbation": equivalent_mm / 1.0,
        "plausibility_statement": (
            "The required correction is small relative to the already observed uncalibrated "
            "contact-convention sensitivity, so it is plausibly a calibration/definition "
            "margin. It is not an accepted noise-budget claim because no measured TCP, "
            "contact patch, plane normal, or force-frame calibration has been recorded."
        ),
        "model_change_statement": (
            "Any accepted recovery must update the measured geometry/normal/gate definition "
            "or produce a calibrated model; the legacy sphere-center convention is only a "
            "sensitivity comparison and is not an acceptable model change by itself."
        ),
    }

    answers = [
        {
            "question": "1. What exact orientation margin remains at the hardest currently known row?",
            "answer": (
                f"{max_stage_b_excess} rad ({rad_to_deg(max_stage_b_excess)} deg) over "
                f"the {current_gate_rad} rad gate at {hardest['group']}."
            ),
        },
        {
            "question": "2. How large a contact normal angular correction would close that margin?",
            "answer": (
                f"At least {required_normal_rotation_rad} rad "
                f"({rad_to_deg(required_normal_rotation_rad)} deg), assuming the correction "
                "acts in the error-reducing direction."
            ),
        },
        {
            "question": "3. What equivalent contact-point/TCP/base-z correction is implied?",
            "answer": (
                f"{equivalent_mm} mm ({equivalent_mm * 1000.0} um) using the v84 high-end "
                f"terminal slope proxy of {terminal_slope_rad_per_mm} rad/mm."
            ),
        },
        {
            "question": "4. Which correction sizes are plausibly below measurement/calibration noise?",
            "answer": (
                "The 0.0325 deg normal correction and 15 um equivalent geometry correction "
                "are small relative to the current unmeasured model-convention ambiguity, "
                "but no accepted measurement noise budget exists yet."
            ),
        },
        {
            "question": "5. Which physical measurements are required before a hardware claim?",
            "answer": "; ".join(measurement_requirements),
        },
        {
            "question": "6. Do existing metrics justify accepting 0.119, 0.11955, 0.1196, or 0.11995 rad?",
            "answer": (
                "They show which rows recover at those gates, but they do not justify a "
                "replacement diagnostic gate without calibrated geometry/normal evidence."
            ),
        },
        {
            "question": "7. Does this support more Stage B qdot tuning?",
            "answer": (
                "No. The hardest weighted rows report 0.0 qdot saturation and miss only by "
                "a small orientation margin."
            ),
        },
    ]

    payload = {
        "run_source": "v85 contact orientation calibration margin",
        "source_runs": {
            "weighted_orientation_model_sensitivity": summarize_source(
                source_paths["weighted_orientation_model_sensitivity"], v84
            ),
            "weighted_gate_time_matrix": summarize_source(
                source_paths["weighted_gate_time_matrix"], v83
            ),
            "positive_terminal_orientation": summarize_source(
                source_paths["positive_terminal_orientation"], v69
            ),
            "positive_orientation_gate_boundary": summarize_source(
                source_paths["positive_orientation_gate_boundary"], v77
            ),
        },
        "source_configs": {
            "ur10e_adapted_acceptance": str(source_paths["ur10e_adapted_acceptance"]),
            "ur10e_adapted_stage_a_target": str(source_paths["ur10e_adapted_stage_a_target"]),
            "mujoco_ur10e_tilted_plane_tcp_contact_point": str(
                source_paths["mujoco_ur10e_tilted_plane_tcp_contact_point"]
            ),
        },
        "config_extracts": {
            "terminal_setup_diagnostic_gate": acceptance[
                "ur10e_adapted_terminal_setup_diagnostic_gate"
            ],
            "selected_stage_a_target_diagnostic_gate": stage_a_target["selected_stage_a_target"][
                "diagnostic_gate"
            ],
            "contact_model_convention": contact_config["ur10e_mujoco"]["contact"][
                "contact_model_convention"
            ],
            "contact_tip_sphere_radius_m": contact_config["ur10e_mujoco"]["contact"][
                "contact_tip_sphere_radius_m"
            ],
            "contact_tip_sphere_center_local_m": contact_config["ur10e_mujoco"]["contact"][
                "contact_tip_sphere_center_local_m"
            ],
            "expected_normal_world": contact_config["ur10e_mujoco"]["contact"][
                "expected_normal_world"
            ],
        },
        "current_gate_rad": current_gate_rad,
        "critical_rows": rows,
        "hardest_row": hardest["group"],
        "positive_orientation_gate_boundary_reference": {
            "v77_min_passing_orientation_gate_rad": v77["aggregate"][
                "min_passing_orientation_gate_rad"
            ],
            "v77_max_stage_b_orientation_error_rad": v77["aggregate"][
                "max_stage_b_orientation_error_rad"
            ],
            "v77_scope": "v72 timing focused +1.0 mm boundary; not the v83 weighted timing row",
        },
        "equivalent_corrections": {
            "required_normal_rotation_rad": required_normal_rotation_rad,
            "required_normal_rotation_deg": rad_to_deg(required_normal_rotation_rad),
            "required_gate_increase_rad": max_stage_b_excess,
            "continuous_required_gate_rad": current_gate_rad + max_stage_b_excess,
            "discrete_v83_min_passing_gate_rad": float(
                boundary_001["min_passing_orientation_gate_rad"]
            ),
            "stage_a_required_normal_rotation_rad": max_stage_a_excess,
            "stage_a_required_normal_rotation_deg": rad_to_deg(max_stage_a_excess),
            "terminal_slope_rad_per_mm": terminal_slope_rad_per_mm,
            "equivalent_base_z_or_contact_point_mm": equivalent_mm,
            "equivalent_base_z_or_contact_point_um": equivalent_mm * 1000.0,
            "stage_a_equivalent_base_z_or_contact_point_mm": equivalent_stage_a_mm,
            "stage_a_equivalent_base_z_or_contact_point_um": equivalent_stage_a_mm * 1000.0,
            "contact_point_plus1mm_orientation_rad": float(
                terminal["contact_point_plus1mm_orientation_rad"]
            ),
            "legacy_center_plus1mm_orientation_rad": float(
                terminal["legacy_center_plus1mm_orientation_rad"]
            ),
            "contact_point_vs_legacy_center_delta_rad": geometry_delta_rad,
            "contact_point_vs_legacy_center_delta_deg": rad_to_deg(geometry_delta_rad),
            "contact_convention_shift_to_required_rotation_ratio": (
                geometry_delta_rad / required_normal_rotation_rad
            ),
        },
        "gate_options": gate_options,
        "calibration_scale_interpretation": calibration_scale,
        "next_measurements": measurement_requirements,
        "v85_objective_answers": answers,
        "support_more_stage_b_qdot_tuning": False,
        "claim_boundary": {
            "recovery_claim": False,
            "contact_calibration_claim": False,
            "paper_equivalent_feasibility": False,
            "hardware_readiness": False,
            "accepted_replacement_gate": False,
            "canonical_controller_default": False,
        },
        "warnings": [
            "post-hoc calibration/definition margin audit only",
            "does not rerun MuJoCo with a calibrated physical model",
            "does not recover the 0.119 rad gate",
            "does not accept 0.11955, 0.1196, or 0.11995 rad as replacement gates",
            "not strict paper-equivalent feasibility",
            "not contact-model calibration",
            "not hardware-ready",
        ],
    }

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "contact_orientation_calibration_margin" / run_id
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
