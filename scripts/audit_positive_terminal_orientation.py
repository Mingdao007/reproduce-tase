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

from audit_stage_a_base_z_bracket import compact_candidate, parse_float_list, write_git_state
from tase_repro.base_z_recovery import (
    aggregate_positive_terminal_orientation,
    base_z_delta_label,
)
from tase_repro.contact import unit_vector
from tase_repro.force_feedback import apply_base_z_offset
from tase_repro.kinematics import load_model, make_data, set_qpos, site_rotation_matrix
from tase_repro.setup_terminal_ik import SetupTerminalThresholds, solve_setup_terminal_ik
from tase_repro.stage_a_target_handoff import load_stage_a_target_config, selected_stage_a_target


VARIANTS = {
    "contact_point": {
        "label": "current contact-point model",
        "config": "configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml",
        "setup_metrics": "runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml",
        "include_selected_stage_a_seed": True,
        "status": "current v54 contact-point convention; simulation-only, not hardware-calibrated",
    },
    "legacy_center": {
        "label": "legacy sphere-center model",
        "config": "configs/mujoco_ur10e_tilted_plane.yaml",
        "setup_metrics": "runs/setup_terminal_ik_audit/20260524T111150/metrics.yaml",
        "include_selected_stage_a_seed": False,
        "status": "known flawed comparison where the 85 mm site is coincident with the contact sphere center",
    },
}


def target_pair_contact_frame_angle(
    model: Any,
    data: Any,
    *,
    plane_geom_name: str,
    contact_geom_name: str,
    normal_world: np.ndarray,
) -> float | None:
    geom_a_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, plane_geom_name)
    geom_b_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, contact_geom_name)
    if geom_a_id < 0 or geom_b_id < 0:
        return None
    target_pair = {int(geom_a_id), int(geom_b_id)}
    angles = []
    normal = unit_vector(normal_world)
    for contact_idx in range(data.ncon):
        contact = data.contact[contact_idx]
        if {int(contact.geom[0]), int(contact.geom[1])} != target_pair:
            continue
        frame_normal = unit_vector(contact.frame.reshape(3, 3)[0].copy())
        angles.append(float(np.arccos(np.clip(float(frame_normal.dot(normal)), -1.0, 1.0))))
    return min(angles) if angles else None


def orientation_components_for_q(
    *,
    model_path: pathlib.Path,
    base_z_offset_m: float,
    q: list[float],
    site_name: str,
    plane_geom_name: str,
    contact_geom_name: str,
    surface_normal_world: np.ndarray,
) -> dict[str, Any]:
    model = load_model(model_path)
    apply_base_z_offset(model, base_z_offset_m)
    data = make_data(model)
    set_qpos(model, data, np.asarray(q, dtype=float))
    rotation = site_rotation_matrix(model, data, site_name)
    normal = unit_vector(surface_normal_world)
    local_z = unit_vector(rotation[:, 2])
    force_normal_error = float(np.arccos(np.clip(float(local_z.dot(normal)), -1.0, 1.0)))
    minus_z_error = float(np.arccos(np.clip(float((-local_z).dot(normal)), -1.0, 1.0)))
    contact_frame_error = target_pair_contact_frame_angle(
        model,
        data,
        plane_geom_name=plane_geom_name,
        contact_geom_name=contact_geom_name,
        normal_world=normal,
    )
    return {
        "force_normal_only_error_rad": force_normal_error,
        "minus_local_z_to_normal_error_rad": minus_z_error,
        "target_contact_frame_normal_error_rad": contact_frame_error,
        "tcp_local_z_world": [float(x) for x in local_z],
    }


def threshold_passes(
    *,
    full_rotation_error_rad: float,
    force_normal_only_error_rad: float,
    force_error_N: float,
    tangential_error_m: float,
    target_contact_count: int,
    force_threshold_N: float,
    tangential_threshold_m: float,
    orientation_thresholds_rad: list[float],
) -> dict[str, Any]:
    force_xy_contact = (
        force_error_N <= force_threshold_N
        and tangential_error_m <= tangential_threshold_m
        and target_contact_count >= 1
    )
    by_threshold = {}
    for threshold in orientation_thresholds_rad:
        key = f"{threshold:.3f}"
        by_threshold[key] = {
            "full_rotation_passed": bool(force_xy_contact and full_rotation_error_rad <= threshold),
            "force_normal_only_passed": bool(
                force_xy_contact and force_normal_only_error_rad <= threshold
            ),
        }
    return {
        "force_xy_contact_passed": bool(force_xy_contact),
        "orientation_thresholds_rad": by_threshold,
    }


