#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from audit_post_v117_evidence_readiness import (  # noqa: E402
    DEFAULT_COMPLETION_BLOCKERS,
    DEFAULT_CONTACT_AUDIT_ROOT,
    DEFAULT_CONTACT_REVIEW_ROOT,
    DEFAULT_MATRIX_RESTATEMENT,
    DEFAULT_ORIENTATION_AUDIT_ROOT,
    DEFAULT_ORIENTATION_REVIEW_ROOT,
    DEFAULT_READ_ONLY_AUDIT_ROOT,
    DEFAULT_READ_ONLY_RUN_ROOT,
    DEFAULT_STRICT_TERMINAL,
    build_payload as build_evidence_payload,
    load_yaml,
    rel,
    resolve,
    write_git_state,
    write_yaml,
)
from audit_post_v122_completion_gate import (  # noqa: E402
    DEFAULT_EXECUTION_PREFLIGHT,
    DEFAULT_PACKET_COVERAGE,
    execution_preflight_row,
    load_required_yaml,
    packet_coverage_row,
    readiness_row,
    readiness_safety_violations,
)

DEFAULT_FINALIZATION_REHEARSAL = (
    "runs/read_only_finalization_rehearsal_boundary/20260525T122000/metrics.yaml"
)


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


def temporary_path_existing_count(metrics: dict[str, Any]) -> int:
    existing = 0
    for row in metrics.get("rehearsal_rows", []):
        for key in ["temporary_run_dir", "temporary_audit_dir"]:
            value = row.get(key)
            if value and pathlib.Path(value).exists():
                existing += 1
    return existing


