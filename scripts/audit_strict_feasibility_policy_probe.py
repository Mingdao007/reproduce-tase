#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.feasibility import FeasibilityThresholds, evaluate_force_motion_feasibility
from tase_repro.force_feedback import ForceMotionResult, summarize_force_motion
from tase_repro.kinematics import joint_ranges, load_model
from tase_repro.staged_force_motion import simulate_orientation_prealign_then_planar_force_motion
from tase_repro.trajectories import paper_e2_figure_eight_planar_state


DEFAULT_CONFIG = "configs/mujoco_ur10e_tilted_plane.yaml"
DEFAULT_ACCEPTANCE = "configs/ur10e_adapted_acceptance.yaml"
DEFAULT_STRICT_BLOCKERS = "runs/strict_feasibility_blockers/20260525T051640/metrics.yaml"
DEFAULT_REMAINING_BLOCKERS = "runs/remaining_blocker_prioritization/20260525T072557/metrics.yaml"


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


@dataclass(frozen=True)
class PolicyCase:
    case_id: str
    recenter_duration_s: float
    settle_duration_s: float
    recenter_mode: str
    settle_mode: str
    recenter_planar_kp: float | None = None
    settle_planar_kp: float | None = None
    planar_axis_weight: float = 1.0
    normal_axis_weight: float = 1.0
    angular_axis_weight: float = 1.0
    recenter_qdot_limit_rad_s: float = 0.15
    settle_qdot_limit_rad_s: float = 0.15
    note: str = ""


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_vector(text: str) -> np.ndarray:
    return np.asarray([float(part.strip()) for part in text.split(",")], dtype=float)


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


def strict_policy_cases() -> list[PolicyCase]:
    return [
        PolicyCase(
            case_id="baseline_no_recenter",
            recenter_duration_s=0.0,
            settle_duration_s=0.0,
            recenter_mode="linear_primary",
            settle_mode="weighted",
            note="v36 reference: orientation/trajectory pass, x/y setup drift fails",
        ),
        PolicyCase(
            case_id="linear_recenter_4_no_settle",
            recenter_duration_s=4.0,
            settle_duration_s=0.0,
            recenter_mode="linear_primary",
            settle_mode="weighted",
            note="v36 reference: x/y recentered, orientation fails",
        ),
        PolicyCase(
            case_id="linear_recenter_4_weighted_settle_1",
            recenter_duration_s=4.0,
            settle_duration_s=1.0,
            recenter_mode="linear_primary",
            settle_mode="weighted",
            note="v36 reference: weighted settle restores orientation but gives back x/y",
        ),
        PolicyCase(
            case_id="linear_recenter_4_weighted_settle_2",
            recenter_duration_s=4.0,
            settle_duration_s=2.0,
            recenter_mode="linear_primary",
            settle_mode="weighted",
            note="v36 reference: longer weighted settle keeps orientation but x/y fails",
        ),
        PolicyCase(
            case_id="linear_recenter_4_linear_settle_4",
            recenter_duration_s=4.0,
            settle_duration_s=4.0,
            recenter_mode="linear_primary",
            settle_mode="linear_primary",
            note="v36 reference: x/y pass, orientation and trajectory fail",
        ),
        PolicyCase(
            case_id="weighted_recenter_4_weighted_settle_2",
            recenter_duration_s=4.0,
            settle_duration_s=2.0,
            recenter_mode="weighted",
            settle_mode="weighted",
            note="new v113 blended-priority recenter and settle",
        ),
        PolicyCase(
            case_id="weighted_recenter_high_planar_kp_4_2",
            recenter_duration_s=4.0,
            settle_duration_s=2.0,
            recenter_mode="weighted",
            settle_mode="weighted",
            recenter_planar_kp=4.0,
            settle_planar_kp=4.0,
            note="new v113 weighted recenter/settle with higher planar feedback",
        ),
        PolicyCase(
            case_id="linear_recenter_weighted_settle_high_planar_kp",
            recenter_duration_s=4.0,
            settle_duration_s=2.0,
            recenter_mode="linear_primary",
            settle_mode="weighted",
            settle_planar_kp=20.0,
            note="new v113 weighted settle with aggressive x/y retention",
        ),
    ]


