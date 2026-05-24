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

DEFAULT_FAST_METRICS = "runs/positive_fast_weighted_full_cell/20260525T064719/metrics.yaml"
DEFAULT_BASE_Z_METRICS = "runs/relaxed_base_z_weighted_handoff/20260525T073012/metrics.yaml"
PROFILE_NAME = "weighted_zero_angular_stage_b_diagnostic"


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


def case_passed(case: dict[str, Any]) -> bool:
    return bool(case["stage_a_passed"]) and bool(case["stitched_passed"])


def compact_case(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario": str(case["scenario"]),
        "orientation_priority_mode": str(case["orientation_priority_mode"]),
        "orientation_kp": float(case["orientation_kp"]),
        "normal_axis_weight": float(case["normal_axis_weight"]),
        "stage_a_duration_s": float(case["stage_a_duration_s"]),
        "stage_a_passed": bool(case["stage_a_passed"]),
        "stitched_passed": bool(case["stitched_passed"]),
        "handoff_pass_count": int(case["handoff_pass_count"]),
        "handoff_trajectory_count": int(case["handoff_trajectory_count"]),
        "failed_trajectories": list(case["failed_trajectories"]),
        "failed_criteria_by_trajectory": dict(case["failed_criteria_by_trajectory"]),
        "max_stage_b_orientation_error_rad": float(case["max_stage_b_orientation_error_rad"]),
        "max_stage_b_qdot_saturation_fraction": float(case["max_stage_b_qdot_saturation_fraction"]),
        "max_stage_b_tail_qdot_utilization": float(case["max_stage_b_tail_qdot_utilization"]),
        "max_stage_b_tail_force_error_N": float(case["max_stage_b_tail_force_error_N"]),
    }


def build_face_summary(*, face_id: str, description: str, metrics: dict[str, Any]) -> dict[str, Any]:
    cases = [compact_case(case) for case in metrics["cases"]]
    baseline = [case for case in cases if case["orientation_priority_mode"] == "linear_primary"]
    weighted = [case for case in cases if case["orientation_priority_mode"] == "weighted"]
    weighted_passing = [case for case in weighted if case_passed(case)]
    baseline_failing = [case for case in baseline if not case_passed(case)]
    source_boundary = metrics["claim_boundary"]
    return {
        "face_id": face_id,
        "description": description,
        "source": metrics["source"],
        "run_id": str(metrics["run_id"]),
        "base_z_offset_delta_mm": float(metrics["base_z_offset_delta_mm"]),
        "paper_time_scale": float(metrics["paper_time_scale"]),
        "qdot_limit_rad_s": float(metrics["qdot_limit_rad_s"]),
        "orientation_gate_rad": float(metrics["orientation_gate_rad"]),
        "stage_a_durations_s": sorted({case["stage_a_duration_s"] for case in cases}),
        "case_count": len(cases),
        "baseline_case_count": len(baseline),
        "baseline_failing_count": len(baseline_failing),
        "baseline_failing_cases": [
            {
                "scenario": case["scenario"],
                "stage_a_duration_s": case["stage_a_duration_s"],
                "failed_trajectories": list(case["failed_trajectories"]),
                "max_stage_b_orientation_error_rad": case["max_stage_b_orientation_error_rad"],
                "max_stage_b_qdot_saturation_fraction": case[
                    "max_stage_b_qdot_saturation_fraction"
                ],
                "max_stage_b_tail_qdot_utilization": case[
                    "max_stage_b_tail_qdot_utilization"
                ],
            }
            for case in baseline_failing
        ],
        "weighted_case_count": len(weighted),
        "weighted_passing_count": len(weighted_passing),
        "weighted_all_passed": bool(weighted) and len(weighted_passing) == len(weighted),
        "weighted_passing_cases": [
            {
                "scenario": case["scenario"],
                "stage_a_duration_s": case["stage_a_duration_s"],
                "normal_axis_weight": case["normal_axis_weight"],
                "max_stage_b_orientation_error_rad": case["max_stage_b_orientation_error_rad"],
                "max_stage_b_qdot_saturation_fraction": case[
                    "max_stage_b_qdot_saturation_fraction"
                ],
                "max_stage_b_tail_qdot_utilization": case[
                    "max_stage_b_tail_qdot_utilization"
                ],
                "max_stage_b_tail_force_error_N": case["max_stage_b_tail_force_error_N"],
            }
            for case in weighted_passing
        ],
        "max_weighted_orientation_error_rad": max(
            case["max_stage_b_orientation_error_rad"] for case in weighted
        ),
        "max_weighted_qdot_saturation_fraction": max(
            case["max_stage_b_qdot_saturation_fraction"] for case in weighted
        ),
        "max_weighted_tail_qdot_utilization": max(
            case["max_stage_b_tail_qdot_utilization"] for case in weighted
        ),
        "min_weighted_tail_force_error_N": min(
            case["max_stage_b_tail_force_error_N"] for case in weighted
        ),
        "source_boundary_preserved": {
            "failed_cell_closed": bool(source_boundary.get("failed_cell_closed", False)),
            "canonical_controller_change": bool(
                source_boundary.get("canonical_controller_change", False)
            ),
            "canonical_orientation_gate_change": bool(
                source_boundary.get("canonical_orientation_gate_change", False)
            ),
            "robustness_claim": bool(source_boundary.get("robustness_claim", False)),
            "strict_paper_equivalent_feasibility": bool(
                source_boundary.get("strict_paper_equivalent_feasibility", False)
            ),
            "hardware_readiness": bool(source_boundary.get("hardware_readiness", False)),
        },
    }


