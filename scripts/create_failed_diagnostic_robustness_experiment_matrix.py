#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import shlex
import subprocess
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

DIAGNOSTIC_MATRIX_METRICS = (
    ROOT / "runs" / "diagnostic_robustness_matrix_candidate" / "20260525T053101" / "metrics.yaml"
)

EXPECTED_FAILED_CELLS = [
    "base_z_plus1mm",
    "positive_fast_timing_0p0075",
    "positive_orientation_gate_0p119",
    "weighted_plus1mm_0p119_gate",
]


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)


def git_value(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def write_git_state(out_dir: pathlib.Path, *, command: list[str]) -> None:
    branch = git_value(["branch", "--show-current"])
    commit = git_value(["rev-parse", "HEAD"])
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


def relative(path: pathlib.Path) -> str:
    return str(path.relative_to(ROOT))


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def script_path(script_name: str) -> pathlib.Path:
    path = ROOT / "scripts" / script_name
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def experiment(
    *,
    cell_id: str,
    title: str,
    source_failed_cell: dict[str, Any],
    script_name: str,
    args: list[str],
    output_dir: pathlib.Path,
    closure_criteria: list[str],
    expected_artifacts: list[str],
    notes: list[str],
) -> dict[str, Any]:
    script = script_path(script_name)
    command = [sys.executable, str(script), "--output-dir", str(output_dir), *args]
    return {
        "id": cell_id,
        "title": title,
        "status": "planned_not_executed",
        "execution_scope": "offline_simulation_only",
        "source_failed_cell": {
            "id": source_failed_cell["id"],
            "status": source_failed_cell["status"],
            "blocker_ids": list(source_failed_cell.get("blocker_ids", [])),
            "source": source_failed_cell["source"],
        },
        "command": command,
        "command_shell": shell_join(command),
        "output_dir": str(output_dir),
        "closure_criteria": closure_criteria,
        "expected_artifacts": expected_artifacts,
        "notes": notes,
    }


def failed_cells_by_id(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cells = {
        item["id"]: item
        for item in matrix["matrix_definition"]["cells"]
        if item["status"] == "failed"
    }
    missing = [cell_id for cell_id in EXPECTED_FAILED_CELLS if cell_id not in cells]
    if missing:
        raise ValueError(f"missing expected failed cells: {missing}")
    unexpected = sorted(set(cells) - set(EXPECTED_FAILED_CELLS))
    if unexpected:
        raise ValueError(f"unexpected failed cells: {unexpected}")
    return cells


def build_experiments(*, run_id: str, matrix: dict[str, Any], out_dir: pathlib.Path) -> list[dict[str, Any]]:
    cells = failed_cells_by_id(matrix)
    experiment_root = out_dir / "experiments"
    return [
        experiment(
            cell_id="base_z_plus1mm",
            title="Focused +1.0 mm base-z start/terminal/path bracket",
            source_failed_cell=cells["base_z_plus1mm"],
            script_name="audit_stage_a_base_z_bracket.py",
            args=[
                "--base-z-deltas-mm",
                "1.0",
                "--stage-a-durations-s",
                "15.0,16.0,18.0",
            ],
            output_dir=experiment_root / "base_z_plus1mm",
            closure_criteria=[
                "delta_p1p000mm has start, terminal, path geometry, and duration recovery in the generated metrics.",
                "Any recovered result remains diagnostic until contact geometry and gate acceptance are closed.",
            ],
            expected_artifacts=["metrics.yaml", "metrics.json", "summary.md", "git_state.md"],
            notes=[
                "Targets the v98 base_z_plus1mm failed cell.",
                "Extends tested Stage A durations but does not alter accepted claim scope.",
            ],
        ),
        experiment(
            cell_id="positive_fast_timing_0p0075",
            title="Focused +1.0 mm positive fast-timing stitched sensitivity",
            source_failed_cell=cells["positive_fast_timing_0p0075"],
            script_name="audit_positive_stitched_sensitivity.py",
            args=[
                "--base-z-deltas-mm",
                "1.0",
                "--scenarios",
                "paper_time_scale_0p0075",
            ],
            output_dir=experiment_root / "positive_fast_timing_0p0075",
            closure_criteria=[
                "paper_time_scale_0p0075 at delta_p1p000mm has stitched_passed = true.",
                "Qdot saturation and tail qdot utilization remain within the diagnostic gate for all four trajectories.",
            ],
            expected_artifacts=["metrics.yaml", "metrics.json", "summary.md", "git_state.md"],
            notes=[
                "Targets the v98 positive_fast_timing_0p0075 failed cell.",
                "Does not make the faster timing a canonical controller default.",
            ],
        ),
        experiment(
            cell_id="positive_orientation_gate_0p119",
            title="Focused +1.0 mm positive orientation-gate boundary",
            source_failed_cell=cells["positive_orientation_gate_0p119"],
            script_name="audit_positive_orientation_gate_boundary.py",
            args=[
                "--base-z-delta-mm",
                "1.0",
                "--orientation-gates",
                "0.119,0.11925,0.1195,0.11975,0.1199,0.11995,0.11997,0.11998,0.12",
            ],
            output_dir=experiment_root / "positive_orientation_gate_0p119",
            closure_criteria=[
                "The boundary run identifies whether the +1.0 mm row can pass at or below 0.119 rad.",
                "Any gate above 0.119 rad remains not accepted without approved calibration evidence.",
            ],
            expected_artifacts=["metrics.yaml", "metrics.json", "summary.md", "git_state.md"],
            notes=[
                "Targets the v98 positive_orientation_gate_0p119 failed cell.",
                "This is a boundary measurement, not gate acceptance.",
            ],
        ),
        experiment(
            cell_id="weighted_plus1mm_0p119_gate",
            title="Focused weighted +1.0 mm gate/time boundary",
            source_failed_cell=cells["weighted_plus1mm_0p119_gate"],
            script_name="audit_weighted_gate_time_matrix.py",
            args=[
                "--base-z-deltas-mm",
                "1.0",
                "--boundary-base-z-delta-mm",
                "1.0",
                "--orientation-gates",
                "0.119,0.11925,0.1195,0.11955,0.1196,0.1197,0.11995",
            ],
            output_dir=experiment_root / "weighted_plus1mm_0p119_gate",
            closure_criteria=[
                "Both weighted scenarios pass the +1.0 mm row at the current 0.119 rad gate, or the run reports the minimum passing diagnostic gate.",
                "Any gate relaxation remains not accepted without approved calibration evidence.",
            ],
            expected_artifacts=["metrics.yaml", "metrics.json", "summary.md", "git_state.md"],
            notes=[
                "Targets the v98 weighted_plus1mm_0p119_gate failed cell.",
                "Runs the weighted matrix machinery on a focused +1.0 mm slice.",
            ],
        ),
    ]


def summarize_experiments(experiments: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "experiment_count": len(experiments),
        "planned_not_executed_count": sum(
            1 for item in experiments if item["status"] == "planned_not_executed"
        ),
        "cell_ids": [item["id"] for item in experiments],
        "all_expected_scripts_exist": all((ROOT / item["command"][1]).exists() for item in experiments),
        "all_commands_have_output_dirs": all("--output-dir" in item["command"] for item in experiments),
    }


def build_matrix(*, run_id: str, out_dir: pathlib.Path) -> dict[str, Any]:
    matrix = load_yaml(DIAGNOSTIC_MATRIX_METRICS)
    experiments = build_experiments(run_id=run_id, matrix=matrix, out_dir=out_dir)
    summary = summarize_experiments(experiments)
    return {
        "audit_source": "v99 failed diagnostic robustness experiment matrix",
        "run_id": run_id,
        "status": "planned_not_executed",
        "source_files": {
            "diagnostic_robustness_matrix_candidate": relative(DIAGNOSTIC_MATRIX_METRICS),
        },
        "source_failed_cell_ids": list(matrix["matrix_summary"]["failed_cell_ids"]),
        "experiments": experiments,
        "experiment_summary": summary,
        "claim_boundary": {
            "do_not_mark_goal_complete": True,
            "robustness_claim": False,
            "paper_equivalent_feasibility": False,
            "contact_calibration_claim": False,
            "orientation_gate_acceptance": False,
            "hardware_readiness": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "hardware_readiness_claim": False,
        },
        "next_offline_actions": [
            "Run one planned experiment command at a time if offline compute budget is available.",
            "After any command runs, add a separate audit that compares its metrics against the failed v98 cell closure criteria.",
            "Keep all gate-relaxation or contact-model interpretations blocked until approved read-only evidence exists.",
        ],
    }


def write_commands(out_dir: pathlib.Path, experiments: list[dict[str, Any]]) -> None:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Offline diagnostic robustness experiments planned by v99.",
        "# These commands do not use live hardware, but they may be compute-heavy.",
        "",
    ]
    for item in experiments:
        lines.extend(
            [
                f"# {item['id']}: {item['title']}",
                item["command_shell"],
                "",
            ]
        )
    commands_path = out_dir / "commands.sh"
    commands_path.write_text("\n".join(lines), encoding="utf-8")
    commands_path.chmod(0o755)


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["experiment_summary"]
    lines = [
        "# Failed Diagnostic Robustness Experiment Matrix",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Status: `{payload['status']}`",
        f"- Experiment count: `{summary['experiment_count']}`",
        f"- Planned-not-executed count: `{summary['planned_not_executed_count']}`",
        f"- Source failed cells: `{payload['source_failed_cell_ids']}`",
        f"- Commands file: `{out_dir / 'commands.sh'}`",
        "",
        "## Experiments",
        "",
    ]
    for item in payload["experiments"]:
        lines.extend(
            [
                f"### {item['id']}",
                "",
                f"- Title: {item['title']}",
                f"- Status: `{item['status']}`",
                f"- Output dir: `{item['output_dir']}`",
                f"- Command: `{item['command_shell']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "- This matrix only plans offline diagnostic simulation commands.",
            "- It does not execute experiments, prove robustness, calibrate contact geometry,",
            "  accept a gate, authorize hardware, or mark the goal complete.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "failed_diagnostic_robustness_experiment_matrix" / run_id
    )
    if out_dir.exists():
        raise FileExistsError(out_dir)
    out_dir.mkdir(parents=True)

    payload = build_matrix(run_id=run_id, out_dir=out_dir)
    payload["audit_root"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_commands(out_dir, payload["experiments"])
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
