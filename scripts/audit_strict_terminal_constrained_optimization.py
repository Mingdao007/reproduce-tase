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
from scipy.optimize import minimize


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


DEFAULT_CONFIG = "configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml"
DEFAULT_ACCEPTANCE = "configs/ur10e_adapted_acceptance.yaml"
DEFAULT_CONTACT_MANIFOLD = "runs/contact_manifold_gate_audit/20260524T142404/metrics.yaml"
DEFAULT_V115 = "runs/explicit_stage_a_constraint_probe/20260525T082500/metrics.yaml"
DEFAULT_REMAINING_BLOCKERS = "runs/remaining_blocker_prioritization/20260525T072557/metrics.yaml"


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


@dataclass(frozen=True)
class TerminalSeed:
    seed_id: str
    source: str
    q_rad: np.ndarray

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed_id": self.seed_id,
            "source": self.source,
            "q_rad": [float(x) for x in self.q_rad],
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


def strict_terminal_thresholds(acceptance: dict[str, Any]) -> dict[str, float]:
    strict = acceptance["strict_setup_terminal_gate"]
    return {
        "max_force_error_N": float(strict["max_tail_mean_abs_force_error_N"]),
        "max_tangential_error_m": float(strict["max_final_tangential_error_m"]),
        "max_orientation_error_rad": float(strict["max_final_orientation_error_rad"]),
        "min_target_contact_count": 1.0,
        "max_joint_limit_violation_rad": float(strict["max_joint_limit_violation_rad"]),
    }


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


def max_joint_limit_violation(q: np.ndarray, q_min: np.ndarray, q_max: np.ndarray) -> float:
    q_array = np.asarray(q, dtype=float)
    lower = np.maximum(q_min - q_array, 0.0)
    upper = np.maximum(q_array - q_max, 0.0)
    return float(np.max(lower + upper))


def terminal_gate(metrics: dict[str, Any], thresholds: dict[str, float]) -> dict[str, Any]:
    criteria = {
        "force_error_N": criterion_leq(metrics["force_error_N"], thresholds["max_force_error_N"]),
        "tangential_error_m": criterion_leq(
            metrics["tangential_error_m"],
            thresholds["max_tangential_error_m"],
        ),
        "orientation_error_rad": criterion_leq(
            metrics["orientation_error_rad"],
            thresholds["max_orientation_error_rad"],
        ),
        "target_contact_count": criterion_geq(
            metrics["target_contact_count"],
            thresholds["min_target_contact_count"],
        ),
        "joint_limit_violation_rad": criterion_leq(
            metrics["joint_limit_violation_rad"],
            thresholds["max_joint_limit_violation_rad"],
        ),
    }
    failed = [name for name, criterion in criteria.items() if not bool(criterion["passed"])]
    ratio_values = [
        criteria["force_error_N"]["ratio"],
        criteria["tangential_error_m"]["ratio"],
        criteria["orientation_error_rad"]["ratio"],
    ]
    max_gate_ratio = float(max(value for value in ratio_values if value is not None))
    if metrics["target_contact_count"] < thresholds["min_target_contact_count"]:
        max_gate_ratio = float("inf")
    return {
        "passed": not failed,
        "failed_criteria": failed,
        "criteria": criteria,
        "max_gate_ratio": max_gate_ratio,
    }


def ratio_vector(metrics: dict[str, Any], thresholds: dict[str, float]) -> np.ndarray:
    return np.asarray(
        [
            metrics["force_error_N"] / thresholds["max_force_error_N"],
            metrics["tangential_error_m"] / thresholds["max_tangential_error_m"],
            metrics["orientation_error_rad"] / thresholds["max_orientation_error_rad"],
        ],
        dtype=float,
    )