def finalization_rehearsal_row(metrics: dict[str, Any]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    boundary = metrics.get("claim_boundary", {})
    existing_temp_paths = temporary_path_existing_count(metrics)
    completion_evidence = (
        summary.get("approved_read_only_evidence_created") is True
        or summary.get("repository_evidence_run_created_by_rehearsal") is True
        or summary.get("repository_evidence_audit_created_by_rehearsal") is True
        or int(summary.get("repository_approved_read_only_run_delta") or 0) > 0
        or int(summary.get("repository_finalization_record_delta") or 0) > 0
        or int(summary.get("repository_approved_read_only_audit_delta") or 0) > 0
        or summary.get("approval_record_created") is True
        or summary.get("rehearsal_authorizes_execution") is True
        or summary.get("rehearsal_authorizes_live_access") is True
        or summary.get("overall_goal_complete") is True
        or summary.get("completion_claim_allowed") is True
        or boundary.get("approved_read_only_evidence") is True
        or boundary.get("approved_read_only_evidence_created_in_repository") is True
        or boundary.get("execution_authorized") is True
        or boundary.get("live_hardware_access_authorized") is True
    )
    status = (
        "temporary_rehearsal_not_evidence"
        if summary.get("audit_passed") is True
        and summary.get("finalization_rehearsal_boundary_complete") is True
        else "audit_not_passed"
    )
    return readiness_row(
        readiness_id="finalization_rehearsal_boundary",
        purpose=(
            "Confirm the positive finalizer/verifier path was rehearsed only in "
            "temporary space and cannot count as repository evidence."
        ),
        status=status,
        completion_evidence=completion_evidence,
        evidence={
            "audit_run_id": metrics.get("audit_run_id"),
            "finalization_rehearsal_boundary_complete": summary.get(
                "finalization_rehearsal_boundary_complete"
            ),
            "registered_finalizer_step_count": summary.get("registered_finalizer_step_count"),
            "rehearsed_step_count": summary.get("rehearsed_step_count"),
            "rehearsal_passed_step_count": summary.get("rehearsal_passed_step_count"),
            "temporary_finalization_count": summary.get("temporary_finalization_count"),
            "approved_read_only_verifier_passed_count": summary.get(
                "approved_read_only_verifier_passed_count"
            ),
            "synthetic_row_only_count": summary.get("synthetic_row_only_count"),
            "live_hardware_accessed_count": summary.get("live_hardware_accessed_count"),
            "temporary_root_removed": summary.get("temporary_root_removed"),
            "temporary_path_existing_count": existing_temp_paths,
            "repository_approved_read_only_run_delta": summary.get(
                "repository_approved_read_only_run_delta"
            ),
            "repository_finalization_record_delta": summary.get(
                "repository_finalization_record_delta"
            ),
            "repository_approved_read_only_audit_delta": summary.get(
                "repository_approved_read_only_audit_delta"
            ),
            "approved_read_only_evidence_created": summary.get(
                "approved_read_only_evidence_created"
            ),
            "rehearsal_authorizes_execution": summary.get("rehearsal_authorizes_execution"),
            "rehearsal_authorizes_live_access": summary.get("rehearsal_authorizes_live_access"),
            "completion_claim_allowed": summary.get("completion_claim_allowed"),
            "do_not_mark_goal_complete": summary.get("do_not_mark_goal_complete"),
        },
        boundary={
            "approval_record_created": boundary.get("approval_record_created"),
            "approved_read_only_evidence": boundary.get("approved_read_only_evidence"),
            "approved_read_only_evidence_created_in_repository": boundary.get(
                "approved_read_only_evidence_created_in_repository"
            ),
            "live_hardware_access_authorized": boundary.get("live_hardware_access_authorized"),
            "execution_authorized": boundary.get("execution_authorized"),
            "hardware_readiness": boundary.get("hardware_readiness"),
            "do_not_mark_goal_complete": boundary.get("do_not_mark_goal_complete"),
        },
    )


def rehearsal_safety_violations(row: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    evidence = row["evidence"]
    expected = {
        "finalization_rehearsal_boundary_complete": True,
        "registered_finalizer_step_count": 5,
        "rehearsed_step_count": 5,
        "rehearsal_passed_step_count": 5,
        "temporary_finalization_count": 5,
        "approved_read_only_verifier_passed_count": 5,
        "synthetic_row_only_count": 5,
        "live_hardware_accessed_count": 0,
        "temporary_root_removed": True,
        "temporary_path_existing_count": 0,
        "repository_approved_read_only_run_delta": 0,
        "repository_finalization_record_delta": 0,
        "repository_approved_read_only_audit_delta": 0,
        "approved_read_only_evidence_created": False,
        "rehearsal_authorizes_execution": False,
        "rehearsal_authorizes_live_access": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    for key, expected_value in expected.items():
        if evidence.get(key) != expected_value:
            violations.append(
                f"finalization_rehearsal_boundary.evidence.{key} is "
                f"{evidence.get(key)!r}, expected {expected_value!r}"
            )
    if row["completion_evidence"]:
        violations.append("finalization_rehearsal_boundary drifted into completion evidence")
    return violations


def build_payload(
    *,
    completion_blockers_path: pathlib.Path,
    strict_terminal_path: pathlib.Path,
    matrix_restatement_path: pathlib.Path,
    read_only_run_root: pathlib.Path,
    read_only_audit_root: pathlib.Path,
    orientation_review_root: pathlib.Path,
    orientation_audit_root: pathlib.Path,
    contact_review_root: pathlib.Path,
    contact_audit_root: pathlib.Path,
    packet_coverage_path: pathlib.Path,
    execution_preflight_path: pathlib.Path,
    finalization_rehearsal_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    evidence_payload = build_evidence_payload(
        completion_blockers_path=completion_blockers_path,
        strict_terminal_path=strict_terminal_path,
        matrix_restatement_path=matrix_restatement_path,
        read_only_run_root=read_only_run_root,
        read_only_audit_root=read_only_audit_root,
        orientation_review_root=orientation_review_root,
        orientation_audit_root=orientation_audit_root,
        contact_review_root=contact_review_root,
        contact_audit_root=contact_audit_root,
        run_id=run_id,
    )
    packet_coverage = load_required_yaml(packet_coverage_path, violations)
    execution_preflight = load_required_yaml(execution_preflight_path, violations)
    finalization_rehearsal = load_required_yaml(finalization_rehearsal_path, violations)

    readiness_rows = []
    if packet_coverage:
        readiness_rows.append(packet_coverage_row(packet_coverage))
    if execution_preflight:
        readiness_rows.append(execution_preflight_row(execution_preflight))
    if finalization_rehearsal:
        readiness_rows.append(finalization_rehearsal_row(finalization_rehearsal))
    violations.extend(readiness_safety_violations(readiness_rows))
    for row in readiness_rows:
        if row["readiness_id"] == "finalization_rehearsal_boundary":
            violations.extend(rehearsal_safety_violations(row))

    evidence_summary = evidence_payload["summary"]
    readiness_completion_evidence_ids = [
        row["readiness_id"] for row in readiness_rows if row["completion_evidence"]
    ]
    completion_claim_allowed = (
        evidence_summary["completion_claim_allowed"]
        and not readiness_completion_evidence_ids
        and not violations
    )
    rehearsal_row = next(
        (row for row in readiness_rows if row["readiness_id"] == "finalization_rehearsal_boundary"),
        {},
    )
    rehearsal_evidence = rehearsal_row.get("evidence", {})
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "overall_goal_complete": completion_claim_allowed,
        "completion_claim_allowed": completion_claim_allowed,
        "do_not_mark_goal_complete": not completion_claim_allowed,
        "top_blocker": evidence_summary["top_blocker"],
        "incomplete_requirement_count": evidence_summary["incomplete_requirement_count"],
        "incomplete_requirement_ids": evidence_summary["incomplete_requirement_ids"],
        "approved_read_only_run_count": evidence_summary["approved_read_only_run_count"],
        "approved_read_only_audit_passed_count": evidence_summary[
            "approved_read_only_audit_passed_count"
        ],
        "accepted_orientation_review_count": evidence_summary["accepted_orientation_review_count"],
        "accepted_contact_setup_target_review_count": evidence_summary[
            "accepted_contact_setup_target_review_count"
        ],
        "strict_terminal_pass_count": evidence_summary["strict_terminal_pass_count"],
        "closed_robustness_cell_count": evidence_summary["closed_robustness_cell_count"],
        "hardware_gate_report_exists": evidence_summary["hardware_gate_report_exists"],
        "readiness_artifact_count": len(readiness_rows),
        "readiness_completion_evidence_ids": readiness_completion_evidence_ids,
        "readiness_artifacts_are_non_evidence": not readiness_completion_evidence_ids,
        "finalization_rehearsal_is_non_evidence": not rehearsal_row.get("completion_evidence", True),
        "rehearsal_temporary_finalization_count": rehearsal_evidence.get(
            "temporary_finalization_count"
        ),
        "rehearsal_approved_read_only_verifier_passed_count": rehearsal_evidence.get(
            "approved_read_only_verifier_passed_count"
        ),
        "rehearsal_temporary_path_existing_count": rehearsal_evidence.get(
            "temporary_path_existing_count"
        ),
        "rehearsal_repository_approved_read_only_run_delta": rehearsal_evidence.get(
            "repository_approved_read_only_run_delta"
        ),
        "rehearsal_repository_finalization_record_delta": rehearsal_evidence.get(
            "repository_finalization_record_delta"
        ),
        "rehearsal_repository_approved_read_only_audit_delta": rehearsal_evidence.get(
            "repository_approved_read_only_audit_delta"
        ),
    }
    return {
        "run_source": "post-v135 completion gate audit",
        "audit_run_id": run_id,
        "source_files": {
            **evidence_payload["source_files"],
            "packet_coverage": rel(packet_coverage_path),
            "execution_preflight": rel(execution_preflight_path),
            "finalization_rehearsal": rel(finalization_rehearsal_path),
        },
        "actual_scan_roots": evidence_payload["actual_scan_roots"],
        "summary": summary,
        "completion_checklist": evidence_payload["completion_checklist"],
        "readiness_artifacts": readiness_rows,
        "claim_boundary": {
            "post_hoc_offline_audit_only": True,
            "readiness_artifacts_do_not_complete_goal": not readiness_completion_evidence_ids,
            "finalization_rehearsal_is_not_evidence": not rehearsal_row.get(
                "completion_evidence", True
            ),
            "approval_record_created": False,
            "approved_read_only_evidence": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "contact_calibration_claim": False,
            "setup_target_acceptance_claim": False,
            "gate_relaxation_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "robustness_claim": False,
            "hardware_readiness": False,
            "do_not_mark_goal_complete": not completion_claim_allowed,
        },
        "next_actions": [
            "Request explicit user approval before any live read-only SOP step.",
            "If approval is absent, continue only offline non-final research.",
            "Treat packet coverage, execution preflight, and finalization rehearsal as readiness artifacts, not evidence.",
            "Do not accept contact/setup-target or orientation-gate changes from simulation recovery alone.",
            "Avoid repeating v113-v116 policy, timing, seed, and terminal-objective families.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Post-V135 Completion Gate Audit",
        "",
        f"Run root: `{out_dir}`",
        "",
        "## Summary",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Overall goal complete: `{summary['overall_goal_complete']}`",
        f"- Completion claim allowed: `{summary['completion_claim_allowed']}`",
        f"- Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        f"- Top blocker: `{summary['top_blocker']}`",
        f"- Approved read-only evidence runs: `{summary['approved_read_only_run_count']}`",
        f"- Passed approved-read-only audits: `{summary['approved_read_only_audit_passed_count']}`",
        f"- Accepted orientation reviews: `{summary['accepted_orientation_review_count']}`",
        f"- Accepted contact/setup-target reviews: `{summary['accepted_contact_setup_target_review_count']}`",
        f"- Strict terminal pass count: `{summary['strict_terminal_pass_count']}`",
        f"- Closed robustness cells: `{summary['closed_robustness_cell_count']}`",
        f"- Hardware gate report exists: `{summary['hardware_gate_report_exists']}`",
        f"- Readiness artifacts are non-evidence: `{summary['readiness_artifacts_are_non_evidence']}`",
        f"- Finalization rehearsal is non-evidence: `{summary['finalization_rehearsal_is_non_evidence']}`",
        "",
        "## Readiness Artifacts",
        "",
    ]
    for row in payload["readiness_artifacts"]:
        lines.extend(
            [
                f"- `{row['readiness_id']}`: status `{row['status']}`",
                f"  - completion evidence: `{row['completion_evidence']}`",
            ]
        )
    lines.extend(["", "## Completion Checklist", ""])
    for row in payload["completion_checklist"]:
        lines.extend(
            [
                f"- `{row['requirement_id']}`: achieved `{row['achieved']}`",
                f"  - missing: `{', '.join(row['missing']) if row['missing'] else 'none'}`",
                f"  - next action: {row['next_action']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This audit is offline bookkeeping only. It does not approve a packet,",
            "collect live evidence, move or configure the robot, accept a contact/",
            "setup target, accept an orientation gate, prove robustness, or",
            "establish hardware readiness.",
            "",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--completion-blockers-path", default=DEFAULT_COMPLETION_BLOCKERS)
    parser.add_argument("--strict-terminal-path", default=DEFAULT_STRICT_TERMINAL)
    parser.add_argument("--matrix-restatement-path", default=DEFAULT_MATRIX_RESTATEMENT)
    parser.add_argument("--read-only-run-root", default=DEFAULT_READ_ONLY_RUN_ROOT)
    parser.add_argument("--read-only-audit-root", default=DEFAULT_READ_ONLY_AUDIT_ROOT)
    parser.add_argument("--orientation-review-root", default=DEFAULT_ORIENTATION_REVIEW_ROOT)
    parser.add_argument("--orientation-audit-root", default=DEFAULT_ORIENTATION_AUDIT_ROOT)
    parser.add_argument("--contact-review-root", default=DEFAULT_CONTACT_REVIEW_ROOT)
    parser.add_argument("--contact-audit-root", default=DEFAULT_CONTACT_AUDIT_ROOT)
    parser.add_argument("--packet-coverage-path", default=DEFAULT_PACKET_COVERAGE)
    parser.add_argument("--execution-preflight-path", default=DEFAULT_EXECUTION_PREFLIGHT)
    parser.add_argument("--finalization-rehearsal-path", default=DEFAULT_FINALIZATION_REHEARSAL)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "post_v135_completion_gate" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(
        completion_blockers_path=resolve(args.completion_blockers_path),
        strict_terminal_path=resolve(args.strict_terminal_path),
        matrix_restatement_path=resolve(args.matrix_restatement_path),
        read_only_run_root=resolve(args.read_only_run_root),
        read_only_audit_root=resolve(args.read_only_audit_root),
        orientation_review_root=resolve(args.orientation_review_root),
        orientation_audit_root=resolve(args.orientation_audit_root),
        contact_review_root=resolve(args.contact_review_root),
        contact_audit_root=resolve(args.contact_audit_root),
        packet_coverage_path=resolve(args.packet_coverage_path),
        execution_preflight_path=resolve(args.execution_preflight_path),
        finalization_rehearsal_path=resolve(args.finalization_rehearsal_path),
        run_id=run_id,
    )
    payload["audit_root"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0 if payload["summary"]["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
