#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import shutil
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from audit_stage_a_base_z_recovery import write_git_state


TEMPLATE_DIR = ROOT / "templates" / "read_only_calibration_measurement"


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)


def write_metrics(path: pathlib.Path, payload: dict[str, Any]) -> None:
    write_yaml(path / "metrics.yaml", payload)
    (path / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def instantiate_metrics(out_dir: pathlib.Path, *, run_id: str) -> None:
    metrics_path = out_dir / "metrics.yaml"
    metrics = load_yaml(metrics_path)
    metrics["run_id"] = run_id
    metrics["status"] = "scaffold_created_not_executed"
    metrics["template_source"] = str(TEMPLATE_DIR.relative_to(ROOT))
    metrics["run_root"] = str(out_dir)
    metrics["execution"]["live_hardware_accessed"] = False
    metrics["execution"]["robot_motion_commanded"] = False
    metrics["execution"]["configuration_written"] = False
    metrics["execution"]["zeroing_or_biasing_performed"] = False
    metrics["execution"]["force_control_run"] = False
    write_metrics(out_dir, metrics)


def instantiate_summary(out_dir: pathlib.Path, *, run_id: str) -> None:
    lines = [
        "# Read-Only Calibration Measurement Summary",
        "",
        f"Run id: `{run_id}`",
        f"Run root: `{out_dir}`",
        "",
        "Status: `scaffold_created_not_executed`",
        "",
        "This run folder was scaffolded from",
        "`templates/read_only_calibration_measurement`.",
        "",
        "No live hardware access, robot motion, configuration write, zeroing, or",
        "force-control action was performed by the scaffold command.",
        "",
        "All recovery, calibration, gate-relaxation, paper-equivalent, robustness,",
        "and hardware-readiness claims remain false until concrete measurements",
        "are collected and audited.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument(
        "--run-id",
        default=None,
        help="Run id to stamp into metrics and summary; defaults to local timestamp.",
    )
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "read_only_calibration_measurement" / run_id
    )
    if out_dir.exists():
        raise FileExistsError(out_dir)
    shutil.copytree(TEMPLATE_DIR, out_dir)
    instantiate_metrics(out_dir, run_id=run_id)
    instantiate_summary(out_dir, run_id=run_id)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
