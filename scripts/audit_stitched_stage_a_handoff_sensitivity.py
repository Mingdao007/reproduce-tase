#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tase_repro.stitched_sensitivity import aggregate_stitched_sensitivity, summarize_stitched_case


DEFAULT_CASES: list[dict[str, Any]] = [
    {"name": "nominal", "parameters": {}},
    {"name": "base_z_minus_1mm", "parameters": {"base_z_offset_delta_m": -0.001}},
    {"name": "base_z_plus_1mm", "parameters": {"base_z_offset_delta_m": 0.001}},
    {"name": "stage_a_14s", "parameters": {"stage_a_duration_s": 14.0}},
    {"name": "stage_a_16s", "parameters": {"stage_a_duration_s": 16.0}},
    {"name": "qdot_limit_0p12", "parameters": {"qdot_limit_rad_s": 0.12}},
    {"name": "force_gain_5e-5", "parameters": {"force_gain": 5e-5}},
    {"name": "force_gain_2e-4", "parameters": {"force_gain": 2e-4}},
    {"name": "paper_time_scale_0p02", "parameters": {"paper_time_scale": 0.02}},
]

TIMING_MARGIN_CASES: list[dict[str, Any]] = [
    {"name": "nominal", "parameters": {}},
    {"name": "stage_a_14s_reference_fail", "parameters": {"stage_a_duration_s": 14.0}},
    {"name": "stage_a_14p5_recovery", "parameters": {"stage_a_duration_s": 14.5}},
    {
        "name": "qdot012_stage_a_17p5_reference_fail",
        "parameters": {"qdot_limit_rad_s": 0.12, "stage_a_duration_s": 17.5},
    },
    {
        "name": "qdot012_stage_a_18p0_recovery",
        "parameters": {"qdot_limit_rad_s": 0.12, "stage_a_duration_s": 18.0},
    },
    {"name": "paper_time_scale_0p012_recovery", "parameters": {"paper_time_scale": 0.012}},
    {"name": "paper_time_scale_0p0125_reference_fail", "parameters": {"paper_time_scale": 0.0125}},
]

CASE_SETS: dict[str, dict[str, Any]] = {
    "sensitivity": {
        "cases": DEFAULT_CASES,
        "run_subdir": "stitched_stage_a_handoff_sensitivity",
        "title": "Stitched Stage A Handoff Sensitivity Summary",
        "claim_scope": "diagnostic-label simulation sensitivity only; not robustness proof or hardware evidence.",
        "interpretation": [
            "Passing cases preserve the v63 diagnostic stitched gate under the listed perturbation only.",
            "Failing cases bound the nominal result and prevent a broad robustness claim.",
            "This audit does not change the strict paper-equivalent, v38 relaxed, or v63 diagnostic claim labels.",
        ],
        "warnings": [
            "diagnostic-label simulation sensitivity audit only",
            "not strict paper-equivalent feasibility",
            "not a formal robustness proof",
            "not hardware-ready",
        ],
    },
    "timing-margin": {
        "cases": TIMING_MARGIN_CASES,
        "run_subdir": "stitched_stage_a_handoff_timing_margin",
        "title": "Stitched Stage A Handoff Timing Margin Summary",
        "claim_scope": "diagnostic-label timing-margin audit only; not robustness proof or hardware evidence.",
        "interpretation": [
            "Passing recovery cases show timing or qdot-budget margins for the nominal diagnostic stitched policy.",
            "Reference-fail cases preserve the nearby failing boundaries from v64.",
            "This audit does not recover 1 mm base-z/contact perturbations and does not change paper-equivalent or hardware claims.",
        ],
        "warnings": [
            "diagnostic-label timing-margin audit only",
            "does not test base-z/contact path reoptimization",
            "not strict paper-equivalent feasibility",
            "not a formal robustness proof",
            "not hardware-ready",
        ],
    },
}

