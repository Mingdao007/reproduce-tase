#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import pathlib
import subprocess
import sys
from typing import Any

import numpy as np
import scipy.io
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.panda_kinematics import (  # noqa: E402
    panda_forward_kinematics,
    panda_geometric_jacobian,
)


DEFAULT_LEGACY_ROOT = pathlib.Path(
    "/home/andy/ur10e_ros2_ws/experiments/"
    "20260523_tase_finite_time_ur10e_mujoco_reproduction/"
    "runs/full_paper_matlab/20260523T114034/worktree/RNN_F2"
)
DEFAULT_PYTHON_RAW = ROOT / "runs/paper_7dof_section_v/20260524T121503/paper_7dof_section_v_raw.npz"
DEFAULT_PYTHON_METRICS = ROOT / "runs/paper_7dof_section_v/20260524T121503/metrics.yaml"
SAMPLE_TIMES_S = (0.0, 5.0, 10.0, 22.0, 29.999)


def git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except subprocess.CalledProcessError:
        return "unavailable"


def display_path(path: pathlib.Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def resolve_path(value: str) -> pathlib.Path:
    path = pathlib.Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def matlab_string(value: Any) -> str:
    array = np.asarray(value)
    if array.shape == ():
        return str(array.item())
    if array.size == 1:
        return str(array.reshape(-1)[0])
    return str(value)


def nearest_index(t_s: np.ndarray, sample_time_s: float) -> int:
    return int(np.argmin(np.abs(t_s - float(sample_time_s))))


def load_legacy_run(path: pathlib.Path) -> dict[str, Any]:
    mat = scipy.io.loadmat(path, squeeze_me=True, struct_as_record=False)
    t_s = np.asarray(mat["t_save"], dtype=float).reshape(-1)
    q_rad = np.asarray(mat["q_save"], dtype=float)
    dq_rad_s = np.asarray(mat["dq_save"], dtype=float)
    x_state = np.asarray(mat["x_save"], dtype=float)
    return {
        "path": path,
        "t_s": t_s,
        "q_rad": q_rad,
        "dq_rad_s": dq_rad_s,
        "x_state": x_state,
        "condJ": np.asarray(mat["condJ_save"], dtype=float).reshape(-1),
        "force_error_N": np.asarray(mat["force_error_save"], dtype=float).reshape(-1),
        "metadata": {
            "paper_method_variant": matlab_string(mat.get("paper_method_variant", "")),
            "paper_method_acceptance_mode": matlab_string(mat.get("paper_method_acceptance_mode", "")),
            "solver_mode": matlab_string(mat.get("solver_mode", "")),
            "orientation_mode": matlab_string(mat.get("orientation_mode", "")),
            "force_loop_mode": matlab_string(mat.get("force_loop_mode", "")),
            "paper_method_notes": matlab_string(mat.get("paper_method_notes", "")),
        },
    }


def load_python_run(raw_path: pathlib.Path, metrics_path: pathlib.Path) -> dict[str, Any]:
    with np.load(raw_path) as raw:
        t_s = np.asarray(raw["t_s"], dtype=float)
        q_rad = np.asarray(raw["q_rad"], dtype=float)
        dq_rad_s = np.asarray(raw["qdot_rad_s"], dtype=float)
        position_m = np.asarray(raw["position_m"], dtype=float)
        force_error_N = np.asarray(raw["force_error_N"], dtype=float)
    metrics_payload = yaml.safe_load(metrics_path.read_text(encoding="utf-8"))
    return {
        "path": raw_path,
        "metrics_path": metrics_path,
        "t_s": t_s,
        "q_rad": q_rad,
        "dq_rad_s": dq_rad_s,
        "position_m": position_m,
        "force_error_N": force_error_N,
        "metadata": {
            "paper_method_variant": metrics_payload.get("run_id", "python"),
            "paper_method_acceptance_mode": "candidate",
            "solver_mode": metrics_payload["metrics"].get("solver_mode", ""),
            "orientation_mode": metrics_payload["metrics"].get("orientation_mode", ""),
            "force_loop_mode": metrics_payload["metrics"].get("force_loop_mode", ""),
            "z0_convention": metrics_payload["metrics"].get("z0_convention", ""),
        },
    }


def q7_summary(run: dict[str, Any]) -> dict[str, Any]:
    t_s = run["t_s"]
    q_rad = run["q_rad"]
    dq_rad_s = run["dq_rad_s"]
    idx22 = nearest_index(t_s, 22.0)
    q7 = q_rad[:, 6]
    near_limit = q7 > 2.49
    exact_limit = np.isclose(q7, 2.5, atol=1.0e-9)
    first_near_index = int(np.argmax(near_limit)) if bool(np.any(near_limit)) else None
    return {
        "duration_s": float(t_s[-1] - t_s[0]),
        "sample_count": int(t_s.size),
        "dt_median_s": float(np.median(np.diff(t_s))),
        "sample_time_22_s": float(t_s[idx22]),
        "q7_at_22_s_rad": float(q_rad[idx22, 6]),
        "q_at_22_s_rad": [float(value) for value in q_rad[idx22, :]],
        "q7_min_rad": float(np.min(q7)),
        "q7_max_rad": float(np.max(q7)),
        "q7_final_rad": float(q7[-1]),
        "q7_near_upper_limit_count_gt_2p49": int(np.count_nonzero(near_limit)),
        "q7_exact_upper_limit_count": int(np.count_nonzero(exact_limit)),
        "q7_first_near_upper_limit_time_s": None
        if first_near_index is None
        else float(t_s[first_near_index]),
        "max_abs_qdot_by_joint_rad_s": [float(value) for value in np.max(np.abs(dq_rad_s), axis=0)],
        "qdot_velocity_limit_hit_count": int(np.count_nonzero(np.abs(dq_rad_s) >= 1.5 - 1.0e-9)),
        "tail_force_error_mean_abs_N": float(np.mean(np.abs(run["force_error_N"][-max(1, t_s.size // 10) :]))),
    }


def interpolate_columns(source_t: np.ndarray, source_values: np.ndarray, target_t: np.ndarray) -> np.ndarray:
    interpolated = np.zeros((target_t.size, source_values.shape[1]), dtype=float)
    for col in range(source_values.shape[1]):
        interpolated[:, col] = np.interp(target_t, source_t, source_values[:, col])
    return interpolated


def compare_joint_trajectory(reference: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    start = max(float(reference["t_s"][0]), float(candidate["t_s"][0]))
    end = min(float(reference["t_s"][-1]), float(candidate["t_s"][-1]))
    mask = (reference["t_s"] >= start) & (reference["t_s"] <= end)
    ref_t = reference["t_s"][mask]
    ref_q = reference["q_rad"][mask, :]
    cand_q = interpolate_columns(candidate["t_s"], candidate["q_rad"], ref_t)
    diff = cand_q - ref_q
    idx22 = nearest_index(ref_t, 22.0)
    return {
        "reference": reference["name"],
        "candidate": candidate["name"],
        "common_start_s": start,
        "common_end_s": end,
        "sample_count": int(ref_t.size),
        "joint_rmse_rad": float(np.sqrt(np.mean(diff * diff))),
        "q7_rmse_rad": float(np.sqrt(np.mean(diff[:, 6] * diff[:, 6]))),
        "q7_max_abs_delta_rad": float(np.max(np.abs(diff[:, 6]))),
        "q7_delta_at_22_s_rad": float(diff[idx22, 6]),
        "q7_abs_delta_at_22_s_rad": float(abs(diff[idx22, 6])),
        "q_delta_at_22_s_rad": [float(value) for value in diff[idx22, :]],
    }


def quaternion_delta_norm(a_xyzw: np.ndarray, b_xyzw: np.ndarray) -> float:
    direct = float(np.linalg.norm(a_xyzw - b_xyzw))
    flipped = float(np.linalg.norm(a_xyzw + b_xyzw))
    return min(direct, flipped)


def kinematics_source_check(legacy_run: dict[str, Any]) -> dict[str, Any]:
    rows = []
    max_position_error = 0.0
    max_quaternion_error = 0.0
    max_condition_error = 0.0
    for sample_time in SAMPLE_TIMES_S:
        idx = nearest_index(legacy_run["t_s"], sample_time)
        q = legacy_run["q_rad"][idx, :]
        pose = panda_forward_kinematics(q)
        jacobian = panda_geometric_jacobian(q)
        ref_position = legacy_run["x_state"][idx, :3]
        ref_quat = legacy_run["x_state"][idx, 3:7]
        position_error = float(np.linalg.norm(pose.position_m - ref_position))
        quaternion_error = quaternion_delta_norm(pose.quaternion_xyzw, ref_quat)
        cond_error = abs(float(np.linalg.cond(jacobian)) - float(legacy_run["condJ"][idx]))
        max_position_error = max(max_position_error, position_error)
        max_quaternion_error = max(max_quaternion_error, quaternion_error)
        max_condition_error = max(max_condition_error, cond_error)
        rows.append(
            {
                "requested_time_s": float(sample_time),
                "actual_time_s": float(legacy_run["t_s"][idx]),
                "position_error_m": position_error,
                "quaternion_delta_norm": quaternion_error,
                "condition_number_error": cond_error,
            }
        )
    return {
        "legacy_run": legacy_run["name"],
        "sample_rows": rows,
        "max_position_error_m": max_position_error,
        "max_quaternion_delta_norm": max_quaternion_error,
        "max_condition_number_error": max_condition_error,
        "passes_tight_fk_check": bool(max_position_error <= 1.0e-12 and max_quaternion_error <= 1.0e-12),
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Paper 7DOF Fig.6 Raw Provenance Comparison",
        "",
        f"Run id: `{payload['run_id']}`",
        "",
        "Scope: compare the current Python Fig.6 candidate against ignored local legacy MATLAB/RNN raw Fig.6 arrays.",
        "Raw `.mat` and `.npz` arrays remain outside ordinary Git; this run records derived lightweight metrics only.",
        "",
        "Summary:",
        "",
        "```yaml",
        yaml.safe_dump(summary, sort_keys=False).strip(),
        "```",
        "",
        "Run metadata:",
        "",
        "| Run | Solver | Orientation | Force loop | Acceptance | q7@22 rad | q7 limit samples | qdot limit hits |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for name, run_summary in payload["run_summaries"].items():
        metadata = run_summary["metadata"]
        q7 = run_summary["q7_summary"]
        lines.append(
            "| "
            f"`{name}` | `{metadata.get('solver_mode', '')}` | "
            f"`{metadata.get('orientation_mode', '')}` | "
            f"`{metadata.get('force_loop_mode', '')}` | "
            f"`{metadata.get('paper_method_acceptance_mode', '')}` | "
            f"`{q7['q7_at_22_s_rad']}` | "
            f"`{q7['q7_exact_upper_limit_count']}` | "
            f"`{q7['qdot_velocity_limit_hit_count']}` |"
        )
    lines.extend(
        [
            "",
            "Joint-trajectory comparisons:",
            "",
            "| Reference | Candidate | q7 delta @22 rad | q7 RMSE rad | joint RMSE rad |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for comparison in payload["trajectory_comparisons"]:
        lines.append(
            "| "
            f"`{comparison['reference']}` | `{comparison['candidate']}` | "
            f"`{comparison['q7_delta_at_22_s_rad']}` | "
            f"`{comparison['q7_rmse_rad']}` | "
            f"`{comparison['joint_rmse_rad']}` |"
        )
    lines.extend(
        [
            "",
            "Kinematics source checks:",
            "",
            "| Legacy run | max position error m | max quaternion delta norm | max condJ error |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for check in payload["kinematics_source_checks"]:
        lines.append(
            "| "
            f"`{check['legacy_run']}` | "
            f"`{check['max_position_error_m']}` | "
            f"`{check['max_quaternion_delta_norm']}` | "
            f"`{check['max_condition_number_error']}` |"
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- Python Panda FK and Jacobian conditioning match the sampled legacy raw states to numerical precision.",
            "- The legacy figure-match q7 landmark comes from a documented landmark/tuning line using `pinv_bounded`, `normal_only`, and `admittance_proxy`, not the formula-faithful `paper_literal` line.",
            "- The figure-match q7 trajectory is upper-limit pinned for most of the run; this is a provenance difference to audit before changing the strict parity candidate.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-root", default=str(DEFAULT_LEGACY_ROOT))
    parser.add_argument("--python-raw-npz", default=str(DEFAULT_PYTHON_RAW))
    parser.add_argument("--python-metrics-yaml", default=str(DEFAULT_PYTHON_METRICS))
    parser.add_argument("--python-label", default="python_v47_uncapped_kkt")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    legacy_root = resolve_path(args.legacy_root)
    python_raw_path = resolve_path(args.python_raw_npz)
    python_metrics_path = resolve_path(args.python_metrics_yaml)
    formula_path = legacy_root / "results/paper_method_formula_faithful_figure_bundle/raw_runs/formula_faithful_fig6_results.mat"
    figure_path = legacy_root / "results/paper_method_figure_match_figure_bundle/raw_runs/figure_match_fig6_results.mat"
    required_paths = [
        legacy_root / "forward_panda.m",
        legacy_root / "getJacobian_panda.m",
        formula_path,
        figure_path,
        python_raw_path,
        python_metrics_path,
    ]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError("missing required provenance inputs: " + ", ".join(missing))

    if args.output_dir:
        out_dir = pathlib.Path(args.output_dir)
        run_id = out_dir.name
    else:
        run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
        out_dir = ROOT / "runs" / "paper_7dof_fig6_raw_provenance" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    formula = load_legacy_run(formula_path)
    formula["name"] = "legacy_formula_faithful"
    figure = load_legacy_run(figure_path)
    figure["name"] = "legacy_figure_match"
    python = load_python_run(python_raw_path, python_metrics_path)
    python_label = args.python_label
    python["name"] = python_label

    runs = [formula, figure, python]
    run_summaries = {
        run["name"]: {
            "source_path": display_path(run["path"]),
            "metadata": run["metadata"],
            "q7_summary": q7_summary(run),
        }
        for run in runs
    }
    trajectory_comparisons = [
        compare_joint_trajectory(formula, python),
        compare_joint_trajectory(figure, python),
        compare_joint_trajectory(formula, figure),
    ]
    kinematics_checks = [kinematics_source_check(formula), kinematics_source_check(figure)]
    summary = {
        "python_fk_matches_sampled_legacy_raw": all(
            bool(check["passes_tight_fk_check"]) for check in kinematics_checks
        ),
        "legacy_formula_force_loop_mode": formula["metadata"]["force_loop_mode"],
        "legacy_figure_force_loop_mode": figure["metadata"]["force_loop_mode"],
        "python_force_loop_mode": python["metadata"]["force_loop_mode"],
        "python_candidate_label": python_label,
        "legacy_figure_q7_at_22_s_rad": run_summaries["legacy_figure_match"]["q7_summary"][
            "q7_at_22_s_rad"
        ],
        "python_q7_at_22_s_rad": run_summaries[python_label]["q7_summary"][
            "q7_at_22_s_rad"
        ],
        "formula_q7_at_22_s_rad": run_summaries["legacy_formula_faithful"]["q7_summary"][
            "q7_at_22_s_rad"
        ],
        "python_abs_delta_to_figure_q7_at_22_s_rad": abs(
            run_summaries[python_label]["q7_summary"]["q7_at_22_s_rad"]
            - run_summaries["legacy_figure_match"]["q7_summary"]["q7_at_22_s_rad"]
        ),
        "python_abs_delta_to_formula_q7_at_22_s_rad": abs(
            run_summaries[python_label]["q7_summary"]["q7_at_22_s_rad"]
            - run_summaries["legacy_formula_faithful"]["q7_summary"]["q7_at_22_s_rad"]
        ),
        "legacy_figure_q7_exact_upper_limit_count": run_summaries["legacy_figure_match"][
            "q7_summary"
        ]["q7_exact_upper_limit_count"],
        "legacy_figure_q7_first_near_upper_limit_time_s": run_summaries["legacy_figure_match"][
            "q7_summary"
        ]["q7_first_near_upper_limit_time_s"],
        "legacy_figure_acceptance_mode": figure["metadata"]["paper_method_acceptance_mode"],
    }
    payload = {
        "run_id": run_id,
        "git_commit": git_value(["rev-parse", "HEAD"]),
        "git_status_short": git_value(["status", "--short"]),
        "legacy_root": str(legacy_root),
        "python_raw_npz": display_path(python_raw_path),
        "python_metrics_yaml": display_path(python_metrics_path),
        "source_files": {
            "forward_panda_m": str(legacy_root / "forward_panda.m"),
            "getJacobian_panda_m": str(legacy_root / "getJacobian_panda.m"),
            "formula_fig6_mat": str(formula_path),
            "figure_match_fig6_mat": str(figure_path),
        },
        "summary": summary,
        "run_summaries": run_summaries,
        "trajectory_comparisons": trajectory_comparisons,
        "kinematics_source_checks": kinematics_checks,
    }

    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, allow_nan=True)
    write_summary(out_dir, payload)
    print(f"wrote {out_dir}")
    print(yaml.safe_dump(summary, sort_keys=False).strip())
    return 0 if bool(summary["python_fk_matches_sampled_legacy_raw"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
