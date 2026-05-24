#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from typing import Any

import mujoco
import numpy as np
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from audit_stage_a_base_z_bracket import (
    parse_float_list,
    summarize_terminal,
    terminal_metrics_for_case,
    write_git_state,
)
from tase_repro.base_z_recovery import aggregate_positive_start_contact, base_z_delta_label
from tase_repro.contact_ladder import positive_contact_normal_force_between
from tase_repro.force_feedback import apply_base_z_offset
from tase_repro.kinematics import load_model, make_data, set_qpos, site_position
from tase_repro.setup_terminal_ik import SetupTerminalThresholds
from tase_repro.stage_a_target_handoff import load_stage_a_target_config, selected_stage_a_target


def candidate_metrics(
    *,
    model: Any,
    data: Any,
    q: np.ndarray,
    seed_label: str,
    site_name: str,
    contact_geom_name: str,
    plane_geom_name: str,
    reference_xy_m: np.ndarray,
    target_force_N: float,
    force_threshold_N: float,
    xy_threshold_m: float,
) -> dict[str, Any]:
    set_qpos(model, data, q)
    mujoco.mj_forward(model, data)
    tcp = site_position(model, data, site_name)
    force, target_contact_count = positive_contact_normal_force_between(
        model,
        data,
        geom_a_name=plane_geom_name,
        geom_b_name=contact_geom_name,
    )
    force_error = abs(float(force) - float(target_force_N))
    xy_error = float(np.linalg.norm(tcp[:2] - reference_xy_m))
    criteria = {
        "force_error_N": {
            "actual": force_error,
            "operator": "<=",
            "threshold": float(force_threshold_N),
            "passed": force_error <= float(force_threshold_N),
        },
        "tangential_error_m": {
            "actual": xy_error,
            "operator": "<=",
            "threshold": float(xy_threshold_m),
            "passed": xy_error <= float(xy_threshold_m),
        },
        "target_contact_count": {
            "actual": int(target_contact_count),
            "operator": ">=",
            "threshold": 1,
            "passed": int(target_contact_count) >= 1,
        },
    }
    failed = [name for name, criterion in criteria.items() if not criterion["passed"]]
    ratios = [
        force_error / float(force_threshold_N),
        xy_error / float(xy_threshold_m),
        0.0 if target_contact_count >= 1 else float("inf"),
    ]
    return {
        "seed_label": seed_label,
        "q": [float(x) for x in q],
        "tcp_m": [float(x) for x in tcp],
        "force_N": float(force),
        "force_error_N": force_error,
        "tangential_error_m": xy_error,
        "target_contact_count": int(target_contact_count),
        "criteria": criteria,
        "failed_criteria": failed,
        "passed": not failed,
        "max_gate_ratio": float(np.max(ratios)),
    }


def candidate_sort_key(candidate: dict[str, Any]) -> tuple[float, float, float, float, str]:
    return (
        0.0 if candidate["passed"] else 1.0,
        0.0 if candidate["target_contact_count"] >= 1 else 1.0,
        float(candidate["max_gate_ratio"]),
        float(candidate["tangential_error_m"]),
        str(candidate["seed_label"]),
    )


