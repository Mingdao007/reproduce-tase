#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import pathlib
import subprocess
import sys
from dataclasses import asdict
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.paper_7dof import (  # noqa: E402
    PaperSectionV7DofConfig,
    simulate_paper_section_v_7dof,
    summarize_paper_section_v_7dof,
)
from tase_repro.paper_platform_parity import parse_legacy_verification_markdown  # noqa: E402


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


def parse_force_integral_limits(value: str) -> list[float]:
    limits: list[float] = []
    for token in value.split(","):
        normalized = token.strip().lower()
        if not normalized:
            continue
        if normalized in {"inf", "+inf", "infinity", "+infinity", "uncapped"}:
            limits.append(float("inf"))
        else:
            limits.append(float(normalized))
    if not limits:
        raise ValueError("at least one force-integral limit is required")
    return limits


def force_integral_slug(value: float) -> str:
    if math.isinf(float(value)):
        return "uncapped"
    return "cap" + f"{float(value):.6g}".replace("-", "m").replace(".", "p")


def variant_label(solver_mode: str, orientation_mode: str, force_integral_limit: float) -> str:
    solver_slug = {
        "kkt_projection": "kkt",
        "pinv_bounded": "pinv",
    }[solver_mode]
    orientation_slug = {
        "force_shortest_arc": "force",
        "normal_only": "normal",
    }[orientation_mode]
    return f"{solver_slug}_{orientation_slug}_{force_integral_slug(force_integral_limit)}"


def resolve_repo_path(path_value: str) -> pathlib.Path:
    path = pathlib.Path(path_value)
    if path.is_absolute():
        return path
    return ROOT / path


def load_legacy_q7_references(config_path: pathlib.Path) -> dict[str, Any]:
    gate = yaml.safe_load(config_path.read_text(encoding="utf-8"))["paper_platform_parity"]
    references: dict[str, Any] = {}
    for name, info in gate["legacy_references"].items():
        path = resolve_repo_path(info["verification_path"])
        metrics = parse_legacy_verification_markdown(path.read_text(encoding="utf-8"))
        references[name] = {
            "label": info.get("label", name),
            "verification_path": display_path(path),
            "q7_sample_time_s": metrics.q7_sample_time_s,
            "q7_at_22_s_rad": metrics.q7_at_22_s_rad,
        }
    return {
        "primary_convergence_reference": gate["primary_convergence_reference"],
        "fig6_landmark_reference": gate["fig6_landmark_reference"],
        "q7_at_22_abs_error_rad_vs_figure_match": float(
            gate["thresholds"]["q7_at_22_abs_error_rad_vs_figure_match"]
        ),
        "references": references,
    }


def with_q7_deltas(metrics: dict[str, Any], references: dict[str, Any]) -> dict[str, Any]:
    q7_value = metrics.get("fig6_q7_at_22s_rad")
    if q7_value is None:
        metrics["fig6_q7_available"] = False
        return metrics
    metrics["fig6_q7_available"] = True
    q7 = float(q7_value)
    figure_name = references["fig6_landmark_reference"]
    formula_name = references["primary_convergence_reference"]
    figure_q7 = float(references["references"][figure_name]["q7_at_22_s_rad"])
    formula_q7 = float(references["references"][formula_name]["q7_at_22_s_rad"])
    tolerance = float(references["q7_at_22_abs_error_rad_vs_figure_match"])
    metrics.update(
        {
            "fig6_q7_reference_figure_match_rad": figure_q7,
            "fig6_q7_reference_formula_faithful_rad": formula_q7,
            "fig6_q7_abs_error_to_figure_match_rad": abs(q7 - figure_q7),
            "fig6_q7_abs_error_to_formula_faithful_rad": abs(q7 - formula_q7),
            "fig6_q7_matches_figure_match_tolerance": abs(q7 - figure_q7) <= tolerance,
        }
    )
    return metrics


