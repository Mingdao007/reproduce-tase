#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
from typing import Any

import numpy as np
import scipy.io
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

DEFAULT_LEGACY_ROOT = pathlib.Path(
    "/home/andy/ur10e_ros2_ws/experiments/"
    "20260523_tase_finite_time_ur10e_mujoco_reproduction/"
    "runs/full_paper_matlab/20260523T114034/worktree/RNN_F2"
)


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


def parse_matlab_scalar(value: str) -> str | float:
    token = value.strip()
    if token.startswith("'") and token.endswith("'"):
        return token[1:-1]
    if token.lower() == "inf":
        return float("inf")
    if token.lower() == "-inf":
        return float("-inf")
    try:
        return float(token)
    except ValueError:
        return token


def extract_assignments(source_text: str, prefix: str) -> dict[str, Any]:
    escaped = re.escape(prefix)
    pattern = re.compile(rf"{escaped}\.(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>[^;]+);(?P<comment>[^\n]*)")
    assignments: dict[str, Any] = {}
    for lineno, line in enumerate(source_text.splitlines(), start=1):
        match = pattern.search(line)
        if not match:
            continue
        comment = match.group("comment").strip()
        if comment.startswith("%"):
            comment = comment[1:].strip()
        assignments[match.group("name")] = {
            "value": parse_matlab_scalar(match.group("value")),
            "raw_value": match.group("value").strip(),
            "comment": comment,
            "line": lineno,
        }
    return assignments


def source_hits(source_text: str, needles: list[str]) -> list[dict[str, Any]]:
    hits = []
    for lineno, line in enumerate(source_text.splitlines(), start=1):
        if any(needle in line for needle in needles):
            hits.append({"line": lineno, "text": line.strip()})
    return hits


def matlab_string(value: Any) -> str:
    array = np.asarray(value)
    if array.shape == ():
        return str(array.item())
    if array.size == 1:
        return str(array.reshape(-1)[0])
    return str(value)


