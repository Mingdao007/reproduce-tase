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
DEFAULT_V113 = "runs/strict_feasibility_policy_probe/20260525T073519/metrics.yaml"
DEFAULT_REMAINING_BLOCKERS = "runs/remaining_blocker_prioritization/20260525T072557/metrics.yaml"


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


@dataclass(frozen=True)
class CommandLimitedCase:
    case_id: str
    approach_duration_s: float
    recenter_duration_s: float
    settle_duration_s: float
    force_gain: float
    planar_kp: float
    recenter_planar_kp: float | None
    settle_planar_kp: float | None
    approach_qdot_limit_rad_s: float
    recenter_qdot_limit_rad_s: float
    settle_qdot_limit_rad_s: float
    trajectory_qdot_limit_rad_s: float
    approach_max_angular_command_rad_s: float | None
    recenter_max_angular_command_rad_s: float | None
    settle_max_angular_command_rad_s: float | None
    recenter_mode: str = "linear_primary"
    settle_mode: str = "weighted"
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


def command_limited_cases() -> list[CommandLimitedCase]:
    return [
        CommandLimitedCase(
            case_id="v113_reference_uncapped",
            approach_duration_s=4.0,
            recenter_duration_s=4.0,
            settle_duration_s=2.0,
            force_gain=5e-4,
            planar_kp=0.5,
            recenter_planar_kp=None,
            settle_planar_kp=None,
            approach_qdot_limit_rad_s=0.25,
            recenter_qdot_limit_rad_s=0.15,
            settle_qdot_limit_rad_s=0.15,
            trajectory_qdot_limit_rad_s=0.15,
            approach_max_angular_command_rad_s=None,
            recenter_max_angular_command_rad_s=None,
            settle_max_angular_command_rad_s=None,
            note="v113-like uncapped command reference",
        ),
        CommandLimitedCase(
            case_id="strict_qdot_uncapped_reference",
            approach_duration_s=4.0,
            recenter_duration_s=4.0,
            settle_duration_s=2.0,
            force_gain=5e-4,
            planar_kp=0.5,
            recenter_planar_kp=None,
            settle_planar_kp=None,
            approach_qdot_limit_rad_s=0.15,
            recenter_qdot_limit_rad_s=0.15,
            settle_qdot_limit_rad_s=0.15,
            trajectory_qdot_limit_rad_s=0.15,
            approach_max_angular_command_rad_s=None,
            recenter_max_angular_command_rad_s=None,
            settle_max_angular_command_rad_s=None,
            note="same command law with strict setup qdot cap in all Stage A phases",
        ),
        CommandLimitedCase(
            case_id="angular_cap_0p02_low_force_longer",
            approach_duration_s=12.0,
            recenter_duration_s=8.0,
            settle_duration_s=8.0,
            force_gain=1e-4,
            planar_kp=0.5,
            recenter_planar_kp=None,
            settle_planar_kp=None,
            approach_qdot_limit_rad_s=0.15,
            recenter_qdot_limit_rad_s=0.15,
            settle_qdot_limit_rad_s=0.15,
            trajectory_qdot_limit_rad_s=0.15,
            approach_max_angular_command_rad_s=0.02,
            recenter_max_angular_command_rad_s=0.02,
            settle_max_angular_command_rad_s=0.02,
            note="command-limited orientation plus lower normal-force gain",
        ),
        CommandLimitedCase(
            case_id="angular_cap_0p01_low_planar_slow",
            approach_duration_s=20.0,
            recenter_duration_s=12.0,
            settle_duration_s=12.0,
            force_gain=5e-5,
            planar_kp=0.1,
            recenter_planar_kp=0.1,
            settle_planar_kp=0.1,
            approach_qdot_limit_rad_s=0.15,
            recenter_qdot_limit_rad_s=0.15,
            settle_qdot_limit_rad_s=0.15,
            trajectory_qdot_limit_rad_s=0.15,
            approach_max_angular_command_rad_s=0.01,
            recenter_max_angular_command_rad_s=0.01,
            settle_max_angular_command_rad_s=0.01,
            note="slower command-limited Stage A with reduced planar feedback",
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


def max_setup_metric(phases: list[dict[str, Any]], key: str) -> float:
    return float(max(phase["summary"][key] for phase in phases))


def criterion_leq(actual: float, threshold: float) -> dict[str, Any]:
    return {
        "actual": float(actual),
        "operator": "<=",
        "threshold": float(threshold),
        "passed": float(actual) <= float(threshold),
        "ratio": None if threshold == 0.0 else float(actual) / float(threshold),
    }


def criterion_geq(actual: float, threshold: float) -> dict[str, Any]:
    return {
        "actual": float(actual),
        "operator": ">=",
        "threshold": float(threshold),
        "passed": float(actual) >= float(threshold),
        "ratio": None if threshold == 0.0 else float(actual) / float(threshold),
    }


def strict_setup_chain_gate(
    *,
    final_orientation_error_rad: float,
    final_tangential_error_m: float,
    setup_phases: list[dict[str, Any]],
    strict_thresholds: dict[str, Any],
    feasibility_thresholds: FeasibilityThresholds,
) -> dict[str, Any]:
    terminal = setup_phases[-1]["summary"]
    criteria = {
        "final_orientation_error_rad": criterion_leq(
            final_orientation_error_rad,
            strict_thresholds["max_final_orientation_error_rad"],
        ),
        "final_tangential_position_error_m": criterion_leq(
            final_tangential_error_m,
            strict_thresholds["max_final_tangential_error_m"],
        ),
        "terminal_tail_mean_abs_force_error_N": criterion_leq(
            terminal["tail_mean_abs_force_error_N"],
            strict_thresholds["max_tail_mean_abs_force_error_N"],
        ),
        "setup_min_contact_present_fraction": criterion_geq(
            min(float(phase["summary"]["contact_present_fraction"]) for phase in setup_phases),
            feasibility_thresholds.contact_present_fraction_min,
        ),
        "setup_max_qdot_saturation_fraction": criterion_leq(
            max_setup_metric(setup_phases, "qdot_saturation_fraction"),
            strict_thresholds["qdot_saturation_fraction_max"],
        ),
        "setup_max_tail_qdot_utilization": criterion_leq(
            max_setup_metric(setup_phases, "tail_max_qdot_utilization"),
            feasibility_thresholds.tail_max_qdot_utilization_max,
        ),
        "setup_max_qdot_violation_rad_s": criterion_leq(
            max_setup_metric(setup_phases, "max_qdot_violation_rad_s"),
            feasibility_thresholds.max_qdot_violation_rad_s_max,
        ),
        "setup_max_joint_limit_violation_rad": criterion_leq(
            max_setup_metric(setup_phases, "max_joint_limit_violation_rad"),
            feasibility_thresholds.max_joint_limit_violation_rad_max,
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


def run_case(
    case: CommandLimitedCase,
    *,
    model_path: pathlib.Path,
    q_min: np.ndarray,
    q_max: np.ndarray,
    strict_thresholds: dict[str, Any],
    dt_s: float,
) -> dict[str, Any]:
    target_force_N = 5.0
    initial_q = parse_vector("0,-0.1,0.15,-0.05,0,0")
    thresholds = FeasibilityThresholds(
        max_orientation_error_rad_max=strict_thresholds["max_final_orientation_error_rad"],
        max_angular_velocity_slack_rad_s_max=0.03,
    )
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
        approach_duration_s=case.approach_duration_s,
        recenter_duration_s=case.recenter_duration_s,
        settle_duration_s=case.settle_duration_s,
        trajectory_duration_s=8.0,
        dt_s=dt_s,
        qdot_min=np.full(len(initial_q), -case.approach_qdot_limit_rad_s, dtype=float),
        qdot_max=np.full(len(initial_q), case.approach_qdot_limit_rad_s, dtype=float),
        recenter_qdot_min=np.full(len(initial_q), -case.recenter_qdot_limit_rad_s, dtype=float),
        recenter_qdot_max=np.full(len(initial_q), case.recenter_qdot_limit_rad_s, dtype=float),
        settle_qdot_min=np.full(len(initial_q), -case.settle_qdot_limit_rad_s, dtype=float),
        settle_qdot_max=np.full(len(initial_q), case.settle_qdot_limit_rad_s, dtype=float),
        trajectory_qdot_min=np.full(len(initial_q), -case.trajectory_qdot_limit_rad_s, dtype=float),
        trajectory_qdot_max=np.full(len(initial_q), case.trajectory_qdot_limit_rad_s, dtype=float),
        force_gain=case.force_gain,
        r=0.5,
        planar_kp=case.planar_kp,
        recenter_planar_kp=case.recenter_planar_kp,
        settle_planar_kp=case.settle_planar_kp,
        axis_weights=np.ones(3, dtype=float),
        slack_axis_weights=np.asarray([1.0, 1.0, 10000.0], dtype=float),
        slack_constraint_weight=1000.0,
        normal_velocity_mode="contact_normal",
        approach_orientation_priority_mode="weighted",
        approach_orientation_kp=2.0,
        approach_max_angular_command_rad_s=case.approach_max_angular_command_rad_s,
        recenter_orientation_priority_mode=case.recenter_mode,
        recenter_max_angular_command_rad_s=case.recenter_max_angular_command_rad_s,
        settle_orientation_priority_mode=case.settle_mode,
        settle_max_angular_command_rad_s=case.settle_max_angular_command_rad_s,
        trajectory_orientation_priority_mode="linear_primary",
        trajectory_orientation_kp=0.1,
        angular_axis_weights=np.ones(3, dtype=float),
        angular_slack_axis_weights=np.ones(3, dtype=float),
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
        qdot_limit_rad_s=case.approach_qdot_limit_rad_s,
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
        qdot_limit_rad_s=case.trajectory_qdot_limit_rad_s,
        thresholds=thresholds,
    )
    assert approach is not None
    assert trajectory is not None
    setup_phases = [phase for phase in [approach, recenter, settle] if phase is not None]
    gate = strict_setup_chain_gate(
        final_orientation_error_rad=staged.setup_final_orientation_error_rad,
        final_tangential_error_m=staged.setup_final_tangential_position_error_m,
        setup_phases=setup_phases,
        strict_thresholds=strict_thresholds,
        feasibility_thresholds=thresholds,
    )
    trajectory_pass = bool(trajectory["feasibility_gate"]["feasibility_pass"])
    row = {
        "case_id": case.case_id,
        "parameters": asdict(case),
        "setup_final_orientation_error_rad": float(staged.setup_final_orientation_error_rad),
        "setup_final_tangential_position_error_m": float(staged.setup_final_tangential_position_error_m),
        "strict_setup_chain_gate": gate,
        "strict_setup_violation_score": violation_score(gate),
        "trajectory_feasibility_gate": trajectory["feasibility_gate"],
        "trajectory_max_orientation_error_rad": trajectory["summary"]["max_orientation_error_rad"],
        "trajectory_tail_mean_abs_force_error_N": trajectory["summary"]["tail_mean_abs_force_error_N"],
        "planned_setup_then_trajectory_pass": bool(gate["passed"] and trajectory_pass),
        "phase_summaries": {
            "approach": approach["summary"],
            "recenter": None if recenter is None else recenter["summary"],
            "settle": None if settle is None else settle["summary"],
            "trajectory": trajectory["summary"],
        },
    }
    return row


def failure_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        for criterion in row["strict_setup_chain_gate"]["failed_criteria"]:
            counts[criterion] = counts.get(criterion, 0) + 1
    return dict(sorted(counts.items()))


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    best_score = min(rows, key=lambda row: row["strict_setup_violation_score"])
    best_qdot = min(
        rows,
        key=lambda row: row["strict_setup_chain_gate"]["criteria"][
            "setup_max_qdot_saturation_fraction"
        ]["actual"],
    )
    best_xy = min(
        rows,
        key=lambda row: row["strict_setup_chain_gate"]["criteria"][
            "final_tangential_position_error_m"
        ]["actual"],
    )
    best_orientation = min(
        rows,
        key=lambda row: row["strict_setup_chain_gate"]["criteria"][
            "final_orientation_error_rad"
        ]["actual"],
    )
    return {
        "case_count": len(rows),
        "strict_setup_chain_pass_count": sum(
            1 for row in rows if row["strict_setup_chain_gate"]["passed"]
        ),
        "trajectory_feasibility_pass_count": sum(
            1 for row in rows if row["trajectory_feasibility_gate"]["feasibility_pass"]
        ),
        "planned_setup_then_trajectory_pass_count": sum(
            1 for row in rows if row["planned_setup_then_trajectory_pass"]
        ),
        "setup_failed_criteria_counts": failure_counts(rows),
        "best_score_case_id": best_score["case_id"],
        "best_score": best_score["strict_setup_violation_score"],
        "best_qdot_case_id": best_qdot["case_id"],
        "best_qdot_saturation_fraction": best_qdot["strict_setup_chain_gate"][
            "criteria"
        ]["setup_max_qdot_saturation_fraction"]["actual"],
        "best_xy_case_id": best_xy["case_id"],
        "best_xy_error_m": best_xy["setup_final_tangential_position_error_m"],
        "best_orientation_case_id": best_orientation["case_id"],
        "best_orientation_error_rad": best_orientation["setup_final_orientation_error_rad"],
        "strict_command_limited_stage_a_complete": False,
        "strict_paper_equivalent_feasibility": False,
    }


def build_payload(
    *,
    config_path: pathlib.Path,
    acceptance_path: pathlib.Path,
    v113_metrics_path: pathlib.Path,
    remaining_blockers_path: pathlib.Path,
    dt_s: float,
) -> dict[str, Any]:
    config = load_yaml(config_path)
    acceptance = load_yaml(acceptance_path)
    v113 = load_yaml(v113_metrics_path)
    remaining = load_yaml(remaining_blockers_path)
    model_path = (ROOT / config["ur10e_mujoco"]["mjcf_path"]).resolve()
    model = load_model(model_path)
    q_min, q_max = joint_ranges(model)
    strict_thresholds = acceptance["strict_setup_terminal_gate"]
    rows = [
        run_case(
            case,
            model_path=model_path,
            q_min=q_min,
            q_max=q_max,
            strict_thresholds=strict_thresholds,
            dt_s=dt_s,
        )
        for case in command_limited_cases()
    ]
    summary = summarize_rows(rows)
    return {
        "run_source": "v114 strict command-limited Stage A probe",
        "source_files": {
            "config": str(config_path),
            "acceptance": str(acceptance_path),
            "v113_policy_probe": str(v113_metrics_path),
            "remaining_blockers": str(remaining_blockers_path),
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
        "v112_priority_context": {
            "top_priority_blocker_id": remaining["summary"]["top_priority_blocker_id"],
            "offline_actionable_blocker_ids": remaining["summary"][
                "offline_actionable_blocker_ids"
            ],
        },
        "strict_thresholds": strict_thresholds,
        "probe_parameters": {
            "trajectory": "e2-figure-eight",
            "paper_time_scale": 0.075,
            "dt_s": float(dt_s),
            "command_generation_change": (
                "finite-time normal-force gain and force-normal angular commands are capped before "
                "the velocity allocation solve"
            ),
        },
        "summary": summary,
        "command_limited_rows": rows,
        "claim_boundary": {
            "offline_simulation_only": True,
            "strict_command_limited_stage_a_complete": False,
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
            "Do not claim strict feasibility from command limiting.",
            "Command limiting alone still does not produce a strict setup chain pass.",
            "Future Stage A work needs either an explicit path/terminal constraint formulation or a model change supported by calibrated contact evidence.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Strict Command-Limited Stage A Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case count: `{summary['case_count']}`",
        f"- Strict setup-chain pass count: `{summary['strict_setup_chain_pass_count']} / {summary['case_count']}`",
        f"- Trajectory feasibility pass count: `{summary['trajectory_feasibility_pass_count']} / {summary['case_count']}`",
        f"- Planned setup-then-trajectory pass count: `{summary['planned_setup_then_trajectory_pass_count']} / {summary['case_count']}`",
        f"- Best score case: `{summary['best_score_case_id']}`",
        f"- Best qdot-saturation case: `{summary['best_qdot_case_id']}`",
        f"- Best x/y case: `{summary['best_xy_case_id']}`",
        f"- Best orientation case: `{summary['best_orientation_case_id']}`",
        "",
        "| case | setup chain pass | failed criteria | setup max qdot sat | setup orientation rad | setup x/y m | trajectory pass |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in payload["command_limited_rows"]:
        gate = row["strict_setup_chain_gate"]
        criteria = ";".join(gate["failed_criteria"]) or "none"
        lines.append(
            "| `{case}` | `{passed}` | `{criteria}` | `{qdot}` | `{orient}` | `{xy}` | `{traj}` |".format(
                case=row["case_id"],
                passed=gate["passed"],
                criteria=criteria,
                qdot=gate["criteria"]["setup_max_qdot_saturation_fraction"]["actual"],
                orient=row["setup_final_orientation_error_rad"],
                xy=row["setup_final_tangential_position_error_m"],
                traj=row["trajectory_feasibility_gate"]["feasibility_pass"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- Command limiting changes Stage A command generation before allocation, but no tested row satisfies the strict setup chain.",
            "- Lower force gain and angular caps reduce some terminal force/orientation pressure but do not recover x/y recentering.",
            "- The best qdot-saturation row still saturates far above the strict `0.01` fraction threshold.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--acceptance", default=DEFAULT_ACCEPTANCE)
    parser.add_argument("--v113-metrics", default=DEFAULT_V113)
    parser.add_argument("--remaining-blockers", default=DEFAULT_REMAINING_BLOCKERS)
    parser.add_argument("--dt-s", type=float, default=0.01)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "strict_command_limited_stage_a" / run_id
    )
    if out_dir.exists():
        raise FileExistsError(out_dir)
    out_dir.mkdir(parents=True)
    payload = build_payload(
        config_path=(ROOT / args.config).resolve(),
        acceptance_path=(ROOT / args.acceptance).resolve(),
        v113_metrics_path=(ROOT / args.v113_metrics).resolve(),
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
