#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from audit_post_v137_completion_gate import (  # noqa: E402
    DEFAULT_COMPLETION_BLOCKERS,
    DEFAULT_CONTACT_AUDIT_ROOT,
    DEFAULT_CONTACT_REVIEW_ROOT,
    DEFAULT_EXECUTION_PREFLIGHT,
    DEFAULT_FINALIZATION_REHEARSAL,
    DEFAULT_MARGIN_SEPARATION,
    DEFAULT_MATRIX_RESTATEMENT,
    DEFAULT_ORIENTATION_AUDIT_ROOT,
    DEFAULT_ORIENTATION_REVIEW_ROOT,
    DEFAULT_PACKET_COVERAGE,
    DEFAULT_READ_ONLY_AUDIT_ROOT,
    DEFAULT_READ_ONLY_RUN_ROOT,
    DEFAULT_STRICT_TERMINAL,
    build_payload as build_post_v137_payload,
    load_required_yaml,
    rel,
    resolve,
    write_git_state,
    write_yaml,
)

DEFAULT_V139_STATUS = "runs/full_reproduction_status_after_v138/20260525T130000/metrics.yaml"
DEFAULT_V140_CONTINUATION = "runs/post_v139_continuation_boundary/20260525T140000/metrics.yaml"


def status_answer_row(metrics: dict[str, Any]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    boundary = metrics.get("claim_boundary", {})
    completion_evidence = (
        summary.get("full_reproduction_complete") is True
        or summary.get("user_question_answer") == "complete"
        or summary.get("source_completion_claim_allowed") is True
        or boundary.get("full_reproduction_claim_allowed") is True
        or boundary.get("live_hardware_access") is True
        or boundary.get("robot_motion_authorized") is True
        or boundary.get("hardware_writes_authorized") is True
        or boundary.get("force_control_authorized") is True
    )
    status = (
        "status_answer_not_complete_not_evidence"
        if summary.get("audit_passed") is True
        and summary.get("user_question_answer") == "not_fully_reproduced"
        else "status_audit_not_passed"
    )
    return {
        "readiness_id": "full_reproduction_status_after_v138",
        "purpose": (
            "Answer the completion question from the existing post-v138 gate "
            "without upgrading readiness artifacts into completion evidence."
        ),
        "status": status,
        "completion_evidence": bool(completion_evidence),
        "evidence": {
            "audit_run_id": metrics.get("audit_run_id"),
            "audit_passed": summary.get("audit_passed"),
            "user_question_answer": summary.get("user_question_answer"),
            "full_reproduction_complete": summary.get("full_reproduction_complete"),
            "continue_required": summary.get("continue_required"),
            "safe_continuation_mode": summary.get("safe_continuation_mode"),
            "source_completion_claim_allowed": summary.get(
                "source_completion_claim_allowed"
            ),
            "top_blocker": summary.get("top_blocker"),
            "incomplete_requirement_count": summary.get("incomplete_requirement_count"),
            "approved_read_only_run_count": summary.get("approved_read_only_run_count"),
            "approved_read_only_audit_passed_count": summary.get(
                "approved_read_only_audit_passed_count"
            ),
            "readiness_artifacts_are_non_evidence": summary.get(
                "readiness_artifacts_are_non_evidence"
            ),
            "margin_separation_is_non_evidence": summary.get(
                "margin_separation_is_non_evidence"
            ),
            "do_not_mark_goal_complete": summary.get("do_not_mark_goal_complete"),
        },
        "claim_boundary": {
            "status_answer_only": boundary.get("status_answer_only"),
            "post_hoc_existing_metrics_only": boundary.get("post_hoc_existing_metrics_only"),
            "new_simulation_run": boundary.get("new_simulation_run"),
            "live_hardware_access": boundary.get("live_hardware_access"),
            "robot_motion_authorized": boundary.get("robot_motion_authorized"),
            "hardware_writes_authorized": boundary.get("hardware_writes_authorized"),
            "force_control_authorized": boundary.get("force_control_authorized"),
            "full_reproduction_claim_allowed": boundary.get(
                "full_reproduction_claim_allowed"
            ),
            "strict_paper_equivalent_feasibility": boundary.get(
                "strict_paper_equivalent_feasibility"
            ),
            "ur10e_hardware_readiness": boundary.get("ur10e_hardware_readiness"),
            "do_not_mark_goal_complete": boundary.get("do_not_mark_goal_complete"),
        },
    }


def continuation_boundary_row(metrics: dict[str, Any]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    boundary = metrics.get("claim_boundary", {})
    completion_evidence = (
        summary.get("freeform_continue_is_approval") is True
        or summary.get("read_only_sop_can_execute_now") is True
        or summary.get("live_access_authorized_now") is True
        or summary.get("execution_authorized_now") is True
        or boundary.get("approval_record_created") is True
        or boundary.get("approved_read_only_evidence_created") is True
        or boundary.get("completion_claim_allowed") is True
        or boundary.get("live_hardware_access") is True
        or boundary.get("live_hardware_access_authorized") is True
        or boundary.get("execution_authorized") is True
        or boundary.get("robot_motion_authorized") is True
        or boundary.get("hardware_writes_authorized") is True
        or boundary.get("force_control_authorized") is True
    )
    status = (
        "freeform_continuation_guarded_not_evidence"
        if summary.get("audit_passed") is True
        and summary.get("freeform_continue_is_approval") is False
        else "continuation_boundary_not_passed"
    )
    return {
        "readiness_id": "post_v139_continuation_boundary",
        "purpose": (
            "Confirm free-form continuation is not exact read-only SOP approval "
            "and does not authorize live access or execution."
        ),
        "status": status,
        "completion_evidence": bool(completion_evidence),
        "evidence": {
            "audit_run_id": metrics.get("audit_run_id"),
            "audit_passed": summary.get("audit_passed"),
            "approval_phrase_required": summary.get("approval_phrase_required"),
            "exact_approval_phrase_observed": summary.get(
                "exact_approval_phrase_observed"
            ),
            "exact_registered_step_observed": summary.get("exact_registered_step_observed"),
            "approval_is_exact_and_registered": summary.get(
                "approval_is_exact_and_registered"
            ),
            "freeform_continue_is_approval": summary.get("freeform_continue_is_approval"),
            "selected_safe_continuation_mode": summary.get(
                "selected_safe_continuation_mode"
            ),
            "first_read_only_candidate_step_id": summary.get(
                "first_read_only_candidate_step_id"
            ),
            "first_read_only_candidate_worksheet": summary.get(
                "first_read_only_candidate_worksheet"
            ),
            "read_only_sop_can_execute_now": summary.get("read_only_sop_can_execute_now"),
            "live_access_authorized_now": summary.get("live_access_authorized_now"),
            "execution_authorized_now": summary.get("execution_authorized_now"),
            "strict_policy_terminal_family_exhausted": summary.get(
                "strict_policy_terminal_family_exhausted"
            ),
            "repeat_strict_family_recommended": summary.get(
                "repeat_strict_family_recommended"
            ),
            "approved_read_only_run_count": summary.get("approved_read_only_run_count"),
            "approved_read_only_audit_passed_count": summary.get(
                "approved_read_only_audit_passed_count"
            ),
            "do_not_mark_goal_complete": summary.get("do_not_mark_goal_complete"),
        },
        "claim_boundary": {
            "post_hoc_existing_metrics_only": boundary.get("post_hoc_existing_metrics_only"),
            "new_simulation_run": boundary.get("new_simulation_run"),
            "live_hardware_access": boundary.get("live_hardware_access"),
            "live_hardware_access_authorized": boundary.get(
                "live_hardware_access_authorized"
            ),
            "execution_authorized": boundary.get("execution_authorized"),
            "robot_motion_authorized": boundary.get("robot_motion_authorized"),
            "hardware_writes_authorized": boundary.get("hardware_writes_authorized"),
            "force_control_authorized": boundary.get("force_control_authorized"),
            "approval_record_created": boundary.get("approval_record_created"),
            "approved_read_only_evidence_created": boundary.get(
                "approved_read_only_evidence_created"
            ),
            "completion_claim_allowed": boundary.get("completion_claim_allowed"),
            "do_not_mark_goal_complete": boundary.get("do_not_mark_goal_complete"),
        },
    }


def status_answer_violations(row: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    evidence = row["evidence"]
    expected = {
        "audit_passed": True,
        "user_question_answer": "not_fully_reproduced",
        "full_reproduction_complete": False,
        "continue_required": True,
        "safe_continuation_mode": "explicit_read_only_approval_or_nonfinal_offline",
        "source_completion_claim_allowed": False,
        "top_blocker": "approved_read_only_calibration_evidence",
        "incomplete_requirement_count": 6,
        "approved_read_only_run_count": 0,
        "approved_read_only_audit_passed_count": 0,
        "readiness_artifacts_are_non_evidence": True,
        "margin_separation_is_non_evidence": True,
        "do_not_mark_goal_complete": True,
    }
    for key, expected_value in expected.items():
        if evidence.get(key) != expected_value:
            violations.append(
                f"full_reproduction_status_after_v138.evidence.{key} is "
                f"{evidence.get(key)!r}, expected {expected_value!r}"
            )
    boundary_expected = {
        "status_answer_only": True,
        "post_hoc_existing_metrics_only": True,
        "new_simulation_run": False,
        "live_hardware_access": False,
        "robot_motion_authorized": False,
        "hardware_writes_authorized": False,
        "force_control_authorized": False,
        "full_reproduction_claim_allowed": False,
        "strict_paper_equivalent_feasibility": False,
        "ur10e_hardware_readiness": False,
        "do_not_mark_goal_complete": True,
    }
    for key, expected_value in boundary_expected.items():
        if row["claim_boundary"].get(key) != expected_value:
            violations.append(
                f"full_reproduction_status_after_v138.claim_boundary.{key} is "
                f"{row['claim_boundary'].get(key)!r}, expected {expected_value!r}"
            )
    if row["completion_evidence"]:
        violations.append("full_reproduction_status_after_v138 drifted into completion evidence")
    return violations


def continuation_boundary_violations(row: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    evidence = row["evidence"]
    expected = {
        "audit_passed": True,
        "exact_approval_phrase_observed": False,
        "exact_registered_step_observed": False,
        "approval_is_exact_and_registered": False,
        "freeform_continue_is_approval": False,
        "selected_safe_continuation_mode": "await_exact_phase1_approval_or_nonfinal_offline",
        "first_read_only_candidate_step_id": "phase1_mounted_stack_tcp_contact_measurement",
        "first_read_only_candidate_worksheet": "tcp_contact_measurements.csv",
        "read_only_sop_can_execute_now": False,
        "live_access_authorized_now": False,
        "execution_authorized_now": False,
        "strict_policy_terminal_family_exhausted": True,
        "repeat_strict_family_recommended": False,
        "approved_read_only_run_count": 0,
        "approved_read_only_audit_passed_count": 0,
        "do_not_mark_goal_complete": True,
    }
    for key, expected_value in expected.items():
        if evidence.get(key) != expected_value:
            violations.append(
                f"post_v139_continuation_boundary.evidence.{key} is "
                f"{evidence.get(key)!r}, expected {expected_value!r}"
            )
    boundary_expected = {
        "post_hoc_existing_metrics_only": True,
        "new_simulation_run": False,
        "live_hardware_access": False,
        "live_hardware_access_authorized": False,
        "execution_authorized": False,
        "robot_motion_authorized": False,
        "hardware_writes_authorized": False,
        "force_control_authorized": False,
        "approval_record_created": False,
        "approved_read_only_evidence_created": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    for key, expected_value in boundary_expected.items():
        if row["claim_boundary"].get(key) != expected_value:
            violations.append(
                f"post_v139_continuation_boundary.claim_boundary.{key} is "
                f"{row['claim_boundary'].get(key)!r}, expected {expected_value!r}"
            )
    if row["completion_evidence"]:
        violations.append("post_v139_continuation_boundary drifted into completion evidence")
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
    margin_separation_path: pathlib.Path,
    v139_status_path: pathlib.Path,
    v140_continuation_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    post_v137_payload = build_post_v137_payload(
        completion_blockers_path=completion_blockers_path,
        strict_terminal_path=strict_terminal_path,
        matrix_restatement_path=matrix_restatement_path,
        read_only_run_root=read_only_run_root,
        read_only_audit_root=read_only_audit_root,
        orientation_review_root=orientation_review_root,
        orientation_audit_root=orientation_audit_root,
        contact_review_root=contact_review_root,
        contact_audit_root=contact_audit_root,
        packet_coverage_path=packet_coverage_path,
        execution_preflight_path=execution_preflight_path,
        finalization_rehearsal_path=finalization_rehearsal_path,
        margin_separation_path=margin_separation_path,
        run_id=run_id,
    )
    violations = list(post_v137_payload["summary"].get("violations", []))
    v139_status = load_required_yaml(v139_status_path, violations)
    v140_continuation = load_required_yaml(v140_continuation_path, violations)

    readiness_rows = list(post_v137_payload["readiness_artifacts"])
    status_row: dict[str, Any] = {}
    continuation_row: dict[str, Any] = {}
    if v139_status:
        status_row = status_answer_row(v139_status)
        readiness_rows.append(status_row)
        violations.extend(status_answer_violations(status_row))
    if v140_continuation:
        continuation_row = continuation_boundary_row(v140_continuation)
        readiness_rows.append(continuation_row)
        violations.extend(continuation_boundary_violations(continuation_row))

    readiness_completion_evidence_ids = [
        row["readiness_id"] for row in readiness_rows if row["completion_evidence"]
    ]
    source_summary = post_v137_payload["summary"]
    completion_claim_allowed = (
        source_summary["completion_claim_allowed"]
        and not readiness_completion_evidence_ids
        and not violations
    )
    status_evidence = status_row.get("evidence", {})
    continuation_evidence = continuation_row.get("evidence", {})
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "overall_goal_complete": completion_claim_allowed,
        "completion_claim_allowed": completion_claim_allowed,
        "do_not_mark_goal_complete": not completion_claim_allowed,
        "top_blocker": source_summary["top_blocker"],
        "incomplete_requirement_count": source_summary["incomplete_requirement_count"],
        "incomplete_requirement_ids": source_summary["incomplete_requirement_ids"],
        "approved_read_only_run_count": source_summary["approved_read_only_run_count"],
        "approved_read_only_audit_passed_count": source_summary[
            "approved_read_only_audit_passed_count"
        ],
        "accepted_orientation_review_count": source_summary[
            "accepted_orientation_review_count"
        ],
        "accepted_contact_setup_target_review_count": source_summary[
            "accepted_contact_setup_target_review_count"
        ],
        "strict_terminal_pass_count": source_summary["strict_terminal_pass_count"],
        "closed_robustness_cell_count": source_summary["closed_robustness_cell_count"],
        "hardware_gate_report_exists": source_summary["hardware_gate_report_exists"],
        "readiness_artifact_count": len(readiness_rows),
        "readiness_completion_evidence_ids": readiness_completion_evidence_ids,
        "readiness_artifacts_are_non_evidence": not readiness_completion_evidence_ids,
        "finalization_rehearsal_is_non_evidence": source_summary[
            "finalization_rehearsal_is_non_evidence"
        ],
        "margin_separation_is_non_evidence": source_summary[
            "margin_separation_is_non_evidence"
        ],
        "status_answer_is_non_evidence": not status_row.get("completion_evidence", True),
        "continuation_boundary_is_non_evidence": not continuation_row.get(
            "completion_evidence", True
        ),
        "v139_user_question_answer": status_evidence.get("user_question_answer"),
        "v139_full_reproduction_complete": status_evidence.get(
            "full_reproduction_complete"
        ),
        "v139_continue_required": status_evidence.get("continue_required"),
        "v140_freeform_continue_is_approval": continuation_evidence.get(
            "freeform_continue_is_approval"
        ),
        "v140_read_only_sop_can_execute_now": continuation_evidence.get(
            "read_only_sop_can_execute_now"
        ),
        "v140_live_access_authorized_now": continuation_evidence.get(
            "live_access_authorized_now"
        ),
        "v140_execution_authorized_now": continuation_evidence.get(
            "execution_authorized_now"
        ),
        "v140_repeat_strict_family_recommended": continuation_evidence.get(
            "repeat_strict_family_recommended"
        ),
    }
    return {
        "run_source": "post-v140 completion gate audit",
        "audit_run_id": run_id,
        "source_files": {
            **post_v137_payload["source_files"],
            "full_reproduction_status_after_v138": rel(v139_status_path),
            "post_v139_continuation_boundary": rel(v140_continuation_path),
        },
        "actual_scan_roots": post_v137_payload["actual_scan_roots"],
        "summary": summary,
        "completion_checklist": post_v137_payload["completion_checklist"],
        "readiness_artifacts": readiness_rows,
        "claim_boundary": {
            "post_hoc_offline_audit_only": True,
            "readiness_artifacts_do_not_complete_goal": not readiness_completion_evidence_ids,
            "status_answer_is_not_evidence": not status_row.get("completion_evidence", True),
            "continuation_boundary_is_not_evidence": not continuation_row.get(
                "completion_evidence", True
            ),
            "approval_record_created": False,
            "approved_read_only_evidence": False,
            "live_hardware_access_authorized": False,
            "execution_authorized": False,
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
            "Request exact phase1 read-only approval before any live SOP step.",
            "If exact approval is absent, continue only offline non-final research.",
            "Do not upgrade v139 status or v140 continuation-boundary artifacts into evidence.",
            "Do not repeat the exhausted v113-v116 strict-policy and terminal-objective family.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Post-V140 Completion Gate Audit",
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
        f"- Readiness artifact count: `{summary['readiness_artifact_count']}`",
        f"- Readiness artifacts are non-evidence: `{summary['readiness_artifacts_are_non_evidence']}`",
        f"- Status answer is non-evidence: `{summary['status_answer_is_non_evidence']}`",
        f"- Continuation boundary is non-evidence: `{summary['continuation_boundary_is_non_evidence']}`",
        f"- V140 read-only SOP can execute now: `{summary['v140_read_only_sop_can_execute_now']}`",
        f"- V140 live access authorized now: `{summary['v140_live_access_authorized_now']}`",
        f"- V140 execution authorized now: `{summary['v140_execution_authorized_now']}`",
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
            "collect live evidence, authorize live access or execution, move or",
            "configure the robot, accept a contact/setup target, accept an",
            "orientation gate, prove robustness, or establish hardware readiness.",
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
    parser.add_argument("--margin-separation-path", default=DEFAULT_MARGIN_SEPARATION)
    parser.add_argument("--v139-status-path", default=DEFAULT_V139_STATUS)
    parser.add_argument("--v140-continuation-path", default=DEFAULT_V140_CONTINUATION)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "post_v140_completion_gate" / run_id
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
        margin_separation_path=resolve(args.margin_separation_path),
        v139_status_path=resolve(args.v139_status_path),
        v140_continuation_path=resolve(args.v140_continuation_path),
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