def evaluate_profile_boundary(faces: list[dict[str, Any]]) -> dict[str, Any]:
    weighted_all_faces = all(face["weighted_all_passed"] for face in faces)
    baseline_failure_all_faces = all(face["baseline_failing_count"] > 0 for face in faces)
    source_boundaries_preserved = all(
        not any(face["source_boundary_preserved"].values()) for face in faces
    )
    scope_parameters_consistent = all(
        abs(float(face["base_z_offset_delta_mm"]) - 1.0) < 1e-12
        and abs(float(face["qdot_limit_rad_s"]) - 0.15) < 1e-12
        and abs(float(face["orientation_gate_rad"]) - 0.12) < 1e-12
        for face in faces
    )
    diagnostic_profile_naming_supported = (
        len(faces) >= 2
        and weighted_all_faces
        and baseline_failure_all_faces
        and source_boundaries_preserved
        and scope_parameters_consistent
    )
    return {
        "profile_name": PROFILE_NAME,
        "diagnostic_profile_naming_supported": diagnostic_profile_naming_supported,
        "evidence_face_count": len(faces),
        "covered_faces": [face["face_id"] for face in faces],
        "weighted_all_faces_recovered": weighted_all_faces,
        "baseline_failure_reproduced_all_faces": baseline_failure_all_faces,
        "source_boundaries_preserved": source_boundaries_preserved,
        "scope_parameters_consistent": scope_parameters_consistent,
        "profile_scope": {
            "orientation_priority_mode": "weighted",
            "orientation_kp": 0.0,
            "normal_axis_weight_values": [1.0, 30.0],
            "base_z_offset_delta_mm": 1.0,
            "qdot_limit_rad_s": 0.15,
            "orientation_gate_rad": 0.12,
            "orientation_gate_status": "run_local_diagnostic_noncanonical",
            "contact_model": "current_contact_point_model_unverified_hardware_calibration",
            "stage_b_trajectories": ["e1-cycloid", "e2-figure-eight", "e3-circle", "e4-cardioid"],
            "covered_paper_time_scales": sorted({face["paper_time_scale"] for face in faces}),
            "covered_stage_a_durations_s": sorted(
                {duration for face in faces for duration in face["stage_a_durations_s"]}
            ),
        },
        "claim_boundary": {
            "can_name_diagnostic_profile": diagnostic_profile_naming_supported,
            "canonical_controller_change": False,
            "canonical_orientation_gate_change": False,
            "failed_cell_closed": False,
            "robustness_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "contact_calibration_claim": False,
            "hardware_readiness": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
        },
        "unsupported_extensions": [
            "canonical controller default",
            "accepted replacement orientation gate",
            "closure of original v99 failed cells",
            "formal robustness proof",
            "strict paper-equivalent staged feasibility",
            "contact geometry calibration",
            "hardware readiness or authorization",
        ],
    }


