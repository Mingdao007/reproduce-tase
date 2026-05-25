#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

import mujoco
import numpy as np
import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.contact_ladder import positive_contact_normal_force_between
from tase_repro.force_feedback import apply_base_z_offset
from tase_repro.kinematics import (
    joint_ranges,
    load_model,
    make_data,
    orientation_error_rotvec,
    set_qpos,
    site_position,
    site_rotation_matrix,
)
from tase_repro.orientation import rotation_aligning_local_z_to_normal
from tase_repro.stage_a_contact_path_tracking import replay_qdot_limited_joint_path


DEFAULT_CONFIG = "configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml"
DEFAULT_ACCEPTANCE = "configs/ur10e_adapted_acceptance.yaml"
DEFAULT_CONTACT_MANIFOLD = "runs/contact_manifold_gate_audit/20260524T142404/metrics.yaml"
DEFAULT_STAGE_A_TRACKING = "runs/stage_a_contact_path_tracking/20260524T152346/metrics.yaml"
DEFAULT_REMAINING_BLOCKERS = "runs/remaining_blocker_prioritization/20260525T072557/metrics.yaml"
DEFAULT_V113 = "runs/strict_feasibility_policy_probe/20260525T073519/metrics.yaml"
DEFAULT_V114 = "runs/strict_command_limited_stage_a/20260525T074557/metrics.yaml"


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


@dataclass(frozen=True)
class TerminalConstraintCase:
    case_id: str
    source_case_name: str
    selected_candidate: str
    optimized_terms: tuple[str, ...]
    q_rad: np.ndarray
    note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "source_case_name": self.source_case_name,
            "selected_candidate": self.selected_candidate,
            "optimized_terms": list(self.optimized_terms),
            "q_rad": [float(x) for x in self.q_rad],
            "note": self.note,
        }


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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


def criterion_leq(actual: float, threshold: float) -> dict[str, Any]:
    return {
        "actual": float(actual),
        "operator": "<=",
        "threshold": float(threshold),
        "passed": float(actual) <= float(threshold),
        "ratio": None if float(threshold) == 0.0 else float(actual) / float(threshold),
    }


def criterion_geq(actual: float, threshold: float) -> dict[str, Any]:
    return {
        "actual": float(actual),
        "operator": ">=",
        "threshold": float(threshold),
        "passed": float(actual) >= float(threshold),
        "ratio": None if float(threshold) == 0.0 else float(actual) / float(threshold),
    }


def terminal_constraint_cases(contact_metrics: dict[str, Any]) -> list[TerminalConstraintCase]:
    cases_by_name = {case["name"]: case for case in contact_metrics["cases"]}

    xy_force = cases_by_name["xy_force"]["best_optimized_candidate"]
    xy_orientation = cases_by_name["xy_orientation"]["best_optimized_candidate"]
    force_orientation = cases_by_name["force_orientation"]["best_optimized_candidate"]
    strict_soft = cases_by_name["xy_force_orientation"]["best_candidate"]

    return [
        TerminalConstraintCase(
            case_id="terminal_xy_force_hold",
            source_case_name="xy_force",
            selected_candidate="best_optimized_candidate",
            optimized_terms=tuple(cases_by_name["xy_force"]["optimized_terms"]),
            q_rad=np.asarray(xy_force["q"], dtype=float),
            note="explicit terminal solve that holds x/y and target force, then audits orientation and qdot-timed path",
        ),
        TerminalConstraintCase(
            case_id="terminal_xy_orientation_hold",
            source_case_name="xy_orientation",
            selected_candidate="best_optimized_candidate",
            optimized_terms=tuple(cases_by_name["xy_orientation"]["optimized_terms"]),
            q_rad=np.asarray(xy_orientation["q"], dtype=float),
            note="explicit terminal solve that holds x/y and force-normal orientation, then audits contact and force",
        ),
        TerminalConstraintCase(
            case_id="terminal_force_orientation_hold",
            source_case_name="force_orientation",
            selected_candidate="best_optimized_candidate",
            optimized_terms=tuple(cases_by_name["force_orientation"]["optimized_terms"]),
            q_rad=np.asarray(force_orientation["q"], dtype=float),
            note="explicit terminal solve that holds target force and force-normal orientation, then audits x/y drift",
        ),
        TerminalConstraintCase(
            case_id="terminal_xy_force_orientation_soft_best",
            source_case_name="xy_force_orientation",
            selected_candidate="best_candidate",
            optimized_terms=tuple(cases_by_name["xy_force_orientation"]["optimized_terms"]),
            q_rad=np.asarray(strict_soft["q"], dtype=float),
            note="best soft strict terminal compromise from contact-manifold gate audit, then qdot-timed as a path target",
        ),
    ]


