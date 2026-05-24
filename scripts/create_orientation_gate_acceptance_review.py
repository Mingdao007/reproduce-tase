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

from audit_read_only_calibration_measurement_run import write_git_state


TEMPLATE_DIR = ROOT / "templates" / "orientation_gate_acceptance_review"


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)


def write_metrics(path: pathlib.Path, payload: dict[str, Any]) -> None:
    write_yaml(path / "metrics.yaml", payload)
    (path / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def instantiate_metrics(out_dir: pathlib.Path, *, review_id: str) -> None:
    metrics = load_yaml(out_dir / "metrics.yaml")
    metrics["review_id"] = review_id
    metrics["status"] = "review_scaffold_not_executed"
    metrics["template_source"] = str(TEMPLATE_DIR.relative_to(ROOT))
    metrics["review_root"] = str(out_dir)
    metrics["source_evidence"]["source_read_only_run"] = None
    metrics["source_evidence"]["source_run_audit"] = None
    metrics["source_evidence"]["approved_read_only_audit_passed"] = False
    metrics["source_evidence"]["evidence_reviewed"] = False
    metrics["review_execution"]["user_approved_gate_acceptance_review"] = False
    metrics["review_execution"]["live_hardware_accessed"] = False
    metrics["review_execution"]["robot_motion_commanded"] = False
    metrics["review_execution"]["configuration_written"] = False
    metrics["review_execution"]["zeroing_or_biasing_performed"] = False
    metrics["review_execution"]["force_control_run"] = False
    metrics["orientation_gate_acceptance"]["decision"] = "not_accepted"
    metrics["orientation_gate_acceptance"]["review_only"] = True
    for field in [
        "accepted_gate_type",
        "accepted_gate_value_rad",
        "accepted_normal_source",
        "accepted_contact_datum_source",
        "accepted_uncertainty_budget",
        "reviewer",
        "accepted_at_utc",
    ]:
        metrics["orientation_gate_acceptance"][field] = None
    write_metrics(out_dir, metrics)


def instantiate_summary(out_dir: pathlib.Path, *, review_id: str) -> None:
    lines = [
        "# Orientation Gate Acceptance Review Summary",
        "",
        f"Review id: `{review_id}`",
        f"Review root: `{out_dir}`",
        "",
        "Status: `review_scaffold_not_executed`",
        "",
        "No replacement diagnostic orientation gate is accepted by this scaffold.",
        "",
        "This review scaffold is separate from read-only evidence finalization.",
        "",
        "No live hardware access, robot motion, configuration write, zeroing, or",
        "force-control action was performed by the scaffold command.",
        "",
        "All recovery, calibration, gate-relaxation, paper-equivalent, robustness,",
        "and hardware-readiness claims remain false.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument(
        "--review-id",
        default=None,
        help="Review id to stamp into metrics and summary; defaults to local timestamp.",
    )
    args = parser.parse_args()

    review_id = args.review_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "orientation_gate_acceptance_review" / review_id
    )
    if out_dir.exists():
        raise FileExistsError(out_dir)
    shutil.copytree(TEMPLATE_DIR, out_dir)
    instantiate_metrics(out_dir, review_id=review_id)
    instantiate_summary(out_dir, review_id=review_id)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
