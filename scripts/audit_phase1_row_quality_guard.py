#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import pathlib
import subprocess
import sys
import tempfile
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

DEFAULT_SEQUENCE_BOUNDARY = "runs/read_only_evidence_sequence_boundary/20260525T115000/metrics.yaml"
EXPECTED_STEP_ID = "phase1_mounted_stack_tcp_contact_measurement"
EXPECTED_WORKSHEET = "tcp_contact_measurements.csv"
APPROVAL_PHRASE = "I approve this read-only measurement step"

VALID_ROW = [
    "sample_001",
    "sensor_flange_face",
    "+z",
    "85.0",
    "dry_run_caliper",
    "0.01",
    "phase1_row_quality_guard",
    "synthetic invalid-row rejection guard only",
]

ROW_QUALITY_CASES = [
    {
        "case_id": "placeholder_datum",
        "row": [*VALID_ROW[:1], "TBD", *VALID_ROW[2:]],
        "expected_stderr": "datum must be non-empty and not a placeholder",
    },
    {
        "case_id": "invalid_tool_axis_sign",
        "row": [*VALID_ROW[:2], "sideways", *VALID_ROW[3:]],
        "expected_stderr": "tool_axis_sign must be one of",
    },
    {
        "case_id": "nonnumeric_distance",
        "row": [*VALID_ROW[:3], "not_numeric", *VALID_ROW[4:]],
        "expected_stderr": "distance_mm is not numeric",
    },
    {
        "case_id": "nonpositive_resolution",
        "row": [*VALID_ROW[:5], "0", *VALID_ROW[6:]],
        "expected_stderr": "resolution_mm must be finite and positive",
    },
    {
        "case_id": "placeholder_row_operator",
        "row": [*VALID_ROW[:6], "TBD", *VALID_ROW[7:]],
        "expected_stderr": "operator must be non-empty and not a placeholder",
    },
]


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


