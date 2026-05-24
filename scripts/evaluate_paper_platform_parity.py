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

from tase_repro.paper_platform_parity import evaluate_paper_platform_parity  # noqa: E402


def git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except subprocess.CalledProcessError:
        return "unavailable"


def write_summary(out_dir: pathlib.Path, run_id: str, payload: dict) -> None:
    result = payload["result"]
    lines = [
        "# Paper Platform Parity Gate",
        "",
        f"Run id: `{run_id}`",
        "",
        f"Parity pass: `{result['paper_platform_parity_pass']}`",
        "",
        "Candidate:",
        "",
        f"- Label: `{result['candidate']['label']}`",
        f"- Metrics: `{result['candidate']['metrics_path']}`",
        f"- Raw arrays: `{result['candidate']['raw_npz_path']}`",
        "",
        "Strict checks:",
        "",
        "| Check | Pass | Detail |",
        "| --- | ---: | --- |",
    ]
    for name in result["strict_required_checks"]:
        check = result["checks"][name]
        detail = _check_detail(check)
        lines.append(f"| `{name}` | `{check['pass']}` | {detail} |")
    lines.extend(
        [
            "",
            "Legacy references:",
            "",
            "| Reference | Acceptance | Overall | Tail force N | Tail position m | Tail orientation rad |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, metrics in result["legacy_references"].items():
        lines.append(
            "| "
            f"`{name}` | `{metrics['acceptance_mode']}` | `{metrics['overall_pass']}` | "
            f"`{metrics['tail_force_error_mean_N']}` | "
            f"`{metrics['tail_position_error_mean_m']}` | "
            f"`{metrics['tail_orientation_error_mean_rad']}` |"
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            result["interpretation"],
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _check_detail(check: dict) -> str:
    parts = []
    for key in [
        "candidate_value",
        "reference_value",
        "abs_delta",
        "delta_tolerance",
        "candidate_duration_s",
        "required_duration_s",
        "candidate_q7_rad",
        "reference_q7_rad",
        "abs_delta_rad",
        "tolerance_rad",
        "missing_r_values",
        "force_integral_limit",
        "reason",
    ]:
        if key in check:
            parts.append(f"`{key}={check[key]}`")
    return ", ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/paper_platform_parity.yaml")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--fail-on-parity-failure", action="store_true")
    args = parser.parse_args()

    if args.output_dir:
        out_dir = pathlib.Path(args.output_dir)
        run_id = out_dir.name
    else:
        run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
        out_dir = ROOT / "runs" / "paper_platform_parity_eval" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    result = evaluate_paper_platform_parity(ROOT / args.config, ROOT)
    payload = {
        "run_id": run_id,
        "git_commit": git_value(["rev-parse", "HEAD"]),
        "git_status_short": git_value(["status", "--short"]),
        "config_path": args.config,
        "result": result,
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    write_summary(out_dir, run_id, payload)
    print(f"wrote {out_dir}")
    print(yaml.safe_dump({"paper_platform_parity_pass": result["paper_platform_parity_pass"]}, sort_keys=False).strip())
    if args.fail_on_parity_failure and not result["paper_platform_parity_pass"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
