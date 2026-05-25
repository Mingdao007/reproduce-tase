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

DEFAULT_FREEZE = "runs/read_only_phase1_approval_request_freeze/20260525T112000/metrics.yaml"
EXPECTED_STEP_ID = "phase1_mounted_stack_tcp_contact_measurement"
EXPECTED_WORKSHEET = "tcp_contact_measurements.csv"
APPROVAL_PHRASE = "I approve this read-only measurement step"

PHASE1_ROW = [
    "sample_001",
    "sensor_flange_face",
    "+z",
    "85.0",
    "dry_run_caliper",
    "0.01",
    "preapproval_guard",
    "synthetic row for rejection guard only",
]
KSM_ROW = [
    "sample_001",
    "ksm_ball",
    "synthetic disallowed row",
    "not measured",
    "dry_run_visual",
    "preapproval_guard",
    "synthetic row for rejection guard only",
]

REJECTION_CASES = [
    {
        "case_id": "wrong_confirmation_phrase",
        "tcp_rows": [PHASE1_ROW],
        "ksm_rows": [],
        "confirmation_phrase": "I approve a different read-only measurement step",
        "approved_step_id": EXPECTED_STEP_ID,
        "operator": "preapproval_guard",
        "expected_stderr": "approval phrase mismatch",
    },
    {
        "case_id": "unknown_step_id",
        "tcp_rows": [PHASE1_ROW],
        "ksm_rows": [],
        "confirmation_phrase": APPROVAL_PHRASE,
        "approved_step_id": "phase999_not_registered",
        "operator": "preapproval_guard",
        "expected_stderr": "is not in",
    },
    {
        "case_id": "operator_tbd",
        "tcp_rows": [PHASE1_ROW],
        "ksm_rows": [],
        "confirmation_phrase": APPROVAL_PHRASE,
        "approved_step_id": EXPECTED_STEP_ID,
        "operator": "TBD",
        "expected_stderr": "operator must be non-empty and not TBD",
    },
    {
        "case_id": "disallowed_worksheet_rows",
        "tcp_rows": [PHASE1_ROW],
        "ksm_rows": [KSM_ROW],
        "confirmation_phrase": APPROVAL_PHRASE,
        "approved_step_id": EXPECTED_STEP_ID,
        "operator": "preapproval_guard",
        "expected_stderr": "does not allow rows in",
    },
    {
        "case_id": "missing_required_rows",
        "tcp_rows": [],
        "ksm_rows": [],
        "confirmation_phrase": APPROVAL_PHRASE,
        "approved_step_id": EXPECTED_STEP_ID,
        "operator": "preapproval_guard",
        "expected_stderr": "at least one worksheet CSV row is required",
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


def append_rows(path: pathlib.Path, rows: list[list[str]]) -> None:
    if not rows:
        return
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


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
    append_rows(run_dir / EXPECTED_WORKSHEET, case["tcp_rows"])
    append_rows(run_dir / "ksm_contact_patch_convention.csv", case["ksm_rows"])
    command = [
        sys.executable,
        "scripts/finalize_read_only_calibration_measurement_evidence.py",
        str(run_dir),
        "--confirmation-phrase",
        case["confirmation_phrase"],
        "--approved-step-id",
        case["approved_step_id"],
        "--operator",
        case["operator"],
        "--live-hardware-accessed",
        "false",
        "--finalized-at-utc",
        "2026-05-25T11:30:00Z",
    ]
    completed = run_command(command)
    state = load_case_state(run_dir)
    expected_text = case["expected_stderr"]
    rejected_as_expected = completed.returncode != 0 and expected_text in completed.stderr
    scaffold_preserved = (
        state["status_after_attempt"] == "scaffold_created_not_executed"
        and state["user_confirmed_after_attempt"] is False
        and state["read_only_evidence_finalization_present"] is False
        and state["approved_read_only_evidence_created"] is False
        and all(value is False for value in state["hard_false_execution_fields"].values())
    )
    return {
        "case_id": case_id,
        "expected_rejection_substring": expected_text,
        "returncode": completed.returncode,
        "rejected_as_expected": rejected_as_expected,
        "scaffold_preserved": scaffold_preserved,
        "stderr_excerpt": completed.stderr.strip()[:240],
        "stdout_excerpt": completed.stdout.strip()[:120],
        "tcp_row_count": len(case["tcp_rows"]),
        "ksm_row_count": len(case["ksm_rows"]),
        **state,
    }


def validate_freeze(freeze: dict[str, Any], violations: list[str]) -> None:
    summary = freeze.get("summary", {})
    if summary.get("audit_passed") is not True:
        violations.append("v129 freeze source is not passed")
    if summary.get("approval_request_freeze_complete") is not True:
        violations.append("v129 freeze source is not complete")
    if summary.get("frozen_step_id") != EXPECTED_STEP_ID:
        violations.append("v129 frozen step ID drifted")
    if summary.get("frozen_worksheet") != EXPECTED_WORKSHEET:
        violations.append("v129 frozen worksheet drifted")
    if summary.get("approval_phrase_required") != APPROVAL_PHRASE:
        violations.append("v129 approval phrase drifted")
    if summary.get("packet_approval_status") != "not_approved":
        violations.append("v129 packet approval status is not not_approved")
    for key in [
        "approved_read_only_evidence_created",
        "freeze_authorizes_live_access",
        "freeze_authorizes_execution",
        "freeze_creates_approved_evidence",
        "overall_goal_complete",
        "completion_claim_allowed",
    ]:
        if summary.get(key) is not False:
            violations.append(f"v129 summary {key} is not false")
    if summary.get("do_not_mark_goal_complete") is not True:
        violations.append("v129 summary no longer blocks goal completion")


def build_payload(
    *,
    freeze_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    if not freeze_path.exists():
        violations.append(f"missing required source file: {rel(freeze_path)}")
    freeze = load_yaml(freeze_path) if freeze_path.exists() else {}
    validate_freeze(freeze, violations)

    case_rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="phase1_preapproval_finalizer_guard_") as tmp:
        temp_root = pathlib.Path(tmp)
        for case in REJECTION_CASES:
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
                        "tcp_row_count": len(case["tcp_rows"]),
                        "ksm_row_count": len(case["ksm_rows"]),
                        "status_after_attempt": None,
                        "approved_read_only_evidence_created": False,
                    }
                )

    for row in case_rows:
        if row.get("rejected_as_expected") is not True:
            violations.append(f"finalizer rejection case did not reject as expected: {row['case_id']}")
        if row.get("scaffold_preserved") is not True:
            violations.append(f"finalizer rejection case did not preserve scaffold: {row['case_id']}")
        if row.get("approved_read_only_evidence_created") is not False:
            violations.append(f"finalizer rejection case created evidence: {row['case_id']}")

    rejected_count = sum(1 for row in case_rows if row.get("rejected_as_expected") is True)
    scaffold_preserved_count = sum(1 for row in case_rows if row.get("scaffold_preserved") is True)
    evidence_created_count = sum(
        1 for row in case_rows if row.get("approved_read_only_evidence_created") is True
    )
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "preapproval_finalizer_guard_complete": not violations,
        "source_freeze_audit_passed": freeze.get("summary", {}).get("audit_passed"),
        "case_count": len(case_rows),
        "rejected_case_count": rejected_count,
        "scaffold_preserved_case_count": scaffold_preserved_count,
        "approved_read_only_evidence_created_count": evidence_created_count,
        "successful_finalization_count": 0,
        "repository_evidence_run_created": False,
        "temp_only_dry_run": True,
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
        "run_source": "read-only phase1 preapproval finalizer guard audit",
        "audit_run_id": run_id,
        "source_files": {
            "read_only_phase1_approval_request_freeze": rel(freeze_path),
        },
        "summary": summary,
        "rejection_case_rows": case_rows,
        "guarded_failure_modes": [
            "wrong confirmation phrase",
            "unknown approved step ID",
            "TBD operator",
            "worksheet rows outside the approved phase1 scope",
            "missing required phase1 worksheet rows",
        ],
        "claim_boundary": {
            "preapproval_finalizer_guard_only": True,
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
        "# Read-Only Phase1 Preapproval Finalizer Guard Audit",
        "",
        f"Run id: `{payload['audit_run_id']}`",
        "",
        f"Audit passed: `{summary['audit_passed']}`",
        f"Guard complete: `{summary['preapproval_finalizer_guard_complete']}`",
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
                "The frozen phase1 path rejects common pre-approval finalizer "
                "misuses in temporary dry-run scaffolds. No repository evidence "
                "run is created, and this audit authorizes no live access or "
                "execution."
            ),
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--freeze-path", default=DEFAULT_FREEZE)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "read_only_phase1_preapproval_finalizer_guard" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(freeze_path=resolve(args.freeze_path), run_id=run_id)
    payload["audit_root"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0 if payload["summary"]["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