def build_summary(payload: dict[str, Any]) -> dict[str, Any]:
    q7_rows = [
        item for item in payload["variants"] if item["metrics"].get("fig6_q7_available", False)
    ]
    q7_values = [float(item["metrics"]["fig6_q7_at_22s_rad"]) for item in q7_rows]
    figure_name = payload["legacy_q7_references"]["fig6_landmark_reference"]
    figure_q7 = float(payload["legacy_q7_references"]["references"][figure_name]["q7_at_22_s_rad"])
    tolerance = float(payload["legacy_q7_references"]["q7_at_22_abs_error_rad_vs_figure_match"])
    if q7_rows:
        closest = min(
            q7_rows,
            key=lambda item: abs(float(item["metrics"]["fig6_q7_at_22s_rad"]) - figure_q7),
        )
        pass_count = sum(
            1
            for item in q7_rows
            if bool(item["metrics"].get("fig6_q7_matches_figure_match_tolerance", False))
        )
        return {
            "all_execution_success": all(
                bool(item["metrics"].get("execution_success", False)) for item in payload["variants"]
            ),
            "all_q7_available": len(q7_rows) == len(payload["variants"]),
            "q7_min_rad": min(q7_values),
            "q7_max_rad": max(q7_values),
            "q7_range_rad": max(q7_values) - min(q7_values),
            "figure_match_q7_rad": figure_q7,
            "figure_match_tolerance_rad": tolerance,
            "figure_match_pass_count": pass_count,
            "variant_count": len(payload["variants"]),
            "closest_variant": closest["variant_label"],
            "closest_variant_q7_rad": float(closest["metrics"]["fig6_q7_at_22s_rad"]),
            "closest_variant_abs_error_to_figure_match_rad": float(
                closest["metrics"]["fig6_q7_abs_error_to_figure_match_rad"]
            ),
        }
    return {
        "all_execution_success": all(
            bool(item["metrics"].get("execution_success", False)) for item in payload["variants"]
        ),
        "all_q7_available": False,
        "variant_count": len(payload["variants"]),
        "reason": "duration does not cover the q7 sample time",
    }


