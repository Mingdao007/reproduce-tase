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


TEMPLATE_DIR = ROOT / "templates" / "contact_setup_target_acceptance_review"
DEFAULT_V116_METRICS = ROOT / "runs" / "strict_terminal_constrained_optimization" / "20260525T085000" / "metrics.yaml"


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)


def write_metrics(path: pathlib.Path, payload: dict[str, Any]) -> None:
    write_yaml(path / "metrics.yaml", payload)
    (path / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def instantiate_metrics(
    out_dir: pathlib.Path,
    *,
    review_id: str,
    v116_metrics_path: pathlib.Path,
) -> None:
    metrics = load_yaml(out_dir / "metrics.yaml")
    v116_metrics = load_yaml(v116_metrics_path)
    v116_summary = v116_metrics["summary"]
    metrics["review_id"] = review_id
    metrics["status"] = "review_scaffold_not_executed"
    metrics["template_source"] = str(TEMPLATE_DIR.relative_to(ROOT))
    metrics["review_root"] = str(out_dir)
    metrics["source_evidence"]["source_read_only_run"] = None
    metrics["source_evidence"]["source_run_audit"] = None
    metrics["source_evidence"]["approved_read_only_audit_passed"] = False
    metrics["source_evidence"]["evidence_reviewed"] = False
    metrics["source_evidence"]["latest_terminal_optimization"] = str(v116_metrics_path)
    metrics["source_evidence"]["terminal_optimization_reviewed"] = False
    metrics["source_evidence"]["contact_geometry_measurement_reviewed"] = False
    metrics["source_evidence"]["setup_target_definition_reviewed"] = False
    metrics["source_evidence"]["force_source_reconciliation_reviewed"] = False
    metrics["terminal_compatibility_context"]["source_metrics"] = str(v116_metrics_path)
    metrics["terminal_compatibility_context"]["strict_terminal_pass_count"] = v116_summary[
        "strict_terminal_pass_count"
    ]
    metrics["terminal_compatibility_context"]["best_max_gate_ratio"] = v116_summary[
        "best_max_gate_ratio"
    ]
    metrics["terminal_compatibility_context"]["v56_strict_best_max_gate_ratio"] = v116_summary[
        "v56_strict_best_max_gate_ratio"
    ]
    metrics["review_execution"]["user_approved_contact_setup_target_review"] = False
    metrics["review_execution"]["live_hardware_accessed"] = False
    metrics["review_execution"]["robot_motion_commanded"] = False
    metrics["review_execution"]["configuration_written"] = False
    metrics["review_execution"]["zeroing_or_biasing_performed"] = False
    metrics["review_execution"]["force_control_run"] = False
    metrics["contact_setup_target_acceptance"]["decision"] = "not_accepted"
    metrics["contact_setup_target_acceptance"]["review_only"] = True
    for field in [
        "accepted_contact_model",
        "accepted_setup_target_label",
        "accepted_tcp_contact_datum_source",
        "accepted_reference_xy_source",
        "accepted_surface_normal_source",
        "accepted_force_source",
        "accepted_uncertainty_budget",
        "accepted_gate_changes",
        "reviewer",
        "accepted_at_utc",
    ]:
        metrics["contact_setup_target_acceptance"][field] = None
    write_metrics(out_dir, metrics)


def instantiate_summary(out_dir: pathlib.Path, *, review_id: str) -> None:
    lines = [
        "# Contact Setup Target Acceptance Review Summary",
        "",
        f"Review id: `{review_id}`",
        f"Review root: `{out_dir}`",
        "",
        "Status: `review_scaffold_not_executed`",
        "",
        "No replacement contact model or setup target is accepted by this scaffold.",
        "",
        "This review scaffold is separate from read-only evidence finalization.",
        "",
        "No live hardware access, robot motion, configuration write, zeroing, or",
        "force-control action was performed by the scaffold command.",
        "",
        "All recovery, contact-calibration, setup-target, gate-relaxation,",
        "paper-equivalent, robustness, and hardware-readiness claims remain false.",
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
    parser.add_argument("--v116-metrics", default=str(DEFAULT_V116_METRICS))
    args = parser.parse_args()

    review_id = args.review_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "contact_setup_target_acceptance_review" / review_id
    )
    if out_dir.exists():
        raise FileExistsError(out_dir)
    v116_metrics_path = pathlib.Path(args.v116_metrics)
    if not v116_metrics_path.is_absolute():
        v116_metrics_path = (ROOT / v116_metrics_path).resolve()
    shutil.copytree(TEMPLATE_DIR, out_dir)
    instantiate_metrics(out_dir, review_id=review_id, v116_metrics_path=v116_metrics_path)
    instantiate_summary(out_dir, review_id=review_id)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