def smooth_minimax_objective(
    ratios: np.ndarray,
    *,
    target_contact_count: int,
    power: float,
    no_contact_penalty: float,
) -> float:
    values = np.asarray(ratios, dtype=float)
    if values.ndim != 1 or len(values) == 0:
        raise ValueError("ratios must be a non-empty vector")
    if power <= 1.0:
        raise ValueError("power must be > 1")
    score = float((np.mean(values**float(power))) ** (1.0 / float(power)))
    if int(target_contact_count) <= 0:
        score += float(no_contact_penalty)
    return score


def evaluate_terminal_metrics(
    *,
    model: mujoco.MjModel,
    data: mujoco.MjData,
    q: np.ndarray,
    q_min: np.ndarray,
    q_max: np.ndarray,
    reference_xy_m: np.ndarray,
    desired_rotation: np.ndarray,
    target_force_N: float,
    site_name: str,
    plane_geom_name: str,
    contact_geom_name: str,
) -> dict[str, Any]:
    q_array = np.asarray(q, dtype=float)
    set_qpos(model, data, q_array)
    mujoco.mj_forward(model, data)
    tcp = site_position(model, data, site_name)
    rotation = site_rotation_matrix(model, data, site_name)
    force, contact_count = positive_contact_normal_force_between(
        model,
        data,
        geom_a_name=plane_geom_name,
        geom_b_name=contact_geom_name,
    )
    force_error = abs(float(force) - float(target_force_N))
    tangential_error = float(np.linalg.norm(tcp[:2] - reference_xy_m))
    orientation_error = float(np.linalg.norm(orientation_error_rotvec(desired_rotation, rotation)))
    return {
        "q_rad": [float(x) for x in q_array],
        "tcp_m": [float(x) for x in tcp],
        "force_N": float(force),
        "force_error_N": float(force_error),
        "tangential_error_m": float(tangential_error),
        "orientation_error_rad": float(orientation_error),
        "target_contact_count": int(contact_count),
        "joint_limit_violation_rad": max_joint_limit_violation(q_array, q_min, q_max),
    }


def seed_candidates(contact_metrics: dict[str, Any]) -> list[TerminalSeed]:
    seeds: list[TerminalSeed] = [
        TerminalSeed(
            seed_id="initial",
            source="contact_manifold_initial_q",
            q_rad=np.asarray(contact_metrics["initial_q"], dtype=float),
        )
    ]
    for case in contact_metrics["cases"]:
        for candidate_key in ("best_candidate", "best_optimized_candidate"):
            candidate = case[candidate_key]
            seeds.append(
                TerminalSeed(
                    seed_id=f"{case['name']}__{candidate_key}",
                    source=f"v56_{case['name']}_{candidate_key}",
                    q_rad=np.asarray(candidate["q"], dtype=float),
                )
            )

    unique: list[TerminalSeed] = []
    seen: set[tuple[float, ...]] = set()
    for seed in seeds:
        key = tuple(round(float(value), 12) for value in seed.q_rad)
        if key in seen:
            continue
        seen.add(key)
        unique.append(seed)
    return unique


def optimizer_options(method: str, maxiter: int) -> dict[str, Any]:
    if method == "SLSQP":
        return {"maxiter": int(maxiter), "ftol": 1e-10}
    if method == "L-BFGS-B":
        return {"maxiter": int(maxiter), "ftol": 1e-12, "gtol": 1e-8}
    raise ValueError(f"unsupported optimizer method: {method}")


