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

from tase_repro.terminal_setup_gate import (
    TerminalSetupDiagnosticGate,
    evaluate_terminal_setup_metrics,
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
    parser.add_argument("--setup-metrics", required=True)
    parser.add_argument("--acceptance-config", default="configs/ur10e_adapted_acceptance.yaml")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    metrics_path = (ROOT / args.setup_metrics).resolve()
    config_path = (ROOT / args.acceptance_config).resolve()
    with metrics_path.open("r", encoding="utf-8") as f:
        source_metrics = yaml.safe_load(f)
    gate = TerminalSetupDiagnosticGate.from_config(load_acceptance_config(config_path))
    evaluation = evaluate_terminal_setup_metrics(source_metrics, gate)

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "terminal_setup_gate_eval" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = {
        "run_id": run_id,
        "setup_metrics": str(metrics_path),
        "acceptance_config": str(config_path),
        **evaluation,
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(metrics, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    best = evaluation["best_candidate"]
    summary_lines = [
        "# Terminal Setup Diagnostic Gate Evaluation Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        "## Result",
        "",
        f"- Source metrics: `{metrics_path}`",
        f"- Source candidates: `{evaluation['source_candidate_count']}`",
        f"- Claim scope: `{gate.claim_scope}`",
        f"- Pass count: `{evaluation['pass_count']}`",
        f"- Passed seed labels: `{','.join(evaluation['passed_seed_labels']) or 'none'}`",
        f"- Best seed: `{best['seed_label']}`",
        f"- Best pass: `{best['passed']}`",
        f"- Best failed criteria: `{';'.join(best['failed_criteria']) or 'none'}`",
        f"- Best max gate ratio: `{best['max_gate_ratio']}`",
        f"- Best force error N: `{best['source_force_error_N']}`",
        f"- Best x/y error m: `{best['source_tangential_error_m']}`",
        f"- Best orientation error rad: `{best['source_orientation_error_rad']}`",
        "",
        "## Limits",
        "",
        "This is a diagnostic terminal setup gate only. It does not prove path",
        "feasibility, trajectory feasibility, paper-equivalent full staged",
        "feasibility, or hardware readiness.",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
