from __future__ import annotations

from pathlib import Path
from typing import Any

import mujoco
import numpy as np
import yaml

from tase_repro.contact_ladder import positive_contact_normal_force_between
from tase_repro.force_feedback import ForceMotionResult, apply_base_z_offset
from tase_repro.kinematics import load_model, make_data, set_qpos


def load_stage_a_target_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def selected_stage_a_target(config: dict[str, Any]) -> dict[str, Any]:
    selected = config["selected_stage_a_target"]
    if selected["label"] != "ur10e_adapted_terminal_setup_diagnostic":
        raise ValueError(f"unsupported Stage A target label: {selected['label']}")
    if selected["claim_scope"] != "terminal_target_for_simulation_controller_prototype_only":
        raise ValueError(f"unsupported Stage A target claim scope: {selected['claim_scope']}")
    return selected


def target_pair_force_trace(
    model_path: str | Path,
    *,
    base_z_offset_m: float,
    q: np.ndarray,
    plane_geom_name: str = "contact_plane",
    contact_geom_name: str = "contact_tip",
) -> dict[str, np.ndarray]:
    model = load_model(model_path)
    apply_base_z_offset(model, base_z_offset_m)
    data = make_data(model)
    q_array = np.asarray(q, dtype=float)
    forces = np.empty(len(q_array), dtype=float)
    counts = np.empty(len(q_array), dtype=int)
    for idx, q_i in enumerate(q_array):
        set_qpos(model, data, q_i)
        mujoco.mj_forward(model, data)
        force, count = positive_contact_normal_force_between(
            model,
            data,
            geom_a_name=plane_geom_name,
            geom_b_name=contact_geom_name,
        )
        forces[idx] = force
        counts[idx] = count
    return {"target_pair_force_N": forces, "target_contact_count": counts}


def summarize_target_pair_force(
    forces: np.ndarray,
    contact_counts: np.ndarray,
    *,
    target_force_N: float,
    tail_fraction: float = 0.2,
) -> dict[str, Any]:
    force_array = np.asarray(forces, dtype=float)
    count_array = np.asarray(contact_counts, dtype=int)
    if force_array.ndim != 1 or count_array.ndim != 1 or len(force_array) != len(count_array):
        raise ValueError("forces and contact_counts must be matching one-dimensional arrays")
    if len(force_array) == 0:
        raise ValueError("force trace must not be empty")
    tail = max(1, int(round(len(force_array) * float(tail_fraction))))
    error = force_array - float(target_force_N)
    return {
        "target_pair_initial_force_N": float(force_array[0]),
        "target_pair_final_force_N": float(force_array[-1]),
        "target_pair_tail_mean_force_N": float(np.mean(force_array[-tail:])),
        "target_pair_tail_mean_abs_force_error_N": float(np.mean(np.abs(error[-tail:]))),
        "target_pair_max_abs_force_error_N": float(np.max(np.abs(error))),
        "target_contact_present_fraction": float(np.mean(count_array > 0)),
        "target_contact_min_count": int(np.min(count_array)),
        "target_contact_max_count": int(np.max(count_array)),
    }


def metrics_with_target_pair_force(base_metrics: dict[str, Any], target_pair_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        **base_metrics,
        "initial_force_N": target_pair_summary["target_pair_initial_force_N"],
        "final_force_N": target_pair_summary["target_pair_final_force_N"],
        "tail_mean_force_N": target_pair_summary["target_pair_tail_mean_force_N"],
        "tail_mean_abs_force_error_N": target_pair_summary["target_pair_tail_mean_abs_force_error_N"],
        "max_abs_force_error_N": target_pair_summary["target_pair_max_abs_force_error_N"],
        "contact_present_fraction": target_pair_summary["target_contact_present_fraction"],
    }


def summarize_handoff_result(
    result: ForceMotionResult,
    *,
    model_path: str | Path,
    base_z_offset_m: float,
    target_force_N: float,
) -> dict[str, Any]:
    trace = target_pair_force_trace(
        model_path,
        base_z_offset_m=base_z_offset_m,
        q=result.q,
    )
    return summarize_target_pair_force(
        trace["target_pair_force_N"],
        trace["target_contact_count"],
        target_force_N=target_force_N,
    )
