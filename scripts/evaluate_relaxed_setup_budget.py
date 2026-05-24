#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.relaxed_setup_budget import (
    RelaxedSetupBudget,
    evaluate_staged_run_root,
    load_acceptance_config,
)


def write_git_state(out_dir: pathlib.Path, *, command: list[str]) -> None:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
    content = "\n".join(
        [
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
    )
    (out_dir / "git_state.md").write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--acceptance-config", default="configs/ur10e_adapted_acceptance.yaml")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    config_path = (ROOT / args.acceptance_config).resolve()
    run_root = (ROOT / args.run_root).resolve()
    config = load_acceptance_config(config_path)
    budget = RelaxedSetupBudget.from_config(config)
    evaluation = evaluate_staged_run_root(run_root, budget)

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "relaxed_setup_budget_eval" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = {
        "run_id": run_id,
        "acceptance_config": str(config_path),
        **evaluation,
        "warnings": [
            "UR10e adapted relaxed setup label only",
            "does not change strict paper-equivalent full staged feasibility",
            "qdot saturation during setup is recorded but not gated by this relaxed budget",
            "simulation-only and not hardware-ready",
        ],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    summary_lines = [
        "# Relaxed Setup Budget Evaluation Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        "## Result",
        "",
        f"- Source run root: `{evaluation['run_root']}`",
        f"- Cases: `{evaluation['case_count']}`",
        f"- Relaxed setup passes: `{evaluation['relaxed_setup_pass_count']}`",
        f"- Trajectory feasibility passes: `{evaluation['trajectory_feasibility_pass_count']}`",
        "- UR10e adapted trajectory-after-relaxed-setup passes: "
        f"`{evaluation['ur10e_adapted_trajectory_after_relaxed_setup_pass_count']}`",
        f"- Strict full staged feasibility passes: `{evaluation['strict_full_staged_feasibility_pass_count']}`",
        "",
        "| trajectory | relaxed setup | trajectory | adapted label | setup drift m | setup qdot sat |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in evaluation["rows"]:
        summary_lines.append(
            "| `{trajectory}` | `{setup}` | `{trajectory_pass}` | `{adapted}` | `{drift}` | `{sat}` |".format(
                trajectory=row["trajectory"],
                setup=row["relaxed_setup_pass"],
                trajectory_pass=row["trajectory_feasibility_pass"],
                adapted=row["ur10e_adapted_trajectory_after_relaxed_setup_pass"],
                drift=row["setup_tangential_drift_m"],
                sat=row["setup_qdot_saturation_fraction"],
            )
        )
    summary_lines.extend(
        [
            "",
            "## Limits",
            "",
            "This is an acceptance-label evaluation. It does not convert the run into",
            "paper-equivalent full staged feasibility, and it is not hardware-ready.",
            "",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