def max_joint_limit_violation(q: np.ndarray, q_min: np.ndarray, q_max: np.ndarray) -> float:
    q_array = np.asarray(q, dtype=float)
    lower = np.maximum(q_min - q_array, 0.0)
    upper = np.maximum(q_array - q_max, 0.0)
    return float(np.max(lower + upper))


def force_normal_orientation_error(rotation: np.ndarray, normal: np.ndarray) -> float:
    local_z = np.asarray(rotation, dtype=float)[:, 2]
    normal_unit = np.asarray(normal, dtype=float)
    local_z = local_z / np.linalg.norm(local_z)
    normal_unit = normal_unit / np.linalg.norm(normal_unit)
    return float(np.arccos(np.clip(float(np.dot(local_z, normal_unit)), -1.0, 1.0)))


def evaluate_q_samples(
    *,
    model: mujoco.MjModel,
    data: mujoco.MjData,
    q_samples: np.ndarray,
    q_min: np.ndarray,
    q_max: np.ndarray,
    reference_xy_m: np.ndarray,
    desired_rotation: np.ndarray,
    surface_normal_world: np.ndarray,
    target_force_N: float,
    site_name: str,
    plane_geom_name: str,
    contact_geom_name: str,
) -> dict[str, Any]:
    force_errors: list[float] = []
    tangential_errors: list[float] = []
    orientation_errors: list[float] = []
    force_normal_errors: list[float] = []
    contact_counts: list[int] = []
    joint_violations: list[float] = []

    for q in np.asarray(q_samples, dtype=float):
        set_qpos(model, data, q)
        mujoco.mj_forward(model, data)
        tcp = site_position(model, data, site_name)
        rotation = site_rotation_matrix(model, data, site_name)
        force, contact_count = positive_contact_normal_force_between(
            model,
            data,
            geom_a_name=plane_geom_name,
            geom_b_name=contact_geom_name,
        )
        force_errors.append(abs(float(force) - float(target_force_N)))
        tangential_errors.append(float(np.linalg.norm(tcp[:2] - reference_xy_m)))
        orientation_errors.append(float(np.linalg.norm(orientation_error_rotvec(desired_rotation, rotation))))
        force_normal_errors.append(force_normal_orientation_error(rotation, surface_normal_world))
        contact_counts.append(int(contact_count))
        joint_violations.append(max_joint_limit_violation(q, q_min, q_max))

    return {
        "sample_count": int(len(q_samples)),
        "target_contact_present_fraction": float(np.mean(np.asarray(contact_counts) > 0)),
        "min_target_contact_count": int(np.min(contact_counts)),
        "max_force_error_N": float(np.max(force_errors)),
        "terminal_force_error_N": float(force_errors[-1]),
        "max_tangential_error_m": float(np.max(tangential_errors)),
        "terminal_tangential_error_m": float(tangential_errors[-1]),
        "max_orientation_error_rad": float(np.max(orientation_errors)),
        "terminal_orientation_error_rad": float(orientation_errors[-1]),
        "max_force_normal_orientation_error_rad": float(np.max(force_normal_errors)),
        "terminal_force_normal_orientation_error_rad": float(force_normal_errors[-1]),
        "max_joint_limit_violation_rad": float(np.max(joint_violations)),
    }