def variant_metrics(
    *,
    variant_name: str,
    variant: dict[str, Any],
    deltas_m: list[float],
    target: dict[str, Any],
    thresholds: SetupTerminalThresholds,
    orientation_thresholds_rad: list[float],
    args: argparse.Namespace,
    out_dir: pathlib.Path,
) -> list[dict[str, Any]]:
    config_path = (ROOT / str(variant["config"])).resolve()
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    model_path = (ROOT / cfg["ur10e_mujoco"]["mjcf_path"]).resolve()
    setup_path = (ROOT / str(variant["setup_metrics"])).resolve()
    with setup_path.open("r", encoding="utf-8") as f:
        setup = yaml.safe_load(f)

    extra_seed_qs = {"setup_best_candidate": np.asarray(setup["best_candidate"]["q"], dtype=float)}
    if bool(variant["include_selected_stage_a_seed"]):
        extra_seed_qs["selected_stage_a_target"] = np.asarray(target["q_rad"], dtype=float)

    base_z_offset_nominal = float(setup["base_z_offset_m"])
    site_name = str(setup["site_name"])
    plane_geom_name = str(setup.get("plane_geom_name", "contact_plane"))
    contact_geom_name = str(setup.get("contact_geom_name", "contact_tip"))
    cases = []
    for delta_m in deltas_m:
        case_name = base_z_delta_label(delta_m)
        case_dir = out_dir / "cases" / variant_name / case_name
        case_dir.mkdir(parents=True, exist_ok=True)
        result = solve_setup_terminal_ik(
            model_path,
            initial_q=np.asarray(setup["initial_q"], dtype=float),
            base_z_offset_m=base_z_offset_nominal + float(delta_m),
            target_force_N=float(setup["target_force_N"]),
            thresholds=thresholds,
            surface_normal_world=np.asarray(setup["surface_normal_world"], dtype=float),
            site_name=site_name,
            contact_geom_name=contact_geom_name,
            plane_geom_name=plane_geom_name,
            random_seed_count=int(args.random_seed_count),
            random_seed_std_rad=float(args.random_seed_std_rad),
            random_seed=int(args.random_seed),
            max_nfev=int(args.max_nfev),
            posture_weight=float(args.posture_weight),
            extra_seed_qs=extra_seed_qs,
        )
        best = compact_candidate(result.best_candidate)
        components = orientation_components_for_q(
            model_path=model_path,
            base_z_offset_m=base_z_offset_nominal + float(delta_m),
            q=best["q"],
            site_name=site_name,
            plane_geom_name=plane_geom_name,
            contact_geom_name=contact_geom_name,
            surface_normal_world=np.asarray(setup["surface_normal_world"], dtype=float),
        )
        threshold_eval = threshold_passes(
            full_rotation_error_rad=float(best["orientation_error_rad"]),
            force_normal_only_error_rad=float(components["force_normal_only_error_rad"]),
            force_error_N=float(best["force_error_N"]),
            tangential_error_m=float(best["tangential_error_m"]),
            target_contact_count=int(best["target_contact_count"]),
            force_threshold_N=thresholds.max_force_error_N,
            tangential_threshold_m=thresholds.max_tangential_error_m,
            orientation_thresholds_rad=orientation_thresholds_rad,
        )
        force_normal_only_passed = bool(
            threshold_eval["force_xy_contact_passed"]
            and float(components["force_normal_only_error_rad"]) <= thresholds.max_orientation_error_rad
        )
        case = {
            "case": case_name,
            "variant": variant_name,
            "variant_label": str(variant["label"]),
            "variant_status": str(variant["status"]),
            "config": str(config_path),
            "model": str(model_path),
            "setup_metrics": str(setup_path),
            "base_z_offset_nominal_m": base_z_offset_nominal,
            "base_z_offset_delta_m": float(delta_m),
            "base_z_offset_delta_mm": 1000.0 * float(delta_m),
            "base_z_offset_m": base_z_offset_nominal + float(delta_m),
            "candidate_count": len(result.candidates),
            "pass_count": result.pass_count,
            "extra_seed_labels": list(extra_seed_qs),
            "best_candidate": best,
            "force_xy_contact_passed": bool(threshold_eval["force_xy_contact_passed"]),
            "diagnostic_passed": bool(best["passed"]),
            "force_normal_only_passed": force_normal_only_passed,
            "full_rotation_error_rad": float(best["orientation_error_rad"]),
            "force_normal_only_error_rad": float(components["force_normal_only_error_rad"]),
            "full_minus_force_normal_abs_rad": abs(
                float(best["orientation_error_rad"])
                - float(components["force_normal_only_error_rad"])
            ),
            "minus_local_z_to_normal_error_rad": float(components["minus_local_z_to_normal_error_rad"]),
            "target_contact_frame_normal_error_rad": components["target_contact_frame_normal_error_rad"],
            "tcp_local_z_world": components["tcp_local_z_world"],
            "threshold_eval": threshold_eval,
        }
        with (case_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
            yaml.safe_dump(case, f, sort_keys=False, allow_unicode=True)
        with (case_dir / "metrics.json").open("w", encoding="utf-8") as f:
            json.dump(case, f, indent=2)
        cases.append(case)
    return cases


def write_summary(out_dir: pathlib.Path, aggregate: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    lines = [
        "# Positive Terminal Orientation Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Case count: `{aggregate['case_count']}`",
        f"- Variant count: `{aggregate['variant_count']}`",
        "",
        "| variant | diagnostic pass | force/x-y/contact pass | max diagnostic delta mm | threshold for all force/x-y/contact cases rad | max full error rad | max yaw gap rad |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant, metrics in aggregate["variants"].items():
        lines.append(
            "| `{variant}` | `{diag}` | `{force_xy}` | `{max_delta}` | `{threshold}` | `{max_full}` | `{yaw}` |".format(
                variant=variant,
                diag=metrics["diagnostic_pass_count"],
                force_xy=metrics["force_xy_contact_pass_count"],
                max_delta=metrics["max_diagnostic_pass_delta_mm"],
                threshold=metrics["min_full_rotation_threshold_for_force_xy_contact_cases_rad"],
                max_full=metrics["max_full_rotation_error_rad"],
                yaw=metrics["max_full_minus_force_normal_abs_rad"],
            )
        )
    lines.extend(
        [
            "",
            "| variant | delta mm | diagnostic pass | force/x-y/contact | full rotation rad | force-normal-only rad | -z convention rad |",
            "| --- | ---: | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for case in cases:
        lines.append(
            "| `{variant}` | `{delta}` | `{diag}` | `{force_xy}` | `{full}` | `{normal}` | `{minus_z}` |".format(
                variant=case["variant"],
                delta=case["base_z_offset_delta_mm"],
                diag=case["diagnostic_passed"],
                force_xy=case["force_xy_contact_passed"],
                full=case["full_rotation_error_rad"],
                normal=case["force_normal_only_error_rad"],
                minus_z=case["minus_local_z_to_normal_error_rad"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- Full-rotation and force-normal-only errors are effectively identical when the yaw gap is near zero.",
            "- The `legacy_center` variant is a known flawed geometry comparison, not a hardware-ready fix.",
            "- This audit is terminal-state simulation evidence only; it does not prove path recovery, robustness, or hardware readiness.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--stage-a-target-config", default="configs/ur10e_adapted_stage_a_target.yaml")
    parser.add_argument("--base-z-deltas-mm", default="0.05,0.1,0.15,0.2,0.25,0.5,0.75,1.0")
    parser.add_argument("--variants", default="contact_point,legacy_center")
    parser.add_argument("--orientation-thresholds-rad", default="0.08,0.09,0.10,0.11,0.12")
    parser.add_argument("--random-seed-count", type=int, default=512)
    parser.add_argument("--random-seed-std-rad", type=float, default=0.15)
    parser.add_argument("--random-seed", type=int, default=37)
    parser.add_argument("--max-nfev", type=int, default=300)
    parser.add_argument("--posture-weight", type=float, default=1e-4)
    args = parser.parse_args()

    deltas_m = [value / 1000.0 for value in parse_float_list(args.base_z_deltas_mm)]
    orientation_thresholds = parse_float_list(args.orientation_thresholds_rad)
    selected_variants = [part.strip() for part in str(args.variants).split(",") if part.strip()]
    unknown = [variant for variant in selected_variants if variant not in VARIANTS]
    if unknown:
        raise ValueError(f"unknown variants: {', '.join(unknown)}")

    target_config_path = (ROOT / args.stage_a_target_config).resolve()
    target_config = load_stage_a_target_config(target_config_path)
    target = selected_stage_a_target(target_config)
    gate = target["diagnostic_gate"]
    thresholds = SetupTerminalThresholds(
        max_force_error_N=float(gate["max_terminal_force_error_N"]),
        max_tangential_error_m=float(gate["max_terminal_tangential_error_m"]),
        max_orientation_error_rad=float(gate["max_terminal_orientation_error_rad"]),
    )
    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "positive_terminal_orientation" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = []
    for variant_name in selected_variants:
        cases.extend(
            variant_metrics(
                variant_name=variant_name,
                variant=VARIANTS[variant_name],
                deltas_m=deltas_m,
                target=target,
                thresholds=thresholds,
                orientation_thresholds_rad=orientation_thresholds,
                args=args,
                out_dir=out_dir,
            )
        )

    aggregate = aggregate_positive_terminal_orientation(cases)
    payload = {
        "run_id": run_id,
        "source": "positive terminal orientation gate/model diagnostic audit",
        "base_z_deltas_mm": [1000.0 * value for value in deltas_m],
        "selected_variants": selected_variants,
        "variant_definitions": {name: VARIANTS[name] for name in selected_variants},
        "diagnostic_gate": gate,
        "orientation_thresholds_rad": orientation_thresholds,
        "parameters": {
            "random_seed_count": int(args.random_seed_count),
            "random_seed_std_rad": float(args.random_seed_std_rad),
            "random_seed": int(args.random_seed),
            "max_nfev": int(args.max_nfev),
            "posture_weight": float(args.posture_weight),
        },
        "aggregate": aggregate,
        "cases": cases,
        "warnings": [
            "terminal-state diagnostic simulation only",
            "legacy_center is a known flawed comparison model, not a solution",
            "not path/trajectory recovery",
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