def run_optimizer(
    seed: TerminalSeed,
    *,
    method: str,
    model: mujoco.MjModel,
    data: mujoco.MjData,
    q_min: np.ndarray,
    q_max: np.ndarray,
    reference_xy_m: np.ndarray,
    desired_rotation: np.ndarray,
    target_force_N: float,
    site_name: str,
    plane_geom_name: str,
    contact_geom_name: str,
    thresholds: dict[str, float],
    power: float,
    no_contact_penalty: float,
    maxiter: int,
) -> dict[str, Any]:
    bounds = list(zip(q_min, q_max))

    def objective(q: np.ndarray) -> float:
        metrics = evaluate_terminal_metrics(
            model=model,
            data=data,
            q=q,
            q_min=q_min,
            q_max=q_max,
            reference_xy_m=reference_xy_m,
            desired_rotation=desired_rotation,
            target_force_N=target_force_N,
            site_name=site_name,
            plane_geom_name=plane_geom_name,
            contact_geom_name=contact_geom_name,
        )
        return smooth_minimax_objective(
            ratio_vector(metrics, thresholds),
            target_contact_count=metrics["target_contact_count"],
            power=power,
            no_contact_penalty=no_contact_penalty,
        )

    result = minimize(
        objective,
        seed.q_rad,
        method=method,
        bounds=bounds,
        options=optimizer_options(method, maxiter),
    )
    metrics = evaluate_terminal_metrics(
        model=model,
        data=data,
        q=result.x,
        q_min=q_min,
        q_max=q_max,
        reference_xy_m=reference_xy_m,
        desired_rotation=desired_rotation,
        target_force_N=target_force_N,
        site_name=site_name,
        plane_geom_name=plane_geom_name,
        contact_geom_name=contact_geom_name,
    )
    gate = terminal_gate(metrics, thresholds)
    ratios = ratio_vector(metrics, thresholds)
    return {
        "case_id": f"{seed.seed_id}__{method.lower()}",
        "seed": seed.to_dict(),
        "optimizer": {
            "method": method,
            "success": bool(result.success),
            "status": int(result.status),
            "message": str(result.message),
            "nfev": int(result.nfev),
            "nit": None if getattr(result, "nit", None) is None else int(result.nit),
            "objective": float(result.fun),
        },
        "terminal_metrics": metrics,
        "terminal_ratios": {
            "force_error_N": float(ratios[0]),
            "tangential_error_m": float(ratios[1]),
            "orientation_error_rad": float(ratios[2]),
        },
        "strict_terminal_gate": gate,
    }


def failure_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        for criterion in row["strict_terminal_gate"]["failed_criteria"]:
            counts[criterion] = counts.get(criterion, 0) + 1
    return dict(sorted(counts.items()))


def summarize_rows(rows: list[dict[str, Any]], *, v56_strict_best_ratio: float) -> dict[str, Any]:
    best = min(rows, key=lambda row: row["strict_terminal_gate"]["max_gate_ratio"])
    best_force = min(rows, key=lambda row: row["terminal_metrics"]["force_error_N"])
    best_xy = min(rows, key=lambda row: row["terminal_metrics"]["tangential_error_m"])
    best_orientation = min(rows, key=lambda row: row["terminal_metrics"]["orientation_error_rad"])
    best_ratio = float(best["strict_terminal_gate"]["max_gate_ratio"])
    return {
        "optimization_case_count": len(rows),
        "strict_terminal_pass_count": sum(1 for row in rows if row["strict_terminal_gate"]["passed"]),
        "optimizer_success_count": sum(1 for row in rows if row["optimizer"]["success"]),
        "setup_failed_criteria_counts": failure_counts(rows),
        "best_case_id": best["case_id"],
        "best_max_gate_ratio": best_ratio,
        "v56_strict_best_max_gate_ratio": float(v56_strict_best_ratio),
        "best_ratio_improvement": float(v56_strict_best_ratio) - best_ratio,
        "best_force_case_id": best_force["case_id"],
        "best_force_error_N": best_force["terminal_metrics"]["force_error_N"],
        "best_xy_case_id": best_xy["case_id"],
        "best_xy_error_m": best_xy["terminal_metrics"]["tangential_error_m"],
        "best_orientation_case_id": best_orientation["case_id"],
        "best_orientation_error_rad": best_orientation["terminal_metrics"]["orientation_error_rad"],
        "strict_terminal_constrained_optimization_complete": False,
        "strict_paper_equivalent_feasibility": False,
    }


def parse_methods(text: str) -> list[str]:
    methods = [part.strip() for part in text.split(",") if part.strip()]
    allowed = {"SLSQP", "L-BFGS-B"}
    unknown = [method for method in methods if method not in allowed]
    if unknown:
        raise ValueError(f"unsupported optimizer methods: {unknown}")
    if not methods:
        raise ValueError("at least one optimizer method is required")
    return methods