def strict_setup_path_gate(
    *,
    path_summary: dict[str, Any],
    tracking_summary: dict[str, Any],
    strict_thresholds: dict[str, Any],
    qdot_limit_rad_s: float,
) -> dict[str, Any]:
    max_qdot_violation = max(
        0.0,
        float(tracking_summary["max_abs_qdot_rad_s"]) - abs(float(qdot_limit_rad_s)),
    )
    criteria = {
        "terminal_force_error_N": criterion_leq(
            path_summary["terminal_force_error_N"],
            strict_thresholds["max_tail_mean_abs_force_error_N"],
        ),
        "terminal_tangential_error_m": criterion_leq(
            path_summary["terminal_tangential_error_m"],
            strict_thresholds["max_final_tangential_error_m"],
        ),
        "terminal_orientation_error_rad": criterion_leq(
            path_summary["terminal_orientation_error_rad"],
            strict_thresholds["max_final_orientation_error_rad"],
        ),
        "path_target_contact_present_fraction": criterion_geq(
            path_summary["target_contact_present_fraction"],
            strict_thresholds["contact_present_fraction_min"],
        ),
        "setup_qdot_saturation_fraction": criterion_leq(
            tracking_summary["qdot_saturation_fraction"],
            strict_thresholds["qdot_saturation_fraction_max"],
        ),
        "setup_tail_max_qdot_utilization": criterion_leq(
            tracking_summary["tail_max_qdot_utilization"],
            strict_thresholds["tail_max_qdot_utilization_max"],
        ),
        "setup_max_qdot_violation_rad_s": criterion_leq(
            max_qdot_violation,
            strict_thresholds["max_qdot_violation_rad_s"],
        ),
        "setup_max_joint_limit_violation_rad": criterion_leq(
            path_summary["max_joint_limit_violation_rad"],
            strict_thresholds["max_joint_limit_violation_rad"],
        ),
    }
    failed = [name for name, criterion in criteria.items() if not bool(criterion["passed"])]
    return {
        "passed": not failed,
        "failed_criteria": failed,
        "criteria": criteria,
    }


def violation_score(gate: dict[str, Any]) -> float:
    score = 0.0
    for criterion in gate["criteria"].values():
        ratio = criterion.get("ratio")
        if ratio is None:
            continue
        if criterion["operator"] == "<=":
            score += max(float(ratio) - 1.0, 0.0)
        else:
            score += max(1.0 - float(ratio), 0.0)
    return float(score)


def row_from_terminal_case(
    case: TerminalConstraintCase,
    *,
    model: mujoco.MjModel,
    data: mujoco.MjData,
    q_initial: np.ndarray,
    q_min: np.ndarray,
    q_max: np.ndarray,
    reference_xy_m: np.ndarray,
    desired_rotation: np.ndarray,
    surface_normal_world: np.ndarray,
    target_force_N: float,
    site_name: str,
    plane_geom_name: str,
    contact_geom_name: str,
    strict_thresholds: dict[str, Any],
    qdot_limit_rad_s: float,
    dt_s: float,
    qdot_utilization_target: float,
) -> dict[str, Any]:
    q_path = np.vstack([q_initial, case.q_rad])
    max_delta = float(np.max(np.abs(case.q_rad - q_initial)))
    min_duration = 0.0 if max_delta == 0.0 else max_delta / abs(float(qdot_limit_rad_s))
    duration = min_duration / float(qdot_utilization_target) if min_duration > 0.0 else float(dt_s)
    tracking = replay_qdot_limited_joint_path(
        q_path,
        duration_s=duration,
        dt_s=dt_s,
        qdot_limit_rad_s=qdot_limit_rad_s,
    )
    tracking_summary = tracking.summary()
    path_summary = evaluate_q_samples(
        model=model,
        data=data,
        q_samples=tracking.q,
        q_min=q_min,
        q_max=q_max,
        reference_xy_m=reference_xy_m,
        desired_rotation=desired_rotation,
        surface_normal_world=surface_normal_world,
        target_force_N=target_force_N,
        site_name=site_name,
        plane_geom_name=plane_geom_name,
        contact_geom_name=contact_geom_name,
    )
    gate = strict_setup_path_gate(
        path_summary=path_summary,
        tracking_summary=tracking_summary,
        strict_thresholds=strict_thresholds,
        qdot_limit_rad_s=qdot_limit_rad_s,
    )
    return {
        "case_id": case.case_id,
        "formulation": "explicit_terminal_constraint_plus_qdot_timed_joint_path",
        "terminal_constraint_case": case.to_dict(),
        "duration_s": float(duration),
        "minimum_duration_s": float(min_duration),
        "qdot_utilization_target": float(qdot_utilization_target),
        "tracking_summary": tracking_summary,
        "path_summary": path_summary,
        "strict_setup_path_gate": gate,
        "strict_setup_violation_score": violation_score(gate),
    }