def load_raw_fig6_summary(path: pathlib.Path) -> dict[str, Any]:
    mat = scipy.io.loadmat(path, squeeze_me=True, struct_as_record=False)
    t_s = np.asarray(mat["t_save"], dtype=float).reshape(-1)
    q = np.asarray(mat["q_save"], dtype=float)
    dq = np.asarray(mat["dq_save"], dtype=float)
    force_error = np.asarray(mat["force_error_save"], dtype=float).reshape(-1)
    idx22 = int(np.argmin(np.abs(t_s - 22.0)))
    q7 = q[:, 6]
    return {
        "path": str(path),
        "paper_method_variant": matlab_string(mat.get("paper_method_variant", "")),
        "acceptance_mode": matlab_string(mat.get("paper_method_acceptance_mode", "")),
        "solver_mode": matlab_string(mat.get("solver_mode", "")),
        "orientation_mode": matlab_string(mat.get("orientation_mode", "")),
        "force_loop_mode": matlab_string(mat.get("force_loop_mode", "")),
        "q7_at_22_s_rad": float(q[idx22, 6]),
        "q7_exact_upper_limit_count": int(np.count_nonzero(np.isclose(q7, 2.5, atol=1.0e-9))),
        "q7_first_near_upper_limit_time_s": None
        if not bool(np.any(q7 > 2.49))
        else float(t_s[int(np.argmax(q7 > 2.49))]),
        "qdot_velocity_limit_hit_count": int(np.count_nonzero(np.abs(dq) >= 1.5 - 1.0e-9)),
        "tail_force_error_mean_abs_N": float(np.mean(np.abs(force_error[-max(1, t_s.size // 10) :]))),
    }


def assignment_value(assignments: dict[str, Any], name: str, default: Any = None) -> Any:
    if name not in assignments:
        return default
    return assignments[name]["value"]


def classify_source(
    *,
    formula: dict[str, Any],
    figure: dict[str, Any],
    raw_figure: dict[str, Any] | None,
) -> dict[str, Any]:
    nonpaper_knobs = []
    expected_formula = {
        "orientation_mode": "force_shortest_arc",
        "solver_mode": "kkt_projection",
        "force_loop_mode": "paper_literal",
        "acceptance_mode": "diagnostic",
    }
    for key, expected in expected_formula.items():
        actual = assignment_value(figure, key)
        if actual != expected:
            nonpaper_knobs.append(
                {
                    "field": key,
                    "figure_match_value": actual,
                    "formula_faithful_value": assignment_value(formula, key),
                    "paper_faithful_expected": expected,
                }
            )
    for key in ["alpha", "maxAngularSpeed", "kp", "q7NullspaceSpeed"]:
        value = assignment_value(figure, key)
        if value is not None:
            nonpaper_knobs.append(
                {
                    "field": key,
                    "figure_match_value": value,
                    "formula_faithful_value": assignment_value(formula, key),
                    "paper_faithful_expected": "not configured as formula-faithful tuning knob",
                }
            )
    q7_bias = assignment_value(figure, "q7NullspaceSpeed", 0.0)
    uses_q7_bias = bool(isinstance(q7_bias, (int, float)) and q7_bias != 0.0)
    figure_pins_q7 = bool(raw_figure and raw_figure.get("q7_exact_upper_limit_count", 0) > 0)
    return {
        "figure_match_is_formula_faithful": False,
        "nonpaper_tuning_knob_count": len(nonpaper_knobs),
        "nonpaper_tuning_knobs": nonpaper_knobs,
        "uses_explicit_q7_nullspace_bias": uses_q7_bias,
        "figure_match_pins_q7_upper_limit": figure_pins_q7,
        "recommended_next_action": (
            "implement a separately labeled Python figure-match/admittance_proxy candidate"
            " or revise the strict parity gate so q7 figure-match remains landmark provenance"
        ),
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Legacy Figure-Match Source Audit",
        "",
        f"Run id: `{payload['run_id']}`",
        "",
        "Scope: static and raw-output provenance audit for the legacy MATLAB/RNN `figure_match` line.",
        "This records lightweight derived metadata only; legacy source and raw `.mat` files remain external inputs.",
        "",
        "Summary:",
        "",
        "```yaml",
        yaml.safe_dump(summary, sort_keys=False).strip(),
        "```",
        "",
        "Figure-match tuning fields:",
        "",
        "| Field | Value | Source line | Comment |",
        "| --- | ---: | ---: | --- |",
    ]
    for key, item in payload["figure_match_assignments"].items():
        lines.append(f"| `{key}` | `{item['value']}` | `{item['line']}` | {item['comment']} |")
    lines.extend(
        [
            "",
            "Formula-faithful fields:",
            "",
            "| Field | Value | Source line | Comment |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for key, item in payload["formula_faithful_assignments"].items():
        lines.append(f"| `{key}` | `{item['value']}` | `{item['line']}` | {item['comment']} |")
    lines.extend(
        [
            "",
            "Non-paper-faithful tuning classification:",
            "",
            "| Field | Figure-match value | Formula-faithful value | Expected paper-faithful value |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for item in summary["nonpaper_tuning_knobs"]:
        lines.append(
            "| "
            f"`{item['field']}` | `{item['figure_match_value']}` | "
            f"`{item['formula_faithful_value']}` | {item['paper_faithful_expected']} |"
        )
    if payload["raw_fig6_summaries"]:
        lines.extend(
            [
                "",
                "Raw Fig.6 summaries:",
                "",
                "| Variant | Force loop | q7@22 rad | q7 exact upper-limit samples | qdot limit hits |",
                "| --- | --- | ---: | ---: | ---: |",
            ]
        )
        for item in payload["raw_fig6_summaries"].values():
            lines.append(
                "| "
                f"`{item['paper_method_variant']}` | `{item['force_loop_mode']}` | "
                f"`{item['q7_at_22_s_rad']}` | "
                f"`{item['q7_exact_upper_limit_count']}` | "
                f"`{item['qdot_velocity_limit_hit_count']}` |"
            )
    lines.extend(
        [
            "",
            "Implementation source hits:",
            "",
            "| File | Line | Text |",
            "| --- | ---: | --- |",
        ]
    )
    for file_label, hits in payload["implementation_hits"].items():
        for hit in hits:
            lines.append(f"| `{file_label}` | `{hit['line']}` | `{hit['text']}` |")
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The legacy `figure_match` line is explicitly configured as `landmark` acceptance and uses tuned values for solver, orientation, force loop, gains, and q7 nullspace bias.",
            "- The `q7NullspaceSpeed` knob is wired into the pseudoinverse nullspace branch, so the 2.5 rad q7 landmark is not an emergent formula-faithful consequence.",
            "- The strict paper-platform gate should keep this provenance boundary visible before using q7@22 as a paper-equivalence requirement.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-root", default=str(DEFAULT_LEGACY_ROOT))
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--skip-raw", action="store_true")
    args = parser.parse_args()

    legacy_root = resolve_path(args.legacy_root)
    config_path = legacy_root / "config_audit.m"
    method_path = legacy_root / "simulate_paper_method_branch.m"
    ideal_path = legacy_root / "simulate_paper_ideal_branch.m"
    required_paths = [config_path, method_path, ideal_path]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError("missing required source inputs: " + ", ".join(missing))

    config_text = config_path.read_text(encoding="utf-8")
    method_text = method_path.read_text(encoding="utf-8")
    ideal_text = ideal_path.read_text(encoding="utf-8")

    formula_assignments = extract_assignments(config_text, "cfg.paper_method.formula_faithful")
    figure_assignments = extract_assignments(config_text, "cfg.paper_method.figure_match")
    acceptance_assignments = extract_assignments(config_text, "cfg.paper_method.acceptance")
    normal_loop_assignments = extract_assignments(config_text, "cfg.paper_ideal.normalLoop")
    raw_summaries: dict[str, Any] = {}
    if not args.skip_raw:
        raw_paths = {
            "formula_faithful": legacy_root
            / "results/paper_method_formula_faithful_figure_bundle/raw_runs/formula_faithful_fig6_results.mat",
            "figure_match": legacy_root
            / "results/paper_method_figure_match_figure_bundle/raw_runs/figure_match_fig6_results.mat",
        }
        for name, path in raw_paths.items():
            if path.exists():
                raw_summaries[name] = load_raw_fig6_summary(path)

    summary = classify_source(
        formula=formula_assignments,
        figure=figure_assignments,
        raw_figure=raw_summaries.get("figure_match"),
    )
    summary.update(
        {
            "figure_match_force_loop_mode": assignment_value(figure_assignments, "force_loop_mode"),
            "figure_match_solver_mode": assignment_value(figure_assignments, "solver_mode"),
            "figure_match_orientation_mode": assignment_value(figure_assignments, "orientation_mode"),
            "figure_match_acceptance_mode": assignment_value(figure_assignments, "acceptance_mode"),
            "figure_match_q7_nullspace_speed": assignment_value(figure_assignments, "q7NullspaceSpeed"),
            "figure_match_alpha": assignment_value(figure_assignments, "alpha"),
            "figure_match_kp": assignment_value(figure_assignments, "kp"),
            "formula_force_loop_mode": assignment_value(formula_assignments, "force_loop_mode"),
            "formula_solver_mode": assignment_value(formula_assignments, "solver_mode"),
            "formula_orientation_mode": assignment_value(formula_assignments, "orientation_mode"),
            "raw_figure_match_q7_at_22_s_rad": raw_summaries.get("figure_match", {}).get("q7_at_22_s_rad"),
            "raw_figure_match_q7_exact_upper_limit_count": raw_summaries.get("figure_match", {}).get(
                "q7_exact_upper_limit_count"
            ),
        }
    )
    implementation_hits = {
        "simulate_paper_method_branch.m": source_hits(
            method_text,
            ["case 'figure_match'", "q7NullspaceSpeed", "forceLoopMode", "notes ="],
        ),
        "simulate_paper_ideal_branch.m": source_hits(
            ideal_text,
            ["case 'admittance_proxy'", "normal_target_accel", "q7NullspaceSpeed", "null_projector", "bias(7)"],
        ),
    }

    if args.output_dir:
        out_dir = pathlib.Path(args.output_dir)
        run_id = out_dir.name
    else:
        run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
        out_dir = ROOT / "runs" / "legacy_figure_match_source_audit" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "git_commit": git_value(["rev-parse", "HEAD"]),
        "git_status_short": git_value(["status", "--short"]),
        "legacy_root": str(legacy_root),
        "source_files": {
            "config_audit_m": str(config_path),
            "simulate_paper_method_branch_m": str(method_path),
            "simulate_paper_ideal_branch_m": str(ideal_path),
        },
        "summary": summary,
        "formula_faithful_assignments": formula_assignments,
        "figure_match_assignments": figure_assignments,
        "acceptance_assignments": acceptance_assignments,
        "normal_loop_assignments": normal_loop_assignments,
        "raw_fig6_summaries": raw_summaries,
        "implementation_hits": implementation_hits,
    }

    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, allow_nan=True)
    write_summary(out_dir, payload)
    print(f"wrote {out_dir}")
    print(yaml.safe_dump(summary, sort_keys=False).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
