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
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from audit_post_v117_evidence_readiness import (  # noqa: E402
    DEFAULT_READ_ONLY_AUDIT_ROOT,
    DEFAULT_READ_ONLY_RUN_ROOT,
    load_yaml,
    nested_get,
    rel,
    resolve,
    scan_metrics,
    write_git_state,
    write_yaml,
)

EXPECTED_STEP_ID = "phase1_mounted_stack_tcp_contact_measurement"
EXPECTED_WORKSHEET = "tcp_contact_measurements.csv"
APPROVAL_PHRASE = "I approve this read-only measurement step"

DEFAULT_DEPENDENCY_MAP = "runs/read_only_evidence_dependency_map/20260525T110000/metrics.yaml"
DEFAULT_NEXT_STEP_SELECTION = "runs/read_only_next_step_selection/20260525T111000/metrics.yaml"
DEFAULT_APPROVAL_FREEZE = "runs/read_only_phase1_approval_request_freeze/20260525T112000/metrics.yaml"
DEFAULT_FINALIZER_GUARD = (
    "runs/read_only_phase1_preapproval_finalizer_guard/20260525T113000/metrics.yaml"
)
DEFAULT_POST_V122_COMPLETION_GATE = "runs/post_v122_completion_gate/20260525T102000/metrics.yaml"


def load_required_yaml(path: pathlib.Path, violations: list[str]) -> dict[str, Any]:
    if not path.exists():
        violations.append(f"missing required metrics file: {rel(path)}")
        return {}
    return load_yaml(path)


def int_value(mapping: dict[str, Any], key: str) -> int:
    return int(mapping.get(key) or 0)


def require_value(
    mapping: dict[str, Any],
    key: str,
    expected: Any,
    label: str,
    violations: list[str],
) -> None:
    if mapping.get(key) != expected:
        violations.append(f"{label}.{key} is {mapping.get(key)!r}, expected {expected!r}")


def require_false_keys(
    mapping: dict[str, Any],
    keys: list[str],
    label: str,
    violations: list[str],
) -> None:
    for key in keys:
        if mapping.get(key) is not False:
            violations.append(f"{label}.{key} is not false")


def require_true_keys(
    mapping: dict[str, Any],
    keys: list[str],
    label: str,
    violations: list[str],
) -> None:
    for key in keys:
        if mapping.get(key) is not True:
            violations.append(f"{label}.{key} is not true")