def row_from_diagnostic_tracking(
    tracking_metrics: dict[str, Any],
    *,
    strict_thresholds: dict[str, Any],
    qdot_limit_rad_s: float,
) -> dict[str, Any]:
    evaluation = tracking_metrics["evaluation"]
    tracking = tracking_metrics["tracking"]
    path_summary = {
        "sample_count": int(tracking["sample_count"]),
        "target_contact_present_fraction": float(evaluation["target_contact_present_fraction"]),
        "min_target_contact_count": int(evaluation["min_target_contact_count"]),
        "max_force_error_N": float(evaluation["max_force_error_N"]),
        "terminal_force_error_N": float(evaluation["terminal_force_error_N"]),
        "max_tangential_error_m": float(evaluation["max_reference_xy_error_m"]),
        "terminal_tangential_error_m": float(evaluation["terminal_reference_xy_error_m"]),
        "max_orientation_error_rad": float(evaluation["max_force_normal_orientation_error_rad"]),
        "terminal_orientation_error_rad": float(evaluation["terminal_force_normal_orientation_error_rad"]),
        "max_force_normal_orientation_error_rad": float(evaluation["max_force_normal_orientation_error_rad"]),
        "terminal_force_normal_orientation_error_rad": float(
            evaluation["terminal_force_normal_orientation_error_rad"]
        ),
        "max_joint_limit_violation_rad": 0.0,
    }
    gate = strict_setup_path_gate(
        path_summary=path_summary,
        tracking_summary=tracking,
        strict_thresholds=strict_thresholds,
        qdot_limit_rad_s=qdot_limit_rad_s,
    )
    return {
        "case_id": "diagnostic_contact_path_tracking_reference",
        "formulation": "v62_diagnostic_contact_path_tracking_reinterpreted_under_strict_gate",
        "source_path": tracking_metrics["source_path_csv"],
        "duration_s": float(tracking_metrics["duration_s"]),
        "minimum_duration_s": None,
        "qdot_utilization_target": None,
        "tracking_summary": tracking,
        "path_summary": path_summary,
        "strict_setup_path_gate": gate,
        "strict_setup_violation_score": violation_score(gate),
    }


def failure_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        for criterion in row["strict_setup_path_gate"]["failed_criteria"]:
            counts[criterion] = counts.get(criterion, 0) + 1
    return dict(sorted(counts.items()))


def terminal_criteria_pass(gate: dict[str, Any]) -> bool:
    terminal_names = {
        "terminal_force_error_N",
        "terminal_tangential_error_m",
        "terminal_orientation_error_rad",
    }
    return all(bool(gate["criteria"][name]["passed"]) for name in terminal_names)