def resolve(path: str | pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(path)
    if path.is_absolute():
        return path
    return ROOT / path


def rel(path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(payload, f, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True)


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


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def create_temp_scaffold(temp_root: pathlib.Path, case_id: str) -> pathlib.Path:
    run_dir = temp_root / case_id
    completed = run_command(
        [
            sys.executable,
            "scripts/create_read_only_calibration_measurement_run.py",
            "--output-dir",
            str(run_dir),
            "--run-id",
            case_id,
        ]
    )
    if completed.returncode != 0:
        raise RuntimeError(f"failed to create scaffold for {case_id}: {completed.stderr}")
    return run_dir


def append_tcp_row(run_dir: pathlib.Path, row: list[str]) -> None:
    with (run_dir / EXPECTED_WORKSHEET).open("a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(row)


def load_case_state(run_dir: pathlib.Path) -> dict[str, Any]:
    metrics = load_yaml(run_dir / "metrics.yaml")
    return {
        "status_after_attempt": metrics.get("status"),
        "user_confirmed_after_attempt": metrics.get("execution", {}).get(
            "user_confirmed_read_only_step"
        ),
        "live_hardware_accessed_after_attempt": metrics.get("execution", {}).get(
            "live_hardware_accessed"
        ),
        "read_only_evidence_finalization_present": "read_only_evidence_finalization" in metrics,
        "approved_read_only_evidence_created": metrics.get("status") == "approved_read_only_evidence",
        "hard_false_execution_fields": {
            key: metrics.get("execution", {}).get(key)
            for key in [
                "robot_motion_commanded",
                "configuration_written",
                "zeroing_or_biasing_performed",
                "force_control_run",
            ]
        },
    }


def run_rejection_case(temp_root: pathlib.Path, case: dict[str, Any]) -> dict[str, Any]:
    case_id = case["case_id"]
    run_dir = create_temp_scaffold(temp_root, case_id)
    append_tcp_row(run_dir, case["row"])
    command = [
        sys.executable,
        "scripts/finalize_read_only_calibration_measurement_evidence.py",
        str(run_dir),
        "--confirmation-phrase",
        APPROVAL_PHRASE,
        "--approved-step-id",
        EXPECTED_STEP_ID,
        "--operator",
        "phase1_row_quality_guard",
        "--live-hardware-accessed",
        "false",
        "--finalized-at-utc",
        "2026-05-25T12:00:00Z",
    ]
    completed = run_command(command)
    state = load_case_state(run_dir)
    rejected_as_expected = completed.returncode != 0 and case["expected_stderr"] in completed.stderr
    scaffold_preserved = (
        state["status_after_attempt"] == "scaffold_created_not_executed"
        and state["user_confirmed_after_attempt"] is False
        and state["read_only_evidence_finalization_present"] is False
        and state["approved_read_only_evidence_created"] is False
        and all(value is False for value in state["hard_false_execution_fields"].values())
    )
    return {
        "case_id": case_id,
        "expected_rejection_substring": case["expected_stderr"],
        "returncode": completed.returncode,
        "rejected_as_expected": rejected_as_expected,
        "scaffold_preserved": scaffold_preserved,
        "stderr_excerpt": completed.stderr.strip()[:240],
        "stdout_excerpt": completed.stdout.strip()[:120],
        **state,
    }


def validate_sequence_boundary(metrics: dict[str, Any], violations: list[str]) -> None:
    summary = metrics.get("summary", {})
    expected = {
        "audit_passed": True,
        "sequence_boundary_complete": True,
        "ordered_step_count": 5,
        "first_step_id": EXPECTED_STEP_ID,
        "first_worksheet": EXPECTED_WORKSHEET,
        "all_steps_separate_approval_required": True,
        "phase1_alone_completes_overall_goal": False,
        "current_approved_read_only_run_count": 0,
        "current_phase1_approved_read_only_run_count": 0,
        "current_finalization_record_count": 0,
        "current_approved_read_only_audit_passed_count": 0,
        "approved_packet_count": 0,
        "execution_authorizing_packet_count": 0,
        "live_access_authorizing_packet_count": 0,
        "bundle_approval_authorized": False,
        "approved_read_only_evidence_created": False,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            violations.append(f"v132 source summary {key} is {summary.get(key)!r}, expected {value!r}")


def build_payload(*, sequence_boundary_path: pathlib.Path, run_id: str) -> dict[str, Any]:
    violations: list[str] = []
    if not sequence_boundary_path.exists():
        violations.append(f"missing required source file: {rel(sequence_boundary_path)}")
    sequence_boundary = load_yaml(sequence_boundary_path) if sequence_boundary_path.exists() else {}
    validate_sequence_boundary(sequence_boundary, violations)

    case_rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="phase1_row_quality_guard_") as tmp:
        temp_root = pathlib.Path(tmp)
        for case in ROW_QUALITY_CASES:
            try:
                case_rows.append(run_rejection_case(temp_root, case))
            except Exception as exc:
                case_rows.append(
                    {
                        "case_id": case["case_id"],
                        "expected_rejection_substring": case["expected_stderr"],
                        "returncode": None,
                        "rejected_as_expected": False,
                        "scaffold_preserved": False,
                        "stderr_excerpt": str(exc)[:240],
                        "stdout_excerpt": "",
                        "approved_read_only_evidence_created": False,
                    }
                )

    for row in case_rows:
        if row.get("rejected_as_expected") is not True:
            violations.append(f"row-quality case did not reject as expected: {row['case_id']}")
        if row.get("scaffold_preserved") is not True:
            violations.append(f"row-quality case did not preserve scaffold: {row['case_id']}")
        if row.get("approved_read_only_evidence_created") is not False:
            violations.append(f"row-quality case created evidence: {row['case_id']}")

    rejected_count = sum(1 for row in case_rows if row.get("rejected_as_expected") is True)
    preserved_count = sum(1 for row in case_rows if row.get("scaffold_preserved") is True)
    evidence_created_count = sum(
        1 for row in case_rows if row.get("approved_read_only_evidence_created") is True
    )
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "phase1_row_quality_guard_complete": not violations,
        "source_sequence_boundary_audit_passed": sequence_boundary.get("summary", {}).get("audit_passed"),
        "case_count": len(case_rows),
        "rejected_case_count": rejected_count,
        "scaffold_preserved_case_count": preserved_count,
        "approved_read_only_evidence_created_count": evidence_created_count,
        "repository_evidence_run_created": False,
        "temp_only_dry_run": True,
        "guarded_step_id": EXPECTED_STEP_ID,
        "guarded_worksheet": EXPECTED_WORKSHEET,
        "approved_packet_count": 0,
        "execution_authorizing_packet_count": 0,
        "live_access_authorizing_packet_count": 0,
        "approved_read_only_evidence_created": False,
        "guard_authorizes_live_access": False,
        "guard_authorizes_execution": False,
        "guard_creates_approved_evidence": False,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    return {
        "run_source": "phase1 row-quality guard audit",
        "audit_run_id": run_id,
        "source_files": {
            "read_only_evidence_sequence_boundary": rel(sequence_boundary_path),
        },
        "summary": summary,
        "rejection_case_rows": case_rows,
        "guarded_failure_modes": [
            "placeholder datum",
            "invalid tool axis sign",
            "nonnumeric distance_mm",
            "nonpositive resolution_mm",
            "placeholder row operator",
        ],
        "claim_boundary": {
            "post_hoc_offline_audit_only": True,
            "phase1_row_quality_guard_only": True,
            "temp_only_dry_run": True,
            "approval_record_created": False,
            "approved_read_only_evidence": False,
            "contact_calibration_claim": False,
            "setup_target_acceptance_claim": False,
            "gate_relaxation_claim": False,
            "strict_terminal_relaxation_accepted": False,
            "strict_paper_equivalent_feasibility": False,
            "robustness_claim": False,
            "hardware_readiness": False,
            "live_hardware_access_authorized": False,
            "execution_authorized": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "do_not_mark_goal_complete": True,
        },
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Phase1 Row-Quality Guard Audit",
        "",
        f"Run id: `{payload['audit_run_id']}`",
        "",
        f"Audit passed: `{summary['audit_passed']}`",
        f"Guard complete: `{summary['phase1_row_quality_guard_complete']}`",
        f"Case count: `{summary['case_count']}`",
        f"Rejected cases: `{summary['rejected_case_count']}`",
        f"Scaffold-preserved cases: `{summary['scaffold_preserved_case_count']}`",
        f"Approved evidence created in dry runs: `{summary['approved_read_only_evidence_created_count']}`",
        f"Repository evidence run created: `{summary['repository_evidence_run_created']}`",
        f"Guard authorizes execution: `{summary['guard_authorizes_execution']}`",
        f"Completion claim allowed: `{summary['completion_claim_allowed']}`",
        f"Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "Rejection cases:",
        "",
        "| Case | Rejected | Scaffold preserved | Expected stderr |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in payload["rejection_case_rows"]:
        lines.append(
            f"| `{row['case_id']}` | `{row['rejected_as_expected']}` | "
            f"`{row['scaffold_preserved']}` | `{row['expected_rejection_substring']}` |"
        )
    lines.extend(["", "Violations:", ""])
    if summary["violations"]:
        lines.extend(f"- {violation}" for violation in summary["violations"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            (
                "The phase1 finalizer rejects malformed TCP/contact measurement "
                "rows before approved evidence can be written. No repository "
                "evidence run is created, and this audit authorizes no live "
                "access or execution."
            ),
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--sequence-boundary-path", default=DEFAULT_SEQUENCE_BOUNDARY)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "phase1_row_quality_guard" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(sequence_boundary_path=resolve(args.sequence_boundary_path), run_id=run_id)
    payload["audit_root"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0 if payload["summary"]["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