def phase_summary(
    result: ForceMotionResult | None,
    *,
    target_force_N: float,
    q_min: np.ndarray,
    q_max: np.ndarray,
    qdot_limit_rad_s: float,
    thresholds: FeasibilityThresholds,
) -> dict[str, Any] | None:
    if result is None:
        return None
    qdot_min = np.full(result.qdot.shape[1], -abs(float(qdot_limit_rad_s)), dtype=float)
    qdot_max = np.full(result.qdot.shape[1], abs(float(qdot_limit_rad_s)), dtype=float)
    summary = summarize_force_motion(
        result,
        target_force_N=target_force_N,
        q_min=q_min,
        q_max=q_max,
        qdot_min=qdot_min,
        qdot_max=qdot_max,
    )
    gate = evaluate_force_motion_feasibility(
        summary,
        thresholds=thresholds,
        qdot_abs_limit_rad_s=qdot_limit_rad_s,
    )
    return {
        "summary": summary,
        "feasibility_gate": gate,
    }


def criterion_leq(name: str, actual: float, threshold: float) -> dict[str, Any]:
    return {
        "actual": float(actual),
        "operator": "<=",
        "threshold": float(threshold),
        "passed": float(actual) <= float(threshold),
        "ratio": None if threshold == 0.0 else float(actual) / float(threshold),
    }


def criterion_geq(name: str, actual: float, threshold: float) -> dict[str, Any]:
    return {
        "actual": float(actual),
        "operator": ">=",
        "threshold": float(threshold),
        "passed": float(actual) >= float(threshold),
        "ratio": None if threshold == 0.0 else float(actual) / float(threshold),
    }


def setup_terminal_gate(
    *,
    final_orientation_error_rad: float,
    final_tangential_error_m: float,
    setup_phase_summary: dict[str, Any],
    strict_thresholds: dict[str, Any],
    feasibility_thresholds: FeasibilityThresholds,
) -> dict[str, Any]:
    summary = setup_phase_summary["summary"]
    criteria = {
        "final_orientation_error_rad": criterion_leq(
            "final_orientation_error_rad",
            final_orientation_error_rad,
            strict_thresholds["max_final_orientation_error_rad"],
        ),
        "final_tangential_position_error_m": criterion_leq(
            "final_tangential_position_error_m",
            final_tangential_error_m,
            strict_thresholds["max_final_tangential_error_m"],
        ),
        "contact_present_fraction": criterion_geq(
            "contact_present_fraction",
            summary["contact_present_fraction"],
            feasibility_thresholds.contact_present_fraction_min,
        ),
        "tail_mean_abs_force_error_N": criterion_leq(
            "tail_mean_abs_force_error_N",
            summary["tail_mean_abs_force_error_N"],
            strict_thresholds["max_tail_mean_abs_force_error_N"],
        ),
        "qdot_saturation_fraction": criterion_leq(
            "qdot_saturation_fraction",
            summary["qdot_saturation_fraction"],
            strict_thresholds["qdot_saturation_fraction_max"],
        ),
        "tail_max_qdot_utilization": criterion_leq(
            "tail_max_qdot_utilization",
            summary["tail_max_qdot_utilization"],
            feasibility_thresholds.tail_max_qdot_utilization_max,
        ),
        "max_qdot_violation_rad_s": criterion_leq(
            "max_qdot_violation_rad_s",
            summary["max_qdot_violation_rad_s"],
            feasibility_thresholds.max_qdot_violation_rad_s_max,
        ),
        "max_joint_limit_violation_rad": criterion_leq(
            "max_joint_limit_violation_rad",
            summary["max_joint_limit_violation_rad"],
            feasibility_thresholds.max_joint_limit_violation_rad_max,
        ),
    }
    failed = [name for name, criterion in criteria.items() if not bool(criterion["passed"])]
    return {
        "passed": not failed,
        "failed_criteria": failed,
        "criteria": criteria,
    }