def qdot_criteria_pass(gate: dict[str, Any]) -> bool:
    qdot_names = {
        "setup_qdot_saturation_fraction",
        "setup_tail_max_qdot_utilization",
        "setup_max_qdot_violation_rad_s",
    }
    return all(bool(gate["criteria"][name]["passed"]) for name in qdot_names)


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    best_score = min(rows, key=lambda row: row["strict_setup_violation_score"])
    best_qdot = min(
        rows,
        key=lambda row: row["strict_setup_path_gate"]["criteria"][
            "setup_qdot_saturation_fraction"
        ]["actual"],
    )
    best_xy = min(
        rows,
        key=lambda row: row["strict_setup_path_gate"]["criteria"][
            "terminal_tangential_error_m"
        ]["actual"],
    )
    best_orientation = min(
        rows,
        key=lambda row: row["strict_setup_path_gate"]["criteria"][
            "terminal_orientation_error_rad"
        ]["actual"],
    )
    return {
        "case_count": len(rows),
        "strict_setup_path_pass_count": sum(
            1 for row in rows if row["strict_setup_path_gate"]["passed"]
        ),
        "terminal_strict_criteria_pass_count": sum(
            1 for row in rows if terminal_criteria_pass(row["strict_setup_path_gate"])
        ),
        "qdot_criteria_pass_count": sum(
            1 for row in rows if qdot_criteria_pass(row["strict_setup_path_gate"])
        ),
        "setup_failed_criteria_counts": failure_counts(rows),
        "best_score_case_id": best_score["case_id"],
        "best_score": best_score["strict_setup_violation_score"],
        "best_qdot_case_id": best_qdot["case_id"],
        "best_qdot_saturation_fraction": best_qdot["strict_setup_path_gate"][
            "criteria"
        ]["setup_qdot_saturation_fraction"]["actual"],
        "best_xy_case_id": best_xy["case_id"],
        "best_xy_error_m": best_xy["path_summary"]["terminal_tangential_error_m"],
        "best_orientation_case_id": best_orientation["case_id"],
        "best_orientation_error_rad": best_orientation["path_summary"][
            "terminal_orientation_error_rad"
        ],
        "planned_setup_then_trajectory_pass_count": 0,
        "explicit_stage_a_constraint_probe_complete": False,
        "strict_paper_equivalent_feasibility": False,
    }