def validate_dependency_map(metrics: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    require_true_keys(
        summary,
        ["audit_passed", "dependency_map_complete", "explicit_user_approval_required"],
        "v127.summary",
        violations,
    )
    for key in [
        "mapped_readiness_check_count",
        "finalizer_step_count",
        "mapped_step_count",
        "packet_covered_step_count",
        "preflight_ready_step_count",
    ]:
        require_value(summary, key, 5, "v127.summary", violations)
    require_value(summary, "approved_packet_count", 0, "v127.summary", violations)
    require_value(summary, "execution_authorizing_packet_count", 0, "v127.summary", violations)
    require_value(summary, "live_access_authorizing_packet_count", 0, "v127.summary", violations)
    require_false_keys(
        summary,
        [
            "approved_read_only_evidence_created",
            "live_access_authorized",
            "execution_authorized",
            "overall_goal_complete",
            "completion_claim_allowed",
        ],
        "v127.summary",
        violations,
    )
    require_true_keys(summary, ["do_not_mark_goal_complete"], "v127.summary", violations)
    return {
        "artifact_id": "v127_dependency_map",
        "status": "ready_not_evidence",
        "completion_evidence": False,
        "evidence": {
            "mapped_readiness_check_count": summary.get("mapped_readiness_check_count"),
            "mapped_step_count": summary.get("mapped_step_count"),
            "packet_covered_step_count": summary.get("packet_covered_step_count"),
            "preflight_ready_step_count": summary.get("preflight_ready_step_count"),
            "approved_packet_count": summary.get("approved_packet_count"),
            "approved_read_only_evidence_created": summary.get(
                "approved_read_only_evidence_created"
            ),
        },
    }


def validate_next_step_selection(metrics: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    require_true_keys(
        summary,
        ["audit_passed", "selection_plan_complete", "exact_step_id_required"],
        "v128.summary",
        violations,
    )
    require_value(summary, "candidate_step_count", 5, "v128.summary", violations)
    require_value(summary, "first_candidate_step_id", EXPECTED_STEP_ID, "v128.summary", violations)
    require_value(summary, "first_candidate_worksheet", EXPECTED_WORKSHEET, "v128.summary", violations)
    require_value(summary, "approval_phrase_required", APPROVAL_PHRASE, "v128.summary", violations)
    require_value(summary, "approved_packet_count", 0, "v128.summary", violations)
    require_value(summary, "execution_authorizing_packet_count", 0, "v128.summary", violations)
    require_value(summary, "live_access_authorizing_packet_count", 0, "v128.summary", violations)
    require_false_keys(
        summary,
        [
            "approved_read_only_evidence_created",
            "selection_authorizes_live_access",
            "selection_authorizes_execution",
            "selection_creates_approved_evidence",
            "overall_goal_complete",
            "completion_claim_allowed",
        ],
        "v128.summary",
        violations,
    )
    require_true_keys(
        summary,
        ["explicit_user_approval_required", "do_not_mark_goal_complete"],
        "v128.summary",
        violations,
    )
    return {
        "artifact_id": "v128_next_step_selection",
        "status": "selected_not_approved",
        "completion_evidence": False,
        "evidence": {
            "candidate_step_count": summary.get("candidate_step_count"),
            "first_candidate_step_id": summary.get("first_candidate_step_id"),
            "first_candidate_worksheet": summary.get("first_candidate_worksheet"),
            "approval_phrase_required": summary.get("approval_phrase_required"),
            "approved_read_only_evidence_created": summary.get(
                "approved_read_only_evidence_created"
            ),
        },
    }


def validate_approval_freeze(metrics: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    require_true_keys(
        summary,
        ["audit_passed", "approval_request_freeze_complete", "exact_step_id_required"],
        "v129.summary",
        violations,
    )
    require_value(summary, "frozen_step_id", EXPECTED_STEP_ID, "v129.summary", violations)
    require_value(summary, "frozen_worksheet", EXPECTED_WORKSHEET, "v129.summary", violations)
    require_value(summary, "approval_phrase_required", APPROVAL_PHRASE, "v129.summary", violations)
    require_value(summary, "packet_status", "approval_packet_created_not_approved", "v129.summary", violations)
    require_value(summary, "packet_approval_status", "not_approved", "v129.summary", violations)
    require_value(summary, "approved_packet_count", 0, "v129.summary", violations)
    require_value(summary, "execution_authorizing_packet_count", 0, "v129.summary", violations)
    require_value(summary, "live_access_authorizing_packet_count", 0, "v129.summary", violations)
    require_false_keys(
        summary,
        [
            "approved_read_only_evidence_created",
            "freeze_authorizes_live_access",
            "freeze_authorizes_execution",
            "freeze_creates_approved_evidence",
            "overall_goal_complete",
            "completion_claim_allowed",
        ],
        "v129.summary",
        violations,
    )
    require_true_keys(summary, ["packet_audit_passed", "do_not_mark_goal_complete"], "v129.summary", violations)
    frozen = metrics.get("frozen_approval_request", {})
    require_value(frozen, "required_approved_step_id", EXPECTED_STEP_ID, "v129.frozen_approval_request", violations)
    require_value(
        frozen,
        "required_confirmation_phrase",
        APPROVAL_PHRASE,
        "v129.frozen_approval_request",
        violations,
    )
    require_value(
        frozen,
        "allowed_worksheets",
        [EXPECTED_WORKSHEET],
        "v129.frozen_approval_request",
        violations,
    )
    return {
        "artifact_id": "v129_phase1_approval_request_freeze",
        "status": "frozen_not_approved",
        "completion_evidence": False,
        "evidence": {
            "frozen_step_id": summary.get("frozen_step_id"),
            "frozen_worksheet": summary.get("frozen_worksheet"),
            "packet_status": summary.get("packet_status"),
            "packet_approval_status": summary.get("packet_approval_status"),
            "approved_read_only_evidence_created": summary.get(
                "approved_read_only_evidence_created"
            ),
        },
    }


def validate_finalizer_guard(metrics: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    require_true_keys(
        summary,
        [
            "audit_passed",
            "preapproval_finalizer_guard_complete",
            "source_freeze_audit_passed",
            "temp_only_dry_run",
        ],
        "v130.summary",
        violations,
    )
    require_value(summary, "case_count", 5, "v130.summary", violations)
    require_value(summary, "rejected_case_count", 5, "v130.summary", violations)
    require_value(summary, "scaffold_preserved_case_count", 5, "v130.summary", violations)
    require_value(summary, "approved_read_only_evidence_created_count", 0, "v130.summary", violations)
    require_value(summary, "successful_finalization_count", 0, "v130.summary", violations)
    require_value(summary, "approved_packet_count", 0, "v130.summary", violations)
    require_value(summary, "execution_authorizing_packet_count", 0, "v130.summary", violations)
    require_value(summary, "live_access_authorizing_packet_count", 0, "v130.summary", violations)
    require_false_keys(
        summary,
        [
            "repository_evidence_run_created",
            "approved_read_only_evidence_created",
            "guard_authorizes_live_access",
            "guard_authorizes_execution",
            "guard_creates_approved_evidence",
            "overall_goal_complete",
            "completion_claim_allowed",
        ],
        "v130.summary",
        violations,
    )
    require_true_keys(summary, ["do_not_mark_goal_complete"], "v130.summary", violations)
    return {
        "artifact_id": "v130_preapproval_finalizer_guard",
        "status": "rejection_guard_passed_temp_only",
        "completion_evidence": False,
        "evidence": {
            "case_count": summary.get("case_count"),
            "rejected_case_count": summary.get("rejected_case_count"),
            "scaffold_preserved_case_count": summary.get("scaffold_preserved_case_count"),
            "approved_read_only_evidence_created_count": summary.get(
                "approved_read_only_evidence_created_count"
            ),
            "repository_evidence_run_created": summary.get("repository_evidence_run_created"),
        },
    }


def validate_post_v122_gate(metrics: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    require_true_keys(
        summary,
        ["audit_passed", "do_not_mark_goal_complete", "readiness_artifacts_are_non_evidence"],
        "v123.summary",
        violations,
    )
    require_false_keys(
        summary,
        ["overall_goal_complete", "completion_claim_allowed", "hardware_gate_report_exists"],
        "v123.summary",
        violations,
    )
    require_value(summary, "approved_read_only_run_count", 0, "v123.summary", violations)
    require_value(summary, "approved_read_only_audit_passed_count", 0, "v123.summary", violations)
    require_value(summary, "strict_terminal_pass_count", 0, "v123.summary", violations)
    require_value(summary, "closed_robustness_cell_count", 0, "v123.summary", violations)
    return {
        "artifact_id": "v123_post_v122_completion_gate",
        "status": "historical_gate_incomplete",
        "completion_evidence": False,
        "evidence": {
            "approved_read_only_run_count": summary.get("approved_read_only_run_count"),
            "approved_read_only_audit_passed_count": summary.get(
                "approved_read_only_audit_passed_count"
            ),
            "readiness_artifacts_are_non_evidence": summary.get(
                "readiness_artifacts_are_non_evidence"
            ),
            "completion_claim_allowed": summary.get("completion_claim_allowed"),
        },
    }


def read_only_run_row(row: dict[str, Any]) -> dict[str, Any]:
    metrics = row["metrics"]
    finalization = metrics.get("read_only_evidence_finalization")
    finalization_map = finalization if isinstance(finalization, dict) else {}
    status = metrics.get("status")
    user_confirmed = nested_get(metrics, ["execution", "user_confirmed_read_only_step"])
    approved_step_id = finalization_map.get("approved_step_id")
    approved = status == "approved_read_only_evidence" and user_confirmed is True
    return {
        "run_id": row["run_id"],
        "path": row["path"],
        "status": status,
        "user_confirmed_read_only_step": user_confirmed,
        "live_hardware_accessed": nested_get(metrics, ["execution", "live_hardware_accessed"]),
        "read_only_evidence_finalization_present": isinstance(finalization, dict),
        "approved_step_id": approved_step_id,
        "is_approved_read_only_evidence": approved,
        "is_phase1_approved_evidence": approved and approved_step_id == EXPECTED_STEP_ID,
    }


def read_only_audit_row(row: dict[str, Any]) -> dict[str, Any]:
    metrics = row["metrics"]
    finalization = metrics.get("read_only_evidence_finalization")
    finalization_map = finalization if isinstance(finalization, dict) else {}
    audit_passed = metrics.get("audit_passed") is True
    approved_audit = metrics.get("audit_mode") == "approved-read-only" and audit_passed
    approved_step_id = finalization_map.get("approved_step_id")
    return {
        "run_id": row["run_id"],
        "path": row["path"],
        "audit_mode": metrics.get("audit_mode"),
        "audit_passed": metrics.get("audit_passed"),
        "audited_run": metrics.get("audited_run"),
        "run_status": metrics.get("run_status"),
        "read_only_evidence_finalization_present": isinstance(finalization, dict),
        "approved_step_id": approved_step_id,
        "is_approved_read_only_audit": approved_audit,
        "is_phase1_approved_read_only_audit": approved_audit and approved_step_id == EXPECTED_STEP_ID,
    }


def scan_current_repository(
    *,
    read_only_run_root: pathlib.Path,
    read_only_audit_root: pathlib.Path,
    violations: list[str],
) -> dict[str, Any]:
    run_rows = [read_only_run_row(row) for row in scan_metrics(read_only_run_root)]
    audit_rows = [read_only_audit_row(row) for row in scan_metrics(read_only_audit_root)]

    approved_runs = [row for row in run_rows if row["is_approved_read_only_evidence"]]
    phase1_approved_runs = [row for row in run_rows if row["is_phase1_approved_evidence"]]
    finalization_runs = [row for row in run_rows if row["read_only_evidence_finalization_present"]]
    approved_audits = [row for row in audit_rows if row["is_approved_read_only_audit"]]
    phase1_approved_audits = [
        row for row in audit_rows if row["is_phase1_approved_read_only_audit"]
    ]

    if approved_runs:
        violations.append("current read-only run scan found approved read-only evidence")
    if phase1_approved_runs:
        violations.append("current read-only run scan found phase1 approved evidence")
    if finalization_runs:
        violations.append("current read-only run scan found finalization metadata")
    if approved_audits:
        violations.append("current read-only audit scan found passed approved-read-only audit")
    if phase1_approved_audits:
        violations.append("current read-only audit scan found phase1 approved-read-only audit")

    no_approved_evidence = not (
        approved_runs or phase1_approved_runs or finalization_runs or approved_audits
    )
    return {
        "read_only_run_root": rel(read_only_run_root),
        "read_only_audit_root": rel(read_only_audit_root),
        "run_count": len(run_rows),
        "audit_count": len(audit_rows),
        "approved_read_only_run_count": len(approved_runs),
        "phase1_approved_read_only_run_count": len(phase1_approved_runs),
        "read_only_evidence_finalization_present_count": len(finalization_runs),
        "approved_read_only_audit_passed_count": len(approved_audits),
        "phase1_approved_read_only_audit_passed_count": len(phase1_approved_audits),
        "no_approved_read_only_evidence_found": no_approved_evidence,
        "run_rows": run_rows,
        "audit_rows": audit_rows,
    }


def build_payload(
    *,
    dependency_map_path: pathlib.Path,
    next_step_selection_path: pathlib.Path,
    approval_freeze_path: pathlib.Path,
    finalizer_guard_path: pathlib.Path,
    post_v122_completion_gate_path: pathlib.Path,
    read_only_run_root: pathlib.Path,
    read_only_audit_root: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    dependency_map = load_required_yaml(dependency_map_path, violations)
    next_step_selection = load_required_yaml(next_step_selection_path, violations)
    approval_freeze = load_required_yaml(approval_freeze_path, violations)
    finalizer_guard = load_required_yaml(finalizer_guard_path, violations)
    post_v122_gate = load_required_yaml(post_v122_completion_gate_path, violations)

    boundary_rows: list[dict[str, Any]] = []
    if dependency_map:
        boundary_rows.append(validate_dependency_map(dependency_map, violations))
    if next_step_selection:
        boundary_rows.append(validate_next_step_selection(next_step_selection, violations))
    if approval_freeze:
        boundary_rows.append(validate_approval_freeze(approval_freeze, violations))
    if finalizer_guard:
        boundary_rows.append(validate_finalizer_guard(finalizer_guard, violations))
    if post_v122_gate:
        boundary_rows.append(validate_post_v122_gate(post_v122_gate, violations))

    current_scan = scan_current_repository(
        read_only_run_root=read_only_run_root,
        read_only_audit_root=read_only_audit_root,
        violations=violations,
    )
    current_scan_row = {
        "artifact_id": "current_repository_read_only_evidence_scan",
        "status": "no_approved_evidence_found"
        if current_scan["no_approved_read_only_evidence_found"]
        else "approved_evidence_present",
        "completion_evidence": not current_scan["no_approved_read_only_evidence_found"],
        "evidence": {
            key: current_scan[key]
            for key in [
                "run_count",
                "audit_count",
                "approved_read_only_run_count",
                "phase1_approved_read_only_run_count",
                "read_only_evidence_finalization_present_count",
                "approved_read_only_audit_passed_count",
                "phase1_approved_read_only_audit_passed_count",
                "no_approved_read_only_evidence_found",
            ]
        },
    }
    boundary_rows.append(current_scan_row)

    completion_evidence_ids = [
        row["artifact_id"] for row in boundary_rows if row["completion_evidence"]
    ]
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "phase1_acceptance_boundary_complete": not violations,
        "source_artifact_count": 5,
        "boundary_row_count": len(boundary_rows),
        "completion_evidence_ids": completion_evidence_ids,
        "readiness_artifacts_are_non_evidence": not completion_evidence_ids,
        "current_repository_scan_finds_no_approved_evidence": current_scan[
            "no_approved_read_only_evidence_found"
        ],
        "read_only_run_count": current_scan["run_count"],
        "read_only_audit_count": current_scan["audit_count"],
        "approved_read_only_run_count": current_scan["approved_read_only_run_count"],
        "phase1_approved_read_only_run_count": current_scan[
            "phase1_approved_read_only_run_count"
        ],
        "read_only_evidence_finalization_present_count": current_scan[
            "read_only_evidence_finalization_present_count"
        ],
        "approved_read_only_audit_passed_count": current_scan[
            "approved_read_only_audit_passed_count"
        ],
        "phase1_approved_read_only_audit_passed_count": current_scan[
            "phase1_approved_read_only_audit_passed_count"
        ],
        "selected_phase1_step_id": EXPECTED_STEP_ID,
        "selected_phase1_worksheet": EXPECTED_WORKSHEET,
        "approval_phrase_required": APPROVAL_PHRASE,
        "approved_packet_count": int_value(approval_freeze.get("summary", {}), "approved_packet_count"),
        "execution_authorizing_packet_count": int_value(
            approval_freeze.get("summary", {}), "execution_authorizing_packet_count"
        ),
        "live_access_authorizing_packet_count": int_value(
            approval_freeze.get("summary", {}), "live_access_authorizing_packet_count"
        ),
        "guard_rejected_case_count": int_value(
            finalizer_guard.get("summary", {}), "rejected_case_count"
        ),
        "guard_scaffold_preserved_case_count": int_value(
            finalizer_guard.get("summary", {}), "scaffold_preserved_case_count"
        ),
        "guard_approved_evidence_created_count": int_value(
            finalizer_guard.get("summary", {}), "approved_read_only_evidence_created_count"
        ),
        "repository_evidence_run_created_by_guard": finalizer_guard.get("summary", {}).get(
            "repository_evidence_run_created"
        ),
        "approved_read_only_evidence_created": False,
        "explicit_user_approval_required": True,
        "live_access_authorized": False,
        "execution_authorized": False,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    return {
        "run_source": "phase1 approved-read-only evidence acceptance boundary audit",
        "audit_run_id": run_id,
        "source_files": {
            "read_only_evidence_dependency_map": rel(dependency_map_path),
            "read_only_next_step_selection": rel(next_step_selection_path),
            "phase1_approval_request_freeze": rel(approval_freeze_path),
            "phase1_preapproval_finalizer_guard": rel(finalizer_guard_path),
            "post_v122_completion_gate": rel(post_v122_completion_gate_path),
        },
        "actual_scan_roots": {
            "read_only_runs": current_scan["read_only_run_root"],
            "read_only_audits": current_scan["read_only_audit_root"],
        },
        "summary": summary,
        "boundary_rows": boundary_rows,
        "current_repository_scan": current_scan,
        "prompt_to_artifact_checklist": [
            {
                "requirement": "No approved phase1 read-only evidence exists before explicit approval.",
                "evidence": "current_repository_scan",
                "passed": current_scan["phase1_approved_read_only_run_count"] == 0
                and current_scan["phase1_approved_read_only_audit_passed_count"] == 0,
            },
            {
                "requirement": "The frozen phase1 packet remains not approved and non-authorizing.",
                "evidence": rel(approval_freeze_path),
                "passed": approval_freeze.get("summary", {}).get("packet_approval_status")
                == "not_approved"
                and approval_freeze.get("summary", {}).get("freeze_authorizes_execution") is False,
            },
            {
                "requirement": "Preapproval finalizer misuse paths create no repository evidence.",
                "evidence": rel(finalizer_guard_path),
                "passed": finalizer_guard.get("summary", {}).get(
                    "approved_read_only_evidence_created_count"
                )
                == 0
                and finalizer_guard.get("summary", {}).get("repository_evidence_run_created")
                is False,
            },
            {
                "requirement": "Readiness maps/selectors remain non-evidence.",
                "evidence": [rel(dependency_map_path), rel(next_step_selection_path)],
                "passed": not completion_evidence_ids,
            },
        ],
        "claim_boundary": {
            "post_hoc_offline_audit_only": True,
            "phase1_acceptance_boundary_only": True,
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
        "next_actions": [
            "Request explicit user approval before any live read-only phase1 measurement.",
            "If approval is absent, continue only non-final offline work.",
            "After approval, create a fresh scaffold and finalize only tcp_contact_measurements.csv.",
            "Do not treat v127-v131 readiness or guard artifacts as approved evidence.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Phase1 Approved-Read-Only Evidence Acceptance Boundary Audit",
        "",
        f"Run id: `{payload['audit_run_id']}`",
        "",
        f"Audit passed: `{summary['audit_passed']}`",
        f"Boundary complete: `{summary['phase1_acceptance_boundary_complete']}`",
        f"Current repository scan finds no approved evidence: `{summary['current_repository_scan_finds_no_approved_evidence']}`",
        f"Read-only run count: `{summary['read_only_run_count']}`",
        f"Read-only audit count: `{summary['read_only_audit_count']}`",
        f"Approved read-only runs: `{summary['approved_read_only_run_count']}`",
        f"Phase1 approved read-only runs: `{summary['phase1_approved_read_only_run_count']}`",
        f"Passed approved-read-only audits: `{summary['approved_read_only_audit_passed_count']}`",
        f"Phase1 passed approved-read-only audits: `{summary['phase1_approved_read_only_audit_passed_count']}`",
        f"Finalization metadata present in run scan: `{summary['read_only_evidence_finalization_present_count']}`",
        f"Guard rejected cases: `{summary['guard_rejected_case_count']}`",
        f"Guard approved evidence created: `{summary['guard_approved_evidence_created_count']}`",
        f"Completion claim allowed: `{summary['completion_claim_allowed']}`",
        f"Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "## Boundary Rows",
        "",
    ]
    for row in payload["boundary_rows"]:
        lines.append(
            f"- `{row['artifact_id']}`: status `{row['status']}`, completion evidence `{row['completion_evidence']}`"
        )
    lines.extend(["", "## Violations", ""])
    if summary["violations"]:
        lines.extend(f"- {violation}" for violation in summary["violations"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "This audit scans the current repository evidence directories after "
                "v130 and cross-checks the v127-v130 readiness/guard chain. It "
                "confirms there is still no approved phase1 read-only evidence and "
                "no passed approved-read-only audit. The active goal remains "
                "incomplete until explicit approval is given and evidence is "
                "collected, finalized, and audited."
            ),
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--dependency-map-path", default=DEFAULT_DEPENDENCY_MAP)
    parser.add_argument("--next-step-selection-path", default=DEFAULT_NEXT_STEP_SELECTION)
    parser.add_argument("--approval-freeze-path", default=DEFAULT_APPROVAL_FREEZE)
    parser.add_argument("--finalizer-guard-path", default=DEFAULT_FINALIZER_GUARD)
    parser.add_argument("--post-v122-completion-gate-path", default=DEFAULT_POST_V122_COMPLETION_GATE)
    parser.add_argument("--read-only-run-root", default=DEFAULT_READ_ONLY_RUN_ROOT)
    parser.add_argument("--read-only-audit-root", default=DEFAULT_READ_ONLY_AUDIT_ROOT)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "phase1_approved_evidence_acceptance_boundary" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        dependency_map_path=resolve(args.dependency_map_path),
        next_step_selection_path=resolve(args.next_step_selection_path),
        approval_freeze_path=resolve(args.approval_freeze_path),
        finalizer_guard_path=resolve(args.finalizer_guard_path),
        post_v122_completion_gate_path=resolve(args.post_v122_completion_gate_path),
        read_only_run_root=resolve(args.read_only_run_root),
        read_only_audit_root=resolve(args.read_only_audit_root),
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
