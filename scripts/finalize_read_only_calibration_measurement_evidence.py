#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import csv
import datetime as dt
import json
import pathlib
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from audit_read_only_calibration_measurement_run import (
    EXPECTED_CSV_HEADERS,
    EXPECTED_EVIDENCE_STATUS,
    HARD_FALSE_FIELDS,
    REQUIRED_FILES,
    audit_run,
    nested_get,
    write_git_state,
    write_yaml,
)

APPROVAL_PHRASE = "I approve this read-only measurement step"

CSV_EVIDENCE_MAP = {
    "tcp_contact_measurements.csv": "mounted_stack_tcp_contact_point",
    "plane_normal_measurements.csv": "plane_normal_robot_base_frame",
    "force_source_comparison.csv": "force_source_frame_reconciliation",
}


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_metrics(run_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    write_yaml(run_dir / "metrics.yaml", payload)
    (run_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_bool(value: str) -> bool:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def non_tbd(value: str, *, field: str) -> str:
    stripped = value.strip()
    if not stripped or stripped.upper() == "TBD":
        raise ValueError(f"{field} must be non-empty and not TBD")
    return stripped


def validate_confirmation(confirmation_phrase: str, approved_step_id: str, operator: str) -> None:
    if confirmation_phrase != APPROVAL_PHRASE:
        raise ValueError(
            "approval phrase mismatch; expected exact phrase "
            f"{APPROVAL_PHRASE!r}"
        )
    non_tbd(approved_step_id, field="approved_step_id")
    non_tbd(operator, field="operator")


def read_worksheet_row_counts(run_dir: pathlib.Path) -> dict[str, int]:
    row_counts: dict[str, int] = {}
    for csv_name, expected_header in EXPECTED_CSV_HEADERS.items():
        path = run_dir / csv_name
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, [])
            if ",".join(header) != expected_header:
                raise ValueError(f"{csv_name} header changed")
            row_counts[csv_name] = sum(1 for row in reader if any(cell.strip() for cell in row))
    return row_counts


def validate_scaffold_run(run_dir: pathlib.Path) -> tuple[dict[str, Any], dict[str, int]]:
    if not run_dir.exists() or not run_dir.is_dir():
        raise FileNotFoundError(run_dir)

    present_files = {path.name for path in run_dir.iterdir() if path.is_file()}
    missing_files = sorted(REQUIRED_FILES - present_files)
    if missing_files:
        raise ValueError("missing required files: " + ", ".join(missing_files))

    metrics = load_yaml(run_dir / "metrics.yaml")
    metrics_json = load_json(run_dir / "metrics.json")
    if metrics != metrics_json:
        raise ValueError("metrics.yaml and metrics.json differ before finalization")

    if metrics.get("status") != "scaffold_created_not_executed":
        raise ValueError("run status must be scaffold_created_not_executed before finalization")
    if metrics.get("source_sop") != "reports/read_only_calibration_measurement_sop.md":
        raise ValueError("source_sop does not point to the v87 SOP")
    if metrics.get("template_source") != "templates/read_only_calibration_measurement":
        raise ValueError("template_source does not point to the v88 template")

    pre_finalization_false_fields = [
        ("execution", "user_confirmed_read_only_step"),
        ("execution", "live_hardware_accessed"),
        *HARD_FALSE_FIELDS,
    ]
    for field_path in pre_finalization_false_fields:
        if nested_get(metrics, field_path) is not False:
            raise ValueError("expected false field is not false: " + ".".join(field_path))

    evidence_status = metrics.get("evidence_status", {})
    for key, expected in EXPECTED_EVIDENCE_STATUS.items():
        if evidence_status.get(key) != expected:
            raise ValueError(f"evidence_status.{key} is not {expected}")

    row_counts = read_worksheet_row_counts(run_dir)
    if not any(row_counts.values()):
        raise ValueError("at least one worksheet CSV row is required before finalization")

    return metrics, row_counts


def derive_evidence_status(row_counts: dict[str, int]) -> dict[str, str]:
    evidence_status = dict(EXPECTED_EVIDENCE_STATUS)
    for csv_name, evidence_key in CSV_EVIDENCE_MAP.items():
        if row_counts.get(csv_name, 0) > 0:
            evidence_status[evidence_key] = "collected_read_only"
    return evidence_status


def finalize_metrics(
    metrics: dict[str, Any],
    *,
    approved_step_id: str,
    operator: str,
    live_hardware_accessed: bool,
    finalized_at_utc: str,
    row_counts: dict[str, int],
) -> dict[str, Any]:
    finalized = copy.deepcopy(metrics)
    finalized["status"] = "approved_read_only_evidence"
    finalized.setdefault("execution", {})
    finalized["execution"]["user_confirmed_read_only_step"] = True
    finalized["execution"]["live_hardware_accessed"] = live_hardware_accessed
    for group, key in HARD_FALSE_FIELDS:
        finalized.setdefault(group, {})
        finalized[group][key] = False
    finalized["evidence_status"] = derive_evidence_status(row_counts)
    finalized["read_only_evidence_finalization"] = {
        "confirmation_phrase_matched": True,
        "approved_step_id": approved_step_id,
        "operator": operator,
        "finalized_at_utc": finalized_at_utc,
        "finalizer": "scripts/finalize_read_only_calibration_measurement_evidence.py",
        "live_hardware_accessed_declared": live_hardware_accessed,
        "worksheet_row_counts": row_counts,
    }
    return finalized


def write_summary(
    run_dir: pathlib.Path,
    *,
    run_id: str,
    approved_step_id: str,
    operator: str,
    live_hardware_accessed: bool,
    finalized_at_utc: str,
    row_counts: dict[str, int],
) -> None:
    lines = [
        "# Read-Only Calibration Measurement Summary",
        "",
        f"Run id: `{run_id}`",
        f"Run root: `{run_dir}`",
        "",
        "Status: `approved_read_only_evidence`",
        "",
        f"Approved step ID: `{approved_step_id}`",
        f"Operator: `{operator}`",
        f"Finalized at UTC: `{finalized_at_utc}`",
        f"Live hardware accessed: `{live_hardware_accessed}`",
        "",
        "Worksheet row counts:",
        "",
    ]
    lines.extend(f"- `{csv_name}`: `{count}`" for csv_name, count in row_counts.items())
    lines.extend(
        [
            "",
            "No robot motion, configuration write, zeroing, biasing, or",
            "force-control action is authorized by this finalization.",
            "",
            "All recovery, calibration, gate-relaxation, paper-equivalent, robustness,",
            "and hardware-readiness claims remain false until separately audited.",
        ]
    )
    (run_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    parser.add_argument(
        "--confirmation-phrase",
        required=True,
        help=f"Must exactly match: {APPROVAL_PHRASE}",
    )
    parser.add_argument("--approved-step-id", required=True)
    parser.add_argument("--operator", required=True)
    parser.add_argument(
        "--live-hardware-accessed",
        required=True,
        type=parse_bool,
        help="Explicit metadata declaration only; expected true or false.",
    )
    parser.add_argument("--finalized-at-utc", default=None)
    args = parser.parse_args()

    run_dir = pathlib.Path(args.run_dir).resolve()
    try:
        validate_confirmation(args.confirmation_phrase, args.approved_step_id, args.operator)
        metrics, row_counts = validate_scaffold_run(run_dir)
        finalized_at_utc = args.finalized_at_utc or dt.datetime.now(dt.UTC).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        approved_step_id = non_tbd(args.approved_step_id, field="approved_step_id")
        operator = non_tbd(args.operator, field="operator")
        finalized = finalize_metrics(
            metrics,
            approved_step_id=approved_step_id,
            operator=operator,
            live_hardware_accessed=args.live_hardware_accessed,
            finalized_at_utc=finalized_at_utc,
            row_counts=row_counts,
        )
        write_metrics(run_dir, finalized)
        write_summary(
            run_dir,
            run_id=finalized.get("run_id", "UNKNOWN"),
            approved_step_id=approved_step_id,
            operator=operator,
            live_hardware_accessed=args.live_hardware_accessed,
            finalized_at_utc=finalized_at_utc,
            row_counts=row_counts,
        )
        write_git_state(run_dir, command=[sys.executable, *sys.argv])
        audit = audit_run(run_dir, audit_mode="approved-read-only")
        if not audit["audit_passed"]:
            raise ValueError("finalized run failed approved-read-only audit: " + "; ".join(audit["violations"]))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