def setup_violation_score(gate: dict[str, Any]) -> float:
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


def failure_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        for criterion in row["setup_terminal_state_gate"]["failed_criteria"]:
            counts[criterion] = counts.get(criterion, 0) + 1
    return dict(sorted(counts.items()))


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    best_setup = min(rows, key=lambda row: row["setup_violation_score"])
    best_tangential = min(
        rows,
        key=lambda row: row["setup_terminal_state_gate"]["criteria"][
            "final_tangential_position_error_m"
        ]["actual"],
    )
    best_orientation = min(
        rows,
        key=lambda row: row["setup_terminal_state_gate"]["criteria"][
            "final_orientation_error_rad"
        ]["actual"],
    )
    return {
        "case_count": len(rows),
        "setup_terminal_state_pass_count": sum(
            1 for row in rows if row["setup_terminal_state_gate"]["passed"]
        ),
        "trajectory_feasibility_pass_count": sum(
            1 for row in rows if row["trajectory_feasibility_gate"]["feasibility_pass"]
        ),
        "planned_setup_then_trajectory_pass_count": sum(
            1 for row in rows if row["planned_setup_then_trajectory_pass"]
        ),
        "full_staged_feasibility_pass_count": sum(
            1 for row in rows if row["full_staged_feasibility_pass"]
        ),
        "setup_failed_criteria_counts": failure_counts(rows),
        "best_setup_score_case_id": best_setup["case_id"],
        "best_setup_violation_score": best_setup["setup_violation_score"],
        "best_tangential_case_id": best_tangential["case_id"],
        "best_tangential_error_m": best_tangential["setup_terminal_state_gate"][
            "criteria"
        ]["final_tangential_position_error_m"]["actual"],
        "best_orientation_case_id": best_orientation["case_id"],
        "best_orientation_error_rad": best_orientation["setup_terminal_state_gate"][
            "criteria"
        ]["final_orientation_error_rad"]["actual"],
        "strict_policy_probe_complete": False,
        "strict_paper_equivalent_feasibility": False,
    }