def build_payload(
    *,
    config_path: pathlib.Path,
    acceptance_path: pathlib.Path,
    contact_manifold_path: pathlib.Path,
    v115_metrics_path: pathlib.Path,
    remaining_blockers_path: pathlib.Path,
    methods: list[str],
    power: float,
    no_contact_penalty: float,
    maxiter: int,
) -> dict[str, Any]:
    config = load_yaml(config_path)
    acceptance = load_yaml(acceptance_path)
    contact = load_yaml(contact_manifold_path)
    v115 = load_yaml(v115_metrics_path)
    remaining = load_yaml(remaining_blockers_path)

    model_path = (ROOT / config["ur10e_mujoco"]["mjcf_path"]).resolve()
    model = load_model(model_path)
    apply_base_z_offset(model, float(contact["base_z_offset_m"]))
    data = make_data(model)
    q_min, q_max = joint_ranges(model)
    reference_xy = np.asarray(contact["reference_xy_m"], dtype=float)
    surface_normal = np.asarray(contact["surface_normal_world"], dtype=float)
    q_initial = np.asarray(contact["initial_q"], dtype=float)
    set_qpos(model, data, q_initial)
    desired_rotation = rotation_aligning_local_z_to_normal(
        surface_normal,
        reference_rotation=site_rotation_matrix(model, data, str(contact["site_name"])),
    )
    thresholds = strict_terminal_thresholds(acceptance)
    seeds = seed_candidates(contact)

    rows: list[dict[str, Any]] = []
    for seed in seeds:
        for method in methods:
            rows.append(
                run_optimizer(
                    seed,
                    method=method,
                    model=model,
                    data=data,
                    q_min=q_min,
                    q_max=q_max,
                    reference_xy_m=reference_xy,
                    desired_rotation=desired_rotation,
                    target_force_N=float(contact["target_force_N"]),
                    site_name=str(contact["site_name"]),
                    plane_geom_name=str(contact["plane_geom_name"]),
                    contact_geom_name=str(contact["contact_geom_name"]),
                    thresholds=thresholds,
                    power=power,
                    no_contact_penalty=no_contact_penalty,
                    maxiter=maxiter,
                )
            )

    summary = summarize_rows(
        rows,
        v56_strict_best_ratio=float(contact["strict_case_best"]["max_gate_ratio"]),
    )
    return {
        "run_source": "v116 strict terminal constrained optimization audit",
        "source_files": {
            "config": str(config_path),
            "acceptance": str(acceptance_path),
            "contact_manifold_gate_audit": str(contact_manifold_path),
            "v115_explicit_constraint_probe": str(v115_metrics_path),
            "remaining_blockers": str(remaining_blockers_path),
        },
        "v112_priority_context": {
            "top_priority_blocker_id": remaining["summary"]["top_priority_blocker_id"],
            "offline_actionable_blocker_ids": remaining["summary"][
                "offline_actionable_blocker_ids"
            ],
        },
        "v115_context": {
            "strict_setup_path_pass_count": v115["summary"]["strict_setup_path_pass_count"],
            "terminal_strict_criteria_pass_count": v115["summary"][
                "terminal_strict_criteria_pass_count"
            ],
            "qdot_criteria_pass_count": v115["summary"]["qdot_criteria_pass_count"],
        },
        "strict_terminal_thresholds": thresholds,
        "probe_parameters": {
            "methods": methods,
            "power": float(power),
            "no_contact_penalty": float(no_contact_penalty),
            "maxiter": int(maxiter),
            "seed_count": len(seeds),
            "optimizer_case_count": len(rows),
            "objective": "smooth p-norm minimax over normalized force, x/y, and orientation errors with no-contact penalty",
            "trajectory_stage": "not_run",
        },
        "summary": summary,
        "seed_rows": [seed.to_dict() for seed in seeds],
        "optimization_rows": rows,
        "claim_boundary": {
            "offline_simulation_only": True,
            "strict_terminal_constrained_optimization_complete": False,
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
            "Do not claim strict terminal feasibility from the improved minimax compromise.",
            "The stronger optimizer reduces the worst normalized strict terminal violation but still has no strict pass.",
            "Further progress likely needs approved calibration evidence or an accepted change to the setup target/contact model.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Strict Terminal Constrained Optimization Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Optimization case count: `{summary['optimization_case_count']}`",
        f"- Strict terminal pass count: `{summary['strict_terminal_pass_count']} / {summary['optimization_case_count']}`",
        f"- Optimizer success count: `{summary['optimizer_success_count']} / {summary['optimization_case_count']}`",
        f"- Best case: `{summary['best_case_id']}`",
        f"- Best max gate ratio: `{summary['best_max_gate_ratio']}`",
        f"- V56 strict best max gate ratio: `{summary['v56_strict_best_max_gate_ratio']}`",
        f"- Best ratio improvement: `{summary['best_ratio_improvement']}`",
        "",
        "| case | optimizer ok | gate pass | failed criteria | max gate ratio | force ratio | xy ratio | orient ratio | contact |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    ranked = sorted(
        payload["optimization_rows"],
        key=lambda row: row["strict_terminal_gate"]["max_gate_ratio"],
    )
    for row in ranked[:12]:
        gate = row["strict_terminal_gate"]
        ratios = row["terminal_ratios"]
        metrics = row["terminal_metrics"]
        failed = ";".join(gate["failed_criteria"]) or "none"
        lines.append(
            "| `{case}` | `{ok}` | `{passed}` | `{failed}` | `{maxr}` | `{force}` | `{xy}` | `{orient}` | `{contact}` |".format(
                case=row["case_id"],
                ok=row["optimizer"]["success"],
                passed=gate["passed"],
                failed=failed,
                maxr=gate["max_gate_ratio"],
                force=ratios["force_error_N"],
                xy=ratios["tangential_error_m"],
                orient=ratios["orientation_error_rad"],
                contact=metrics["target_contact_count"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The smooth-minimax optimizer improves the v56 best strict terminal ratio but still finds no strict pass.",
            "- The best optimized row remains target-contacting, but force, x/y, and orientation are all still outside at least one strict threshold.",
            "- This is terminal compatibility evidence only; no Stage A controller, Stage B trajectory, robustness, calibration, or hardware claim is made.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--acceptance", default=DEFAULT_ACCEPTANCE)
    parser.add_argument("--contact-manifold-metrics", default=DEFAULT_CONTACT_MANIFOLD)
    parser.add_argument("--v115-metrics", default=DEFAULT_V115)
    parser.add_argument("--remaining-blockers", default=DEFAULT_REMAINING_BLOCKERS)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--methods", default="SLSQP,L-BFGS-B")
    parser.add_argument("--power", type=float, default=8.0)
    parser.add_argument("--no-contact-penalty", type=float, default=20.0)
    parser.add_argument("--maxiter", type=int, default=200)
    args = parser.parse_args()

    if args.power <= 1.0:
        raise ValueError("--power must be > 1")
    if args.no_contact_penalty < 0.0:
        raise ValueError("--no-contact-penalty must be nonnegative")
    if args.maxiter <= 0:
        raise ValueError("--maxiter must be positive")

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "strict_terminal_constrained_optimization" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(
        config_path=(ROOT / args.config).resolve(),
        acceptance_path=(ROOT / args.acceptance).resolve(),
        contact_manifold_path=(ROOT / args.contact_manifold_metrics).resolve(),
        v115_metrics_path=(ROOT / args.v115_metrics).resolve(),
        remaining_blockers_path=(ROOT / args.remaining_blockers).resolve(),
        methods=parse_methods(args.methods),
        power=float(args.power),
        no_contact_penalty=float(args.no_contact_penalty),
        maxiter=int(args.maxiter),
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