def build_payload(
    *,
    config_path: pathlib.Path,
    acceptance_path: pathlib.Path,
    contact_manifold_path: pathlib.Path,
    stage_a_tracking_path: pathlib.Path,
    remaining_blockers_path: pathlib.Path,
    v113_metrics_path: pathlib.Path,
    v114_metrics_path: pathlib.Path,
    qdot_limit_rad_s: float,
    qdot_utilization_target: float,
) -> dict[str, Any]:
    config = load_yaml(config_path)
    acceptance = load_yaml(acceptance_path)
    contact = load_yaml(contact_manifold_path)
    tracking = load_yaml(stage_a_tracking_path)
    remaining = load_yaml(remaining_blockers_path)
    v113 = load_yaml(v113_metrics_path)
    v114 = load_yaml(v114_metrics_path)

    model_path = (ROOT / config["ur10e_mujoco"]["mjcf_path"]).resolve()
    model = load_model(model_path)
    apply_base_z_offset(model, float(contact["base_z_offset_m"]))
    data = make_data(model)
    q_min, q_max = joint_ranges(model)
    q_initial = np.asarray(contact["initial_q"], dtype=float)
    reference_xy = np.asarray(contact["reference_xy_m"], dtype=float)
    surface_normal = np.asarray(contact["surface_normal_world"], dtype=float)
    set_qpos(model, data, q_initial)
    desired_rotation = rotation_aligning_local_z_to_normal(
        surface_normal,
        reference_rotation=site_rotation_matrix(model, data, str(contact["site_name"])),
    )
    dt_s = float(config["ur10e_mujoco"]["timestep_s"])
    strict_thresholds = acceptance["strict_setup_terminal_gate"]

    rows = [
        row_from_diagnostic_tracking(
            tracking,
            strict_thresholds=strict_thresholds,
            qdot_limit_rad_s=qdot_limit_rad_s,
        )
    ]
    for case in terminal_constraint_cases(contact):
        rows.append(
            row_from_terminal_case(
                case,
                model=model,
                data=data,
                q_initial=q_initial,
                q_min=q_min,
                q_max=q_max,
                reference_xy_m=reference_xy,
                desired_rotation=desired_rotation,
                surface_normal_world=surface_normal,
                target_force_N=float(contact["target_force_N"]),
                site_name=str(contact["site_name"]),
                plane_geom_name=str(contact["plane_geom_name"]),
                contact_geom_name=str(contact["contact_geom_name"]),
                strict_thresholds=strict_thresholds,
                qdot_limit_rad_s=qdot_limit_rad_s,
                dt_s=dt_s,
                qdot_utilization_target=qdot_utilization_target,
            )
        )

    summary = summarize_rows(rows)
    return {
        "run_source": "v115 explicit Stage A terminal/path constraint probe",
        "source_files": {
            "config": str(config_path),
            "acceptance": str(acceptance_path),
            "contact_manifold_gate_audit": str(contact_manifold_path),
            "stage_a_tracking_reference": str(stage_a_tracking_path),
            "remaining_blockers": str(remaining_blockers_path),
            "v113_policy_probe": str(v113_metrics_path),
            "v114_command_limited_probe": str(v114_metrics_path),
        },
        "v112_priority_context": {
            "top_priority_blocker_id": remaining["summary"]["top_priority_blocker_id"],
            "offline_actionable_blocker_ids": remaining["summary"][
                "offline_actionable_blocker_ids"
            ],
        },
        "v113_context": {
            "setup_terminal_state_pass_count": v113["summary"][
                "setup_terminal_state_pass_count"
            ],
            "planned_setup_then_trajectory_pass_count": v113["summary"][
                "planned_setup_then_trajectory_pass_count"
            ],
            "full_staged_feasibility_pass_count": v113["summary"][
                "full_staged_feasibility_pass_count"
            ],
        },
        "v114_context": {
            "strict_setup_chain_pass_count": v114["summary"][
                "strict_setup_chain_pass_count"
            ],
            "planned_setup_then_trajectory_pass_count": v114["summary"][
                "planned_setup_then_trajectory_pass_count"
            ],
        },
        "strict_thresholds": strict_thresholds,
        "probe_parameters": {
            "qdot_limit_rad_s": float(qdot_limit_rad_s),
            "qdot_utilization_target": float(qdot_utilization_target),
            "terminal_source": "v56 contact-manifold gate cases",
            "path_source": "qdot-timed straight joint path to each terminal candidate plus v62 diagnostic path reference",
            "trajectory_stage": "not_run",
        },
        "summary": summary,
        "constraint_rows": rows,
        "claim_boundary": {
            "offline_simulation_only": True,
            "explicit_stage_a_constraint_probe_complete": False,
            "strict_paper_equivalent_feasibility": False,
            "canonical_controller_change": False,
            "canonical_orientation_gate_change": False,
            "failed_cell_closed": False,
            "robustness_claim": False,
            "contact_calibration_claim": False,
            "hardware_readiness": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "do_not_mark_goal_complete": True,
        },
        "next_offline_actions": [
            "Do not claim strict setup from qdot-timed terminal paths; terminal compatibility remains unsolved.",
            "The diagnostic path shows qdot saturation can be removed, but it still fails the strict terminal x/y/orientation gate.",
            "Further strict-feasibility work likely needs a changed setup target/contact model supported by approved calibration evidence, or a formal constrained optimization that proves compatibility under accepted gates.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Explicit Stage A Constraint Probe Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case count: `{summary['case_count']}`",
        f"- Strict setup-path pass count: `{summary['strict_setup_path_pass_count']} / {summary['case_count']}`",
        f"- Terminal strict-criteria pass count: `{summary['terminal_strict_criteria_pass_count']} / {summary['case_count']}`",
        f"- Qdot-criteria pass count: `{summary['qdot_criteria_pass_count']} / {summary['case_count']}`",
        f"- Planned setup-then-trajectory pass count: `{summary['planned_setup_then_trajectory_pass_count']} / {summary['case_count']}`",
        f"- Best score case: `{summary['best_score_case_id']}`",
        f"- Best qdot case: `{summary['best_qdot_case_id']}`",
        f"- Best x/y case: `{summary['best_xy_case_id']}`",
        f"- Best orientation case: `{summary['best_orientation_case_id']}`",
        "",
        "| case | setup path pass | failed criteria | qdot sat | tail qdot util | terminal xy m | terminal orient rad | terminal force N | contact frac |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["constraint_rows"]:
        gate = row["strict_setup_path_gate"]
        criteria = ";".join(gate["failed_criteria"]) or "none"
        lines.append(
            "| `{case}` | `{passed}` | `{criteria}` | `{qdot}` | `{tail}` | `{xy}` | `{orient}` | `{force}` | `{contact}` |".format(
                case=row["case_id"],
                passed=gate["passed"],
                criteria=criteria,
                qdot=gate["criteria"]["setup_qdot_saturation_fraction"]["actual"],
                tail=gate["criteria"]["setup_tail_max_qdot_utilization"]["actual"],
                xy=row["path_summary"]["terminal_tangential_error_m"],
                orient=row["path_summary"]["terminal_orientation_error_rad"],
                force=row["path_summary"]["terminal_force_error_N"],
                contact=row["path_summary"]["target_contact_present_fraction"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- Qdot-timed paths can remove the v113/v114 setup qdot-saturation failure in all tested rows.",
            "- Removing qdot saturation does not solve the strict terminal compatibility problem.",
            "- The x/y plus orientation terminal row loses target contact and force; the force plus orientation row drifts in x/y.",
            "- The best soft strict terminal compromise still fails strict x/y and orientation.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--acceptance", default=DEFAULT_ACCEPTANCE)
    parser.add_argument("--contact-manifold-metrics", default=DEFAULT_CONTACT_MANIFOLD)
    parser.add_argument("--stage-a-tracking-metrics", default=DEFAULT_STAGE_A_TRACKING)
    parser.add_argument("--remaining-blockers", default=DEFAULT_REMAINING_BLOCKERS)
    parser.add_argument("--v113-metrics", default=DEFAULT_V113)
    parser.add_argument("--v114-metrics", default=DEFAULT_V114)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--qdot-limit-rad-s", type=float, default=0.15)
    parser.add_argument("--qdot-utilization-target", type=float, default=0.95)
    args = parser.parse_args()

    if not 0.0 < float(args.qdot_utilization_target) < 0.98:
        raise ValueError("qdot-utilization-target must be between 0 and 0.98")

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "explicit_stage_a_constraint_probe" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(
        config_path=(ROOT / args.config).resolve(),
        acceptance_path=(ROOT / args.acceptance).resolve(),
        contact_manifold_path=(ROOT / args.contact_manifold_metrics).resolve(),
        stage_a_tracking_path=(ROOT / args.stage_a_tracking_metrics).resolve(),
        remaining_blockers_path=(ROOT / args.remaining_blockers).resolve(),
        v113_metrics_path=(ROOT / args.v113_metrics).resolve(),
        v114_metrics_path=(ROOT / args.v114_metrics).resolve(),
        qdot_limit_rad_s=float(args.qdot_limit_rad_s),
        qdot_utilization_target=float(args.qdot_utilization_target),
    )
    payload["run_id"] = run_id
    payload["output_dir"] = str(out_dir)

    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.dump(payload, f, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