def run_policy_case(
    case: PolicyCase,
    *,
    model_path: pathlib.Path,
    q_min: np.ndarray,
    q_max: np.ndarray,
    strict_thresholds: dict[str, Any],
    dt_s: float,
) -> dict[str, Any]:
    target_force_N = 5.0
    qdot_limit = 0.15
    approach_qdot_limit = 0.25
    trajectory_qdot_limit = 0.15
    thresholds = FeasibilityThresholds(
        max_orientation_error_rad_max=strict_thresholds["max_final_orientation_error_rad"],
        max_angular_velocity_slack_rad_s_max=0.03,
    )
    initial_q = parse_vector("0,-0.1,0.15,-0.05,0,0")
    approach_qdot_min = np.full(len(initial_q), -approach_qdot_limit, dtype=float)
    approach_qdot_max = np.full(len(initial_q), approach_qdot_limit, dtype=float)
    recenter_qdot_min = np.full(len(initial_q), -case.recenter_qdot_limit_rad_s, dtype=float)
    recenter_qdot_max = np.full(len(initial_q), case.recenter_qdot_limit_rad_s, dtype=float)
    settle_qdot_min = np.full(len(initial_q), -case.settle_qdot_limit_rad_s, dtype=float)
    settle_qdot_max = np.full(len(initial_q), case.settle_qdot_limit_rad_s, dtype=float)
    trajectory_qdot_min = np.full(len(initial_q), -trajectory_qdot_limit, dtype=float)
    trajectory_qdot_max = np.full(len(initial_q), trajectory_qdot_limit, dtype=float)

    staged = simulate_orientation_prealign_then_planar_force_motion(
        model_path,
        initial_q=initial_q,
        base_z_offset_m=-0.0011631221220595766,
        target_force_N=target_force_N,
        planar_trajectory=lambda t_s: paper_e2_figure_eight_planar_state(
            t_s,
            amplitude_x_m=0.04,
            amplitude_y_m=0.01,
            omega_rad_s=0.1,
            time_scale=0.075,
        ),
        approach_duration_s=4.0,
        recenter_duration_s=case.recenter_duration_s,
        settle_duration_s=case.settle_duration_s,
        trajectory_duration_s=8.0,
        dt_s=dt_s,
        qdot_min=approach_qdot_min,
        qdot_max=approach_qdot_max,
        recenter_qdot_min=recenter_qdot_min,
        recenter_qdot_max=recenter_qdot_max,
        settle_qdot_min=settle_qdot_min,
        settle_qdot_max=settle_qdot_max,
        trajectory_qdot_min=trajectory_qdot_min,
        trajectory_qdot_max=trajectory_qdot_max,
        force_gain=5e-4,
        r=0.5,
        recenter_planar_kp=case.recenter_planar_kp,
        settle_planar_kp=case.settle_planar_kp,
        axis_weights=np.asarray(
            [case.planar_axis_weight, case.planar_axis_weight, case.normal_axis_weight],
            dtype=float,
        ),
        slack_axis_weights=np.asarray([1.0, 1.0, 10000.0], dtype=float),
        slack_constraint_weight=1000.0,
        normal_velocity_mode="contact_normal",
        approach_orientation_priority_mode="weighted",
        approach_orientation_kp=2.0,
        recenter_orientation_priority_mode=case.recenter_mode,
        settle_orientation_priority_mode=case.settle_mode,
        trajectory_orientation_priority_mode="linear_primary",
        trajectory_orientation_kp=0.1,
        angular_axis_weights=np.asarray(
            [case.angular_axis_weight, case.angular_axis_weight, case.angular_axis_weight],
            dtype=float,
        ),
        angular_slack_axis_weights=np.asarray([1.0, 1.0, 1.0], dtype=float),
        trajectory_joint_posture_target=initial_q,
        trajectory_joint_posture_kp=1.0,
        trajectory_joint_posture_weight=0.001,
        trajectory_max_joint_posture_velocity_rad_s=0.05,
        approach_orientation_threshold_rad=strict_thresholds["max_final_orientation_error_rad"],
    )
    approach = phase_summary(
        staged.approach,
        target_force_N=target_force_N,
        q_min=q_min,
        q_max=q_max,
        qdot_limit_rad_s=approach_qdot_limit,
        thresholds=thresholds,
    )
    recenter = phase_summary(
        staged.approach_recenter,
        target_force_N=target_force_N,
        q_min=q_min,
        q_max=q_max,
        qdot_limit_rad_s=case.recenter_qdot_limit_rad_s,
        thresholds=thresholds,
    )
    settle = phase_summary(
        staged.approach_settle,
        target_force_N=target_force_N,
        q_min=q_min,
        q_max=q_max,
        qdot_limit_rad_s=case.settle_qdot_limit_rad_s,
        thresholds=thresholds,
    )
    trajectory = phase_summary(
        staged.trajectory,
        target_force_N=target_force_N,
        q_min=q_min,
        q_max=q_max,
        qdot_limit_rad_s=trajectory_qdot_limit,
        thresholds=thresholds,
    )
    setup_phase = settle or recenter or approach
    assert approach is not None
    assert trajectory is not None
    assert setup_phase is not None
    gate = setup_terminal_gate(
        final_orientation_error_rad=staged.setup_final_orientation_error_rad,
        final_tangential_error_m=staged.setup_final_tangential_position_error_m,
        setup_phase_summary=setup_phase,
        strict_thresholds=strict_thresholds,
        feasibility_thresholds=thresholds,
    )
    setup_phase_gate_pass = bool(
        approach["feasibility_gate"]["feasibility_pass"]
        and (recenter is None or recenter["feasibility_gate"]["feasibility_pass"])
        and (settle is None or settle["feasibility_gate"]["feasibility_pass"])
    )
    planned = bool(gate["passed"] and trajectory["feasibility_gate"]["feasibility_pass"])
    full = bool(setup_phase_gate_pass and trajectory["feasibility_gate"]["feasibility_pass"])
    row = {
        "case_id": case.case_id,
        "parameters": asdict(case),
        "setup_final_orientation_error_rad": staged.setup_final_orientation_error_rad,
        "setup_final_tangential_position_error_m": staged.setup_final_tangential_position_error_m,
        "setup_terminal_state_gate": gate,
        "setup_phase_feasibility_pass": setup_phase_gate_pass,
        "trajectory_feasibility_gate": trajectory["feasibility_gate"],
        "trajectory_max_orientation_error_rad": trajectory["summary"]["max_orientation_error_rad"],
        "trajectory_qdot_saturation_fraction": trajectory["summary"]["qdot_saturation_fraction"],
        "planned_setup_then_trajectory_pass": planned,
        "full_staged_feasibility_pass": full,
        "phase_summaries": {
            "approach": approach["summary"],
            "recenter": None if recenter is None else recenter["summary"],
            "settle": None if settle is None else settle["summary"],
            "trajectory": trajectory["summary"],
        },
    }
    row["setup_violation_score"] = setup_violation_score(gate)
    return row