def build_payload(*, fast_metrics_path: pathlib.Path, base_z_metrics_path: pathlib.Path) -> dict[str, Any]:
    fast_metrics = load_yaml(fast_metrics_path)
    base_z_metrics = load_yaml(base_z_metrics_path)
    faces = [
        build_face_summary(
            face_id="positive_fast_timing_full_e1e4",
            description="v107 +1.0 mm fast-timing full E1-E4 face",
            metrics=fast_metrics,
        ),
        build_face_summary(
            face_id="relaxed_base_z_plus1mm_handoff",
            description="v109 relaxed +1.0 mm base-z Stage B handoff face",
            metrics=base_z_metrics,
        ),
    ]
    boundary = evaluate_profile_boundary(faces)
    return {
        "run_source": "v110 weighted priority profile boundary audit",
        "source_files": {
            "positive_fast_weighted_full_cell": str(fast_metrics_path),
            "relaxed_base_z_weighted_handoff": str(base_z_metrics_path),
        },
        "profile_boundary": boundary,
        "evidence_faces": faces,
        "summary": {
            "profile_name": boundary["profile_name"],
            "diagnostic_profile_naming_supported": boundary[
                "diagnostic_profile_naming_supported"
            ],
            "evidence_face_count": boundary["evidence_face_count"],
            "covered_faces": list(boundary["covered_faces"]),
            "weighted_all_faces_recovered": boundary["weighted_all_faces_recovered"],
            "baseline_failure_reproduced_all_faces": boundary[
                "baseline_failure_reproduced_all_faces"
            ],
            "can_name_diagnostic_profile": boundary["claim_boundary"][
                "can_name_diagnostic_profile"
            ],
            "canonical_controller_change": False,
            "canonical_orientation_gate_change": False,
            "failed_cell_closed": False,
            "robustness_claim": False,
            "hardware_readiness": False,
            "max_weighted_orientation_error_rad": max(
                face["max_weighted_orientation_error_rad"] for face in faces
            ),
            "max_weighted_qdot_saturation_fraction": max(
                face["max_weighted_qdot_saturation_fraction"] for face in faces
            ),
            "max_weighted_tail_qdot_utilization": max(
                face["max_weighted_tail_qdot_utilization"] for face in faces
            ),
        },
        "next_offline_actions": [
            "Do not change the canonical controller default from this audit.",
            "Use the named weighted profile only as diagnostic-label scope unless a later acceptance review changes the boundary.",
            "Keep original v99 failed cells open until canonical gate/controller/contact evidence exists.",
            "Do not claim robustness from the two recovered faces.",
            "Keep live read-only SOP work blocked until explicit user approval exists for the exact step.",
        ],
        "warnings": [
            "post-hoc offline audit of existing v107 and v109 metrics only",
            "does not rerun MuJoCo",
            "does not accept weighted priority as canonical",
            "does not accept the 0.12 rad orientation gate as canonical",
            "does not close original v99 failed cells",
            "not strict paper-equivalent feasibility",
            "not a robustness proof",
            "not contact-model calibration",
            "not hardware-ready",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    boundary = payload["profile_boundary"]
    summary = payload["summary"]
    lines = [
        "# Weighted Priority Profile Boundary Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Profile name: `{summary['profile_name']}`",
        f"- Diagnostic profile naming supported: `{summary['diagnostic_profile_naming_supported']}`",
        f"- Evidence faces: `{', '.join(summary['covered_faces'])}`",
        f"- Weighted all faces recovered: `{summary['weighted_all_faces_recovered']}`",
        f"- Baseline failure reproduced all faces: `{summary['baseline_failure_reproduced_all_faces']}`",
        f"- Canonical controller change: `{summary['canonical_controller_change']}`",
        f"- Canonical orientation gate change: `{summary['canonical_orientation_gate_change']}`",
        f"- Failed cell closed: `{summary['failed_cell_closed']}`",
        f"- Robustness claim: `{summary['robustness_claim']}`",
        "",
        "| face | baseline failures | weighted passes | max weighted orientation | max weighted qdot sat | max weighted tail qdot |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for face in payload["evidence_faces"]:
        lines.append(
            "| `{face}` | `{baseline}` | `{weighted}` | `{orientation}` | `{qdot}` | `{tail_qdot}` |".format(
                face=face["face_id"],
                baseline=face["baseline_failing_count"],
                weighted=face["weighted_passing_count"],
                orientation=face["max_weighted_orientation_error_rad"],
                qdot=face["max_weighted_qdot_saturation_fraction"],
                tail_qdot=face["max_weighted_tail_qdot_utilization"],
            )
        )
    lines.extend(
        [
            "",
            "Supported diagnostic profile scope:",
            "",
            f"- Orientation priority mode: `{boundary['profile_scope']['orientation_priority_mode']}`",
            f"- Orientation kp: `{boundary['profile_scope']['orientation_kp']}`",
            f"- Normal-axis weights: `{boundary['profile_scope']['normal_axis_weight_values']}`",
            f"- Orientation gate status: `{boundary['profile_scope']['orientation_gate_status']}`",
            "",
            "Interpretation:",
            "",
            "- The existing evidence supports naming `weighted_zero_angular_stage_b_diagnostic` as a diagnostic profile for the covered faces.",
            "- This audit does not make the profile canonical, accept the `0.12 rad` gate, close any original v99 failed cell, prove robustness, or authorize hardware work.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast-metrics", default=DEFAULT_FAST_METRICS)
    parser.add_argument("--base-z-metrics", default=DEFAULT_BASE_Z_METRICS)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "weighted_priority_profile_boundary" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        fast_metrics_path=(ROOT / args.fast_metrics).resolve(),
        base_z_metrics_path=(ROOT / args.base_z_metrics).resolve(),
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