def write_variant_summary(out_dir: pathlib.Path, row: dict[str, Any]) -> None:
    metrics = row["metrics"]
    lines = [
        "# Paper 7DOF q7 Variant Probe Row",
        "",
        f"Variant: `{row['variant_label']}`",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key in [
        "execution_success",
        "contact_force_tail_success",
        "duration_s",
        "solver_mode",
        "orientation_mode",
        "force_integral_limit",
        "fig6_q7_available",
        "fig6_q7_at_22s_rad",
        "fig6_q7_abs_error_to_figure_match_rad",
        "fig6_q7_abs_error_to_formula_faithful_rad",
        "tail_force_error_mean_N",
        "tail_position_error_mean_m",
        "tail_orientation_error_mean_rad",
        "max_abs_qdot_rad_s",
        "q_bound_violation_count",
        "qdot_bound_violation_count",
    ]:
        if key in metrics:
            lines.append(f"| `{key}` | `{metrics[key]}` |")
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_run_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Paper 7DOF q7 Variant Probe",
        "",
        f"Run id: `{payload['run_id']}`",
        "",
        "Scope: supported Python 7DOF Section V variants for isolating the Fig.6 q7-at-22 s mismatch.",
        "This is a diagnostic sensitivity probe, not a strict parity gate update.",
        "",
        "Summary:",
        "",
        "```yaml",
        yaml.safe_dump(summary, sort_keys=False).strip(),
        "```",
        "",
        "| Variant | Solver | Orientation | Force integral | q7@22 rad | Delta to figure-match rad | Tail force error N | Execution |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["variants"]:
        metrics = row["metrics"]
        lines.append(
            "| "
            f"`{row['variant_label']}` | "
            f"`{metrics['solver_mode']}` | "
            f"`{metrics['orientation_mode']}` | "
            f"`{metrics['force_integral_limit']}` | "
            f"`{metrics.get('fig6_q7_at_22s_rad', 'unavailable')}` | "
            f"`{metrics.get('fig6_q7_abs_error_to_figure_match_rad', 'unavailable')}` | "
            f"`{metrics['tail_force_error_mean_N']}` | "
            f"`{metrics['execution_success']}` |"
        )
    lines.extend(
        [
            "",
            "Legacy q7 references:",
            "",
            "```yaml",
            yaml.safe_dump(payload["legacy_q7_references"], sort_keys=False).strip(),
            "```",
            "",
            "Interpretation:",
            "",
            "- If `figure_match_pass_count` is zero, the q7 landmark mismatch persists across this supported variant matrix.",
            "- This probe does not validate Panda/Franka DH provenance or the legacy figure-match tuning source.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-platform-parity-config", default="configs/paper_platform_parity.yaml")
    parser.add_argument("--duration-s", type=float, default=30.0)
    parser.add_argument("--dt-s", type=float, default=0.002)
    parser.add_argument("--solver-modes", nargs="+", choices=["kkt_projection", "pinv_bounded"], default=None)
    parser.add_argument("--orientation-modes", nargs="+", choices=["force_shortest_arc", "normal_only"], default=None)
    parser.add_argument("--force-integral-limits", default="inf,0.1")
    parser.add_argument("--communication-delay-s", type=float, default=0.032)
    parser.add_argument("--force-integral-leak", type=float, default=0.0)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    solver_modes = args.solver_modes or ["kkt_projection", "pinv_bounded"]
    orientation_modes = args.orientation_modes or ["force_shortest_arc", "normal_only"]
    force_integral_limits = parse_force_integral_limits(args.force_integral_limits)
    config_path = resolve_repo_path(args.paper_platform_parity_config)
    legacy_references = load_legacy_q7_references(config_path)

    if args.output_dir:
        out_dir = pathlib.Path(args.output_dir)
        run_id = out_dir.name
    else:
        run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
        out_dir = ROOT / "runs" / "paper_7dof_q7_variant_probe" / run_id
    git_commit = git_value(["rev-parse", "HEAD"])
    git_status_short = git_value(["status", "--short"])
    out_dir.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "run_id": run_id,
        "git_commit": git_commit,
        "git_status_short": git_status_short,
        "paper_platform_parity_config": display_path(config_path),
        "legacy_q7_references": legacy_references,
        "base_config": {
            "duration_s": args.duration_s,
            "dt_s": args.dt_s,
            "communication_delay_s": args.communication_delay_s,
            "force_integral_leak": args.force_integral_leak,
        },
        "variants": [],
    }

    for solver_mode in solver_modes:
        for orientation_mode in orientation_modes:
            for force_integral_limit in force_integral_limits:
                label = variant_label(solver_mode, orientation_mode, force_integral_limit)
                config = PaperSectionV7DofConfig(
                    duration_s=args.duration_s,
                    dt_s=args.dt_s,
                    solver_mode=solver_mode,
                    orientation_mode=orientation_mode,
                    communication_delay_s=args.communication_delay_s,
                    force_integral_limit=force_integral_limit,
                    force_integral_leak=args.force_integral_leak,
                )
                result = simulate_paper_section_v_7dof(config)
                metrics = summarize_paper_section_v_7dof(result)
                metrics.update(
                    {
                        "claim_level": "paper_platform_7dof_q7_variant_probe",
                        "variant_label": label,
                        "force_integral_limit": force_integral_limit,
                        "force_integral_slug": force_integral_slug(force_integral_limit),
                    }
                )
                metrics = with_q7_deltas(metrics, legacy_references)
                row_dir = out_dir / label
                row_dir.mkdir(parents=True, exist_ok=True)
                row_payload = {
                    "run_id": run_id,
                    "git_commit": git_commit,
                    "git_status_short": git_status_short,
                    "variant_label": label,
                    "metrics": metrics,
                    "config": asdict(config),
                }
                with (row_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
                    yaml.safe_dump(row_payload, f, sort_keys=False)
                with (row_dir / "metrics.json").open("w", encoding="utf-8") as f:
                    json.dump(row_payload, f, indent=2)
                write_variant_summary(row_dir, row_payload)
                payload["variants"].append(
                    {
                        "variant_label": label,
                        "metrics_path": display_path(row_dir / "metrics.yaml"),
                        "metrics": metrics,
                    }
                )

    payload["summary"] = build_summary(payload)
    with (out_dir / "summary.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False)
    with (out_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    write_run_summary(out_dir, payload)
    print(f"wrote {out_dir}")
    print(yaml.safe_dump(payload["summary"], sort_keys=False).strip())
    return 0 if bool(payload["summary"]["all_execution_success"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