def build_payload(
    *,
    config_path: pathlib.Path,
    acceptance_path: pathlib.Path,
    strict_blockers_path: pathlib.Path,
    remaining_blockers_path: pathlib.Path,
    dt_s: float,
) -> dict[str, Any]:
    config = load_yaml(config_path)
    acceptance = load_yaml(acceptance_path)
    strict_blockers = load_yaml(strict_blockers_path)
    remaining_blockers = load_yaml(remaining_blockers_path)
    model_path = (ROOT / config["ur10e_mujoco"]["mjcf_path"]).resolve()
    model = load_model(model_path)
    q_min, q_max = joint_ranges(model)
    strict_thresholds = acceptance["strict_setup_terminal_gate"]
    rows = [
        run_policy_case(
            case,
            model_path=model_path,
            q_min=q_min,
            q_max=q_max,
            strict_thresholds=strict_thresholds,
            dt_s=dt_s,
        )
        for case in strict_policy_cases()
    ]
    summary = summarize_rows(rows)
    return {
        "run_source": "v113 strict feasibility policy probe",
        "source_files": {
            "config": str(config_path),
            "acceptance": str(acceptance_path),
            "strict_blockers": str(strict_blockers_path),
            "remaining_blockers": str(remaining_blockers_path),
        },
        "model_path": str(model_path),
        "v112_priority_context": {
            "top_priority_blocker_id": remaining_blockers["summary"][
                "top_priority_blocker_id"
            ],
            "offline_actionable_blocker_ids": remaining_blockers["summary"][
                "offline_actionable_blocker_ids"
            ],
        },
        "v96_strict_context": {
            "primary_blocker": strict_blockers["blocker_summary"]["primary_blocker"],
            "strict_full_staged_feasibility_pass_count": strict_blockers[
                "blocker_summary"
            ]["strict_full_staged_feasibility_pass_count"],
            "three_phase_setup_terminal_state_pass_count": strict_blockers[
                "blocker_summary"
            ]["setup_terminal_state_pass_count"],
            "three_phase_trajectory_feasibility_pass_count": strict_blockers[
                "blocker_summary"
            ]["trajectory_feasibility_pass_count"],
        },
        "strict_thresholds": strict_thresholds,
        "probe_parameters": {
            "trajectory": "e2-figure-eight",
            "paper_time_scale": 0.075,
            "dt_s": float(dt_s),
            "approach_duration_s": 4.0,
            "approach_qdot_limit_rad_s": 0.25,
            "trajectory_duration_s": 8.0,
            "trajectory_qdot_limit_rad_s": 0.15,
        },
        "summary": summary,
        "policy_rows": rows,
        "claim_boundary": {
            "post_hoc_or_offline_simulation_only": True,
            "strict_policy_probe_complete": False,
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
            "Do not claim strict feasibility from this compact E2 policy probe.",
            "The next strict-feasibility step needs a formulation that constrains setup x/y while restoring force-normal orientation without qdot saturation.",
            "Keep any future relaxed setup or diagnostic profile separate from paper-equivalent strict feasibility.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Strict Feasibility Policy Probe Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case count: `{summary['case_count']}`",
        f"- Setup terminal-state pass count: `{summary['setup_terminal_state_pass_count']} / {summary['case_count']}`",
        f"- Trajectory feasibility pass count: `{summary['trajectory_feasibility_pass_count']} / {summary['case_count']}`",
        f"- Planned setup-then-trajectory pass count: `{summary['planned_setup_then_trajectory_pass_count']} / {summary['case_count']}`",
        f"- Full staged feasibility pass count: `{summary['full_staged_feasibility_pass_count']} / {summary['case_count']}`",
        f"- Best setup-score case: `{summary['best_setup_score_case_id']}`",
        f"- Best tangential-error case: `{summary['best_tangential_case_id']}`",
        f"- Best orientation-error case: `{summary['best_orientation_case_id']}`",
        "",
        "| case | setup pass | setup failed criteria | setup orientation rad | setup x/y m | setup score | trajectory pass | full pass |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in payload["policy_rows"]:
        criteria = ";".join(row["setup_terminal_state_gate"]["failed_criteria"]) or "none"
        lines.append(
            "| `{case}` | `{setup}` | `{criteria}` | `{orient}` | `{xy}` | `{score}` | `{traj}` | `{full}` |".format(
                case=row["case_id"],
                setup=row["setup_terminal_state_gate"]["passed"],
                criteria=criteria,
                orient=row["setup_final_orientation_error_rad"],
                xy=row["setup_final_tangential_position_error_m"],
                score=row["setup_violation_score"],
                traj=row["trajectory_feasibility_gate"]["feasibility_pass"],
                full=row["full_staged_feasibility_pass"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- No tested Stage A policy satisfies the strict setup terminal-state gate.",
            "- Weighted settling preserves orientation and force but gives back x/y recentering.",
            "- Linear-primary settling preserves x/y but fails orientation and the following E2 trajectory.",
            "- Aggressive planar retention reduces x/y drift but reintroduces orientation, force, and qdot pressure.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--acceptance", default=DEFAULT_ACCEPTANCE)
    parser.add_argument("--strict-blockers", default=DEFAULT_STRICT_BLOCKERS)
    parser.add_argument("--remaining-blockers", default=DEFAULT_REMAINING_BLOCKERS)
    parser.add_argument("--dt-s", type=float, default=0.01)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "strict_feasibility_policy_probe" / run_id
    )
    if out_dir.exists():
        raise FileExistsError(out_dir)
    out_dir.mkdir(parents=True)
    payload = build_payload(
        config_path=(ROOT / args.config).resolve(),
        acceptance_path=(ROOT / args.acceptance).resolve(),
        strict_blockers_path=(ROOT / args.strict_blockers).resolve(),
        remaining_blockers_path=(ROOT / args.remaining_blockers).resolve(),
        dt_s=args.dt_s,
    )
    payload["run_id"] = run_id
    payload["audit_root"] = str(out_dir)
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
