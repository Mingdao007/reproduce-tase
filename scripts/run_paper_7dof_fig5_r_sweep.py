#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from dataclasses import asdict

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.paper_7dof import (  # noqa: E402
    PaperSectionV7DofConfig,
    simulate_paper_section_v_7dof,
    summarize_paper_section_v_7dof,
)


def git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except subprocess.CalledProcessError:
        return "unavailable"


def r_slug(value: float) -> str:
    return f"r_{value:.1f}".replace(".", "p")


def display_path(path: pathlib.Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_run_summary(out_dir: pathlib.Path, payload: dict) -> None:
    lines = [
        "# Paper 7DOF Fig.5 r Sweep",
        "",
        f"Run id: `{payload['run_id']}`",
        "",
        "Scope: Python 7DOF Section V diagnostic coverage for Fig.5 r-sweep windows.",
        "This is not paper-equivalent Fig.5 numerical parity by itself.",
        "",
        "| r | execution | tail force pass | task residual RMS | metrics |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    for item in payload["sweep"]:
        metrics = item["metrics"]
        lines.append(
            "| "
            f"`{item['r']}` | `{metrics['execution_success']}` | "
            f"`{metrics['contact_force_tail_success']}` | "
            f"`{metrics['task_residual_rms']}` | "
            f"`{item['metrics_path']}` |"
        )
    lines.extend(
        [
            "",
            "Config snapshot:",
            "",
            "```yaml",
            yaml.safe_dump(payload["base_config"], sort_keys=False).strip(),
            "```",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_single_summary(out_dir: pathlib.Path, payload: dict) -> None:
    metrics = payload["metrics"]
    lines = [
        "# Paper 7DOF Fig.5 r Sweep Row",
        "",
        f"Run id: `{payload['run_id']}`",
        f"r: `{metrics['fig5_r_value']}`",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key in [
        "execution_success",
        "contact_force_tail_success",
        "duration_s",
        "sample_count",
        "fig5_r_value",
        "fig5_window_s",
        "task_residual_rms",
        "tail_position_error_mean_m",
        "tail_orientation_error_mean_rad",
        "tail_force_error_mean_N",
        "q_bound_violation_count",
        "qdot_bound_violation_count",
    ]:
        lines.append(f"| `{key}` | `{metrics[key]}` |")
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-truth-config", default="configs/paper_truth.yaml")
    parser.add_argument("--duration-s", type=float, default=2.0)
    parser.add_argument("--dt-s", type=float, default=0.002)
    parser.add_argument("--solver-mode", choices=["kkt_projection", "pinv_bounded"], default="kkt_projection")
    parser.add_argument("--orientation-mode", choices=["force_shortest_arc", "normal_only"], default="force_shortest_arc")
    parser.add_argument("--communication-delay-s", type=float, default=0.032)
    parser.add_argument("--force-integral-limit", type=float, default=0.1)
    parser.add_argument("--force-integral-leak", type=float, default=0.0)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    truth_path = ROOT / args.paper_truth_config
    truth = yaml.safe_load(truth_path.read_text(encoding="utf-8"))
    r_values = [float(value) for value in truth["paper"]["section_v"]["r_sweep"]]
    if args.output_dir:
        out_dir = pathlib.Path(args.output_dir)
        run_id = out_dir.name
    else:
        run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
        out_dir = ROOT / "runs" / "paper_7dof_fig5_r_sweep" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    git_commit = git_value(["rev-parse", "HEAD"])
    git_status_short = git_value(["status", "--short"])
    base_config = PaperSectionV7DofConfig(
        duration_s=args.duration_s,
        dt_s=args.dt_s,
        solver_mode=args.solver_mode,
        orientation_mode=args.orientation_mode,
        communication_delay_s=args.communication_delay_s,
        force_integral_limit=args.force_integral_limit,
        force_integral_leak=args.force_integral_leak,
    )
    summary_payload = {
        "run_id": run_id,
        "git_commit": git_commit,
        "git_status_short": git_status_short,
        "paper_truth_config": args.paper_truth_config,
        "base_config": asdict(base_config),
        "sweep": [],
    }

    for r_value in r_values:
        row_dir = out_dir / r_slug(r_value)
        row_dir.mkdir(parents=True, exist_ok=True)
        config = PaperSectionV7DofConfig(
            **{**asdict(base_config), "finite_time_power": r_value}
        )
        result = simulate_paper_section_v_7dof(config)
        metrics = summarize_paper_section_v_7dof(result)
        metrics.update(
            {
                "fig5_r_value": r_value,
                "fig5_window_s": float(args.duration_s),
                "claim_level": "paper_platform_7dof_fig5_r_sweep_diagnostic",
            }
        )
        row_payload = {
            "run_id": run_id,
            "git_commit": git_commit,
            "git_status_short": git_status_short,
            "metrics": metrics,
            "config": asdict(config),
        }
        with (row_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
            yaml.safe_dump(row_payload, f, sort_keys=False)
        with (row_dir / "metrics.json").open("w", encoding="utf-8") as f:
            json.dump(row_payload, f, indent=2)
        write_single_summary(row_dir, row_payload)
        summary_payload["sweep"].append(
            {
                "r": r_value,
                "metrics_path": display_path(row_dir / "metrics.yaml"),
                "metrics": metrics,
            }
        )

    with (out_dir / "summary.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(summary_payload, f, sort_keys=False)
    with (out_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)
    write_run_summary(out_dir, summary_payload)
    print(f"wrote {out_dir}")
    return 0 if all(item["metrics"]["execution_success"] for item in summary_payload["sweep"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