PARAMETER_FLAGS = {
    "base_z_offset_delta_m": "--base-z-offset-delta-m",
    "stage_a_duration_s": "--stage-a-duration-s",
    "stage_b_duration_s": "--stage-b-duration-s",
    "target_force_N": "--target-force-N",
    "force_gain": "--force-gain",
    "r": "--r",
    "qdot_limit_rad_s": "--qdot-limit-rad-s",
    "planar_kp": "--planar-kp",
    "paper_time_scale": "--paper-time-scale",
    "orientation_kp": "--orientation-kp",
}


def write_git_state(out_dir: pathlib.Path, *, command: list[str]) -> None:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
    lines = [
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
    (out_dir / "git_state.md").write_text("\n".join(lines), encoding="utf-8")


def command_for_case(case_dir: pathlib.Path, parameters: dict[str, Any]) -> list[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "evaluate_stitched_stage_a_handoff.py"),
        "--output-dir",
        str(case_dir),
    ]
    for key, value in parameters.items():
        if key not in PARAMETER_FLAGS:
            raise ValueError(f"unsupported sensitivity parameter: {key}")
        command.extend([PARAMETER_FLAGS[key], str(value)])
    return command


def run_case(case: dict[str, Any], *, cases_root: pathlib.Path) -> dict[str, Any]:
    case_name = str(case["name"])
    parameters = dict(case.get("parameters", {}))
    case_dir = cases_root / case_name
    case_dir.mkdir(parents=True, exist_ok=True)
    command = command_for_case(case_dir, parameters)
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    (case_dir / "command_stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (case_dir / "command_stderr.txt").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"{case_name} failed with exit code {completed.returncode}: {completed.stderr}")
    metrics = yaml.safe_load((case_dir / "metrics.yaml").read_text(encoding="utf-8"))
    return summarize_stitched_case(case_name=case_name, parameters=parameters, metrics=metrics)


def write_summary(
    out_dir: pathlib.Path,
    aggregate: dict[str, Any],
    cases: list[dict[str, Any]],
    *,
    case_set: dict[str, Any],
) -> None:
    lines = [
        f"# {case_set['title']}",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Stitched pass count: `{aggregate['stitched_pass_count']} / {aggregate['case_count']}`",
        f"- Failing cases: `{', '.join(aggregate['failing_cases']) or 'none'}`",
        f"- Claim scope: {case_set['claim_scope']}",
        "",
        "| case | pass | Stage A pass | Stage B pass | Stage A max qdot | terminal force err N | Stage B worst force err N | parameters |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in cases:
        params = ", ".join(f"{key}={value}" for key, value in row["parameters"].items()) or "nominal"
        worst = row["stage_b_worst"]
        lines.append(
            "| `{case}` | `{passed}` | `{stage_a}` | `{stage_b_pass}/{stage_b_count}` | `{qdot}` | `{terminal_force}` | `{stage_b_force}` | `{params}` |".format(
                case=row["case"],
                passed=row["stitched_passed"],
                stage_a=row["stage_a_passed"],
                stage_b_pass=row["stage_b_pass_count"],
                stage_b_count=row["stage_b_trajectory_count"],
                qdot=row["stage_a_max_qdot_rad_s"],
                terminal_force=row["stage_a_terminal_force_error_N"],
                stage_b_force=worst["max_tail_force_error_N"],
                params=params,
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            *[f"- {line}" for line in case_set["interpretation"]],
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-set", choices=sorted(CASE_SETS), default="sensitivity")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    case_set = CASE_SETS[args.case_set]

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / str(case_set["run_subdir"]) / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    cases_root = out_dir / "cases"

    case_summaries = [run_case(case, cases_root=cases_root) for case in case_set["cases"]]
    aggregate = aggregate_stitched_sensitivity(case_summaries)
    payload = {
        "run_id": run_id,
        "case_set": args.case_set,
        "source": "v63 stitched diagnostic Stage A tracker plus Stage B handoff",
        "case_count": aggregate["case_count"],
        "aggregate": aggregate,
        "cases": case_summaries,
        "warnings": case_set["warnings"],
    }
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    write_summary(out_dir, aggregate, case_summaries, case_set=case_set)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