def start_search_for_case(
    *,
    case_name: str,
    base_z_offset_delta_m: float,
    base_z_offset_nominal_m: float,
    model_path: pathlib.Path,
    setup: dict[str, Any],
    config_path: pathlib.Path,
    setup_path: pathlib.Path,
    args: argparse.Namespace,
    out_dir: pathlib.Path,
) -> dict[str, Any]:
    base_z_offset = base_z_offset_nominal_m + float(base_z_offset_delta_m)
    model = load_model(model_path)
    apply_base_z_offset(model, base_z_offset)
    data = make_data(model)
    q0 = np.asarray(setup["initial_q"], dtype=float)
    reference_xy = np.asarray(setup["reference_xy_m"], dtype=float)
    site_name = str(setup["site_name"])
    contact_geom_name = str(setup["contact_geom_name"])
    plane_geom_name = str(setup["plane_geom_name"])
    target_force = float(setup["target_force_N"])
    force_threshold = float(args.max_force_error_N)
    xy_threshold = float(args.max_tangential_error_m)

    seed_specs: list[tuple[str, np.ndarray]] = [("initial", q0.copy())]
    joint_steps = np.linspace(-float(args.joint_sweep_rad), float(args.joint_sweep_rad), int(args.joint_sweep_count))
    for joint_idx in range(len(q0)):
        for step in joint_steps:
            q = q0.copy()
            q[joint_idx] += float(step)
            seed_specs.append((f"joint{joint_idx}_{float(step):+.6f}", q))
    pair_steps = np.linspace(-float(args.pair_sweep_rad), float(args.pair_sweep_rad), int(args.pair_sweep_count))
    pair_specs = [
        tuple(int(part) for part in spec.strip().split(":"))
        for spec in str(args.pair_sweep_joints).split(",")
        if spec.strip()
    ]
    for joint_a, joint_b in pair_specs:
        for step_a in pair_steps:
            for step_b in pair_steps:
                q = q0.copy()
                q[joint_a] += float(step_a)
                q[joint_b] += float(step_b)
                seed_specs.append(
                    (
                        f"joint{joint_a}_{float(step_a):+.6f}__joint{joint_b}_{float(step_b):+.6f}",
                        q,
                    )
                )
    rng = np.random.default_rng(int(args.random_seed) + int(round(1_000_000.0 * float(base_z_offset_delta_m))))
    for idx in range(int(args.random_seed_count)):
        seed_specs.append((f"random_{idx:05d}", q0 + rng.normal(0.0, float(args.random_seed_std_rad), size=q0.shape)))

    candidates = [
        candidate_metrics(
            model=model,
            data=data,
            q=q,
            seed_label=label,
            site_name=site_name,
            contact_geom_name=contact_geom_name,
            plane_geom_name=plane_geom_name,
            reference_xy_m=reference_xy,
            target_force_N=target_force,
            force_threshold_N=force_threshold,
            xy_threshold_m=xy_threshold,
        )
        for label, q in seed_specs
    ]
    candidates.sort(key=candidate_sort_key)
    best = candidates[0]
    pass_count = sum(1 for candidate in candidates if candidate["passed"])
    contact_count = sum(1 for candidate in candidates if candidate["target_contact_count"] >= 1)
    payload = {
        "case": case_name,
        "config": str(config_path),
        "model": str(model_path),
        "setup_metrics": str(setup_path),
        "base_z_offset_nominal_m": base_z_offset_nominal_m,
        "base_z_offset_delta_m": float(base_z_offset_delta_m),
        "base_z_offset_m": base_z_offset,
        "candidate_count": len(candidates),
        "pass_count": pass_count,
        "contact_candidate_count": contact_count,
        "joint_sweep_rad": float(args.joint_sweep_rad),
        "joint_sweep_count": int(args.joint_sweep_count),
        "pair_sweep_rad": float(args.pair_sweep_rad),
        "pair_sweep_count": int(args.pair_sweep_count),
        "pair_sweep_joints": [list(pair) for pair in pair_specs],
        "random_seed_count": int(args.random_seed_count),
        "random_seed_std_rad": float(args.random_seed_std_rad),
        "random_seed": int(args.random_seed),
        "thresholds": {
            "max_force_error_N": force_threshold,
            "max_tangential_error_m": xy_threshold,
        },
        "best_candidate": best,
        "warnings": [
            "start-contact candidate search only",
            "not terminal, path, trajectory, robustness, or hardware evidence",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    lines = [
        "# Positive Base-Z Start Contact Search Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case: `{case_name}`",
        f"- Base-z offset delta m: `{base_z_offset_delta_m}`",
        f"- Start pass count: `{pass_count} / {len(candidates)}`",
        f"- Contact candidate count: `{contact_count}`",
        f"- Best pass: `{best['passed']}`",
        f"- Best seed: `{best['seed_label']}`",
        f"- Best failed criteria: `{';'.join(best['failed_criteria']) or 'none'}`",
        f"- Best force error N: `{best['force_error_N']}`",
        f"- Best x/y error m: `{best['tangential_error_m']}`",
        "",
        "Interpretation:",
        "",
        "- This search probes whether the Stage A start-contact failure is local-optimizer dependent.",
        "- It is simulation-only and does not prove terminal or path recovery.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def summarize_start_search(metrics: dict[str, Any]) -> dict[str, Any]:
    best = metrics["best_candidate"]
    return {
        "passed": bool(best["passed"]),
        "pass_count": int(metrics["pass_count"]),
        "candidate_count": int(metrics["candidate_count"]),
        "contact_candidate_count": int(metrics["contact_candidate_count"]),
        "best_seed": str(best["seed_label"]),
        "best_force_error_N": float(best["force_error_N"]),
        "best_tangential_error_m": float(best["tangential_error_m"]),
        "best_force_N": float(best["force_N"]),
        "best_target_contact_count": int(best["target_contact_count"]),
        "best_failed_criteria": list(best["failed_criteria"]),
        "best_q": list(best["q"]),
    }


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    lines = [
        "# Positive Base-Z Start Contact Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case count: `{aggregate['case_count']}`",
        f"- Start pass count: `{aggregate['start_pass_count']}`",
        f"- Terminal pass count: `{aggregate['terminal_pass_count']}`",
        f"- Contact-without-start-pass count: `{aggregate['contact_without_start_pass_count']}`",
        f"- Max start-pass delta mm: `{aggregate['max_start_pass_delta_mm']}`",
        f"- Max terminal-pass delta mm: `{aggregate['max_terminal_pass_delta_mm']}`",
        "",
        "| delta mm | start pass | start best seed | start force err N | start x/y err m | terminal pass | terminal orientation rad |",
        "| ---: | --- | --- | ---: | ---: | --- | ---: |",
    ]
    for case in cases:
        start = case["start_search"]
        terminal = case["terminal"]
        lines.append(
            "| `{delta}` | `{start_pass}` | `{seed}` | `{force}` | `{xy}` | `{terminal_pass}` | `{orientation}` |".format(
                delta=case["base_z_offset_delta_mm"],
                start_pass=start["passed"],
                seed=start["best_seed"],
                force=start["best_force_error_N"],
                xy=start["best_tangential_error_m"],
                terminal_pass=terminal["passed"],
                orientation=terminal["orientation_error_rad"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- Positive-side start contact is recoverable for the listed passing deltas under this broad seed search.",
            "- Terminal orientation remains a separate gate; this audit is not path recovery or robustness evidence.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml")
    parser.add_argument("--setup-metrics", default="runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml")
    parser.add_argument("--stage-a-target-config", default="configs/ur10e_adapted_stage_a_target.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--base-z-deltas-mm", default="0.05,0.1,0.15,0.2,0.25,0.5,0.75,1.0")
    parser.add_argument("--joint-sweep-rad", type=float, default=0.08)
    parser.add_argument("--joint-sweep-count", type=int, default=321)
    parser.add_argument("--pair-sweep-rad", type=float, default=0.04)
    parser.add_argument("--pair-sweep-count", type=int, default=161)
    parser.add_argument("--pair-sweep-joints", default="1:2,2:5,2:3,3:5")
    parser.add_argument("--random-seed-count", type=int, default=10000)
    parser.add_argument("--random-seed-std-rad", type=float, default=0.03)
    parser.add_argument("--random-seed", type=int, default=541)
    parser.add_argument("--max-force-error-N", type=float, default=0.25)
    parser.add_argument("--max-tangential-error-m", type=float, default=0.004)
    parser.add_argument("--terminal-random-seed-count", type=int, default=512)
    parser.add_argument("--terminal-random-seed-std-rad", type=float, default=0.15)
    parser.add_argument("--terminal-random-seed", type=int, default=37)
    parser.add_argument("--terminal-max-nfev", type=int, default=300)
    parser.add_argument("--posture-weight", type=float, default=1e-4)
    args = parser.parse_args()

    deltas_m = [value / 1000.0 for value in parse_float_list(args.base_z_deltas_mm)]
    config_path = (ROOT / args.config).resolve()
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    setup_path = (ROOT / args.setup_metrics).resolve()
    with setup_path.open("r", encoding="utf-8") as f:
        setup = yaml.safe_load(f)
    target_config_path = (ROOT / args.stage_a_target_config).resolve()
    target_config = load_stage_a_target_config(target_config_path)
    target = selected_stage_a_target(target_config)
    gate = target["diagnostic_gate"]
    thresholds = SetupTerminalThresholds(
        max_force_error_N=float(gate["max_terminal_force_error_N"]),
        max_tangential_error_m=float(gate["max_terminal_tangential_error_m"]),
        max_orientation_error_rad=float(gate["max_terminal_orientation_error_rad"]),
    )
    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    base_z_offset_nominal = float(setup["base_z_offset_m"])
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "positive_base_z_start_contact" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    extra_terminal_seeds = {
        "selected_stage_a_target": np.asarray(target["q_rad"], dtype=float),
    }

    cases = []
    for delta_m in deltas_m:
        case_name = base_z_delta_label(delta_m)
        case_dir = out_dir / "cases" / case_name
        start_dir = case_dir / "start_search"
        terminal_dir = case_dir / "terminal"
        start_dir.mkdir(parents=True, exist_ok=True)
        terminal_dir.mkdir(parents=True, exist_ok=True)
        start_metrics = start_search_for_case(
            case_name=case_name,
            base_z_offset_delta_m=delta_m,
            base_z_offset_nominal_m=base_z_offset_nominal,
            model_path=model_path,
            setup=setup,
            config_path=config_path,
            setup_path=setup_path,
            args=args,
            out_dir=start_dir,
        )
        terminal_args = argparse.Namespace(
            random_seed_count=int(args.terminal_random_seed_count),
            random_seed_std_rad=float(args.terminal_random_seed_std_rad),
            random_seed=int(args.terminal_random_seed),
            terminal_max_nfev=int(args.terminal_max_nfev),
            posture_weight=float(args.posture_weight),
        )
        terminal_metrics = terminal_metrics_for_case(
            case_name=case_name,
            base_z_offset_delta_m=delta_m,
            base_z_offset_nominal_m=base_z_offset_nominal,
            model_path=model_path,
            setup=setup,
            setup_path=setup_path,
            config_path=config_path,
            thresholds=thresholds,
            extra_seed_qs=extra_terminal_seeds,
            args=terminal_args,
            out_dir=terminal_dir,
        )
        cases.append(
            {
                "case": case_name,
                "base_z_offset_delta_m": float(delta_m),
                "base_z_offset_delta_mm": 1000.0 * float(delta_m),
                "start_search": summarize_start_search(start_metrics),
                "terminal": summarize_terminal(terminal_metrics),
            }
        )

    aggregate = aggregate_positive_start_contact(cases)
    payload = {
        "run_id": run_id,
        "source": "positive base-z start-contact diagnostic search",
        "base_z_deltas_mm": [1000.0 * value for value in deltas_m],
        "aggregate": aggregate,
        "parameters": {
            "joint_sweep_rad": float(args.joint_sweep_rad),
            "joint_sweep_count": int(args.joint_sweep_count),
            "pair_sweep_rad": float(args.pair_sweep_rad),
            "pair_sweep_count": int(args.pair_sweep_count),
            "pair_sweep_joints": args.pair_sweep_joints,
            "random_seed_count": int(args.random_seed_count),
            "random_seed_std_rad": float(args.random_seed_std_rad),
            "random_seed": int(args.random_seed),
            "terminal_random_seed_count": int(args.terminal_random_seed_count),
            "terminal_random_seed_std_rad": float(args.terminal_random_seed_std_rad),
            "terminal_random_seed": int(args.terminal_random_seed),
            "terminal_max_nfev": int(args.terminal_max_nfev),
        },
        "cases": cases,
        "warnings": [
            "start-contact diagnostic search only",
            "not terminal/path/trajectory recovery",
            "not strict paper-equivalent feasibility",
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
