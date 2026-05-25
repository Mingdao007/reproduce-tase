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

from audit_post_v140_completion_gate import (  # noqa: E402
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
    DEFAULT_V139_STATUS,
    DEFAULT_V140_CONTINUATION,
    build_payload as build_post_v140_payload,
    load_required_yaml,
    rel,
    resolve,
    write_git_state,
    write_yaml,
)

DEFAULT_V142_FRONTIER = (
    "runs/robustness_dependency_frontier_after_v141/20260525T160000/metrics.yaml"
)
EXPECTED_PROFILE_OVERLAY_CELLS = ["base_z_plus1mm", "positive_fast_timing_0p0075"]
EXPECTED_GATE_BLOCKED_CELLS = [
    "positive_orientation_gate_0p119",
    "weighted_plus1mm_0p119_gate",
]


def same_items(left: list[str], right: list[str]) -> bool:
    return sorted(left) == sorted(right)


def robustness_frontier_row(metrics: dict[str, Any]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    boundary = metrics.get("claim_boundary", {})
    completion_evidence = (
        summary.get("robustness_complete") is True
        or summary.get("accepted_as_robustness_proof") is True
        or summary.get("candidate_matrix_complete") is True
        or summary.get("all_failed_cells_closed") is True
        or summary.get("closed_cell_count", 0) not in (0, None)
        or summary.get("new_simulation_selected") is True
        or summary.get("additional_failed_cell_execution_recommended") is True
        or boundary.get("failed_cells_closed") is True
        or boundary.get("canonical_controller_change") is True
        or boundary.get("canonical_orientation_gate_change") is True
        or boundary.get("contact_calibration_claim") is True
        or boundary.get("orientation_gate_acceptance_claim") is True
        or boundary.get("robustness_proof") is True
        or boundary.get("strict_paper_equivalent_feasibility") is True
        or boundary.get("hardware_readiness") is True
        or boundary.get("live_hardware_access_authorized") is True
        or boundary.get("execution_authorized") is True
        or boundary.get("robot_motion_authorized") is True
        or boundary.get("hardware_writes_authorized") is True
        or boundary.get("force_control_authorized") is True
    )
    status = (
        "robustness_frontier_classified_not_evidence"
        if summary.get("audit_passed") is True
        and summary.get("robustness_complete") is False
        and summary.get("accepted_as_robustness_proof") is False
        and summary.get("closed_cell_count") == 0
        else "robustness_frontier_not_passed"
    )
    return {
        "readiness_id": "robustness_dependency_frontier_after_v141",
        "purpose": (
            "Classify remaining robustness blockers without accepting profile overlays, "
            "gate/contact changes, simulations, or failed-cell closure as completion evidence."
        ),
        "status": status,
        "completion_evidence": bool(completion_evidence),
        "evidence": {
            "audit_run_id": metrics.get("audit_run_id"),
            "audit_passed": summary.get("audit_passed"),
            "overall_goal_complete": summary.get("overall_goal_complete"),
            "completion_claim_allowed": summary.get("completion_claim_allowed"),
            "robustness_complete": summary.get("robustness_complete"),
            "accepted_as_robustness_proof": summary.get("accepted_as_robustness_proof"),
            "candidate_matrix_complete": summary.get("candidate_matrix_complete"),
            "all_failed_cells_closed": summary.get("all_failed_cells_closed"),
            "closed_cell_count": summary.get("closed_cell_count"),
            "source_failed_cell_count": summary.get("source_failed_cell_count"),
            "frontier_row_count": summary.get("frontier_row_count"),
            "profile_overlay_supported_noncanonical_count": summary.get(
                "profile_overlay_supported_noncanonical_count"
            ),
            "profile_overlay_supported_noncanonical_cell_ids": summary.get(
                "profile_overlay_supported_noncanonical_cell_ids"
            ),
            "gate_or_contact_acceptance_blocked_count": summary.get(
                "gate_or_contact_acceptance_blocked_count"
            ),
            "gate_or_contact_acceptance_blocked_cell_ids": summary.get(
                "gate_or_contact_acceptance_blocked_cell_ids"
            ),
            "new_simulation_selected": summary.get("new_simulation_selected"),
            "additional_failed_cell_execution_recommended": summary.get(
                "additional_failed_cell_execution_recommended"
            ),
            "requires_approved_read_only_evidence_for_closure": summary.get(
                "requires_approved_read_only_evidence_for_closure"
            ),
            "requires_contact_setup_target_acceptance_for_closure": summary.get(
                "requires_contact_setup_target_acceptance_for_closure"
            ),
            "requires_orientation_gate_acceptance_for_gate_rows": summary.get(
                "requires_orientation_gate_acceptance_for_gate_rows"
            ),
            "source_approved_read_only_run_count": summary.get(
                "source_approved_read_only_run_count"
            ),
            "source_approved_read_only_audit_passed_count": summary.get(
                "source_approved_read_only_audit_passed_count"
            ),
            "source_accepted_orientation_review_count": summary.get(
                "source_accepted_orientation_review_count"
            ),
            "source_accepted_contact_setup_target_review_count": summary.get(
                "source_accepted_contact_setup_target_review_count"
            ),
            "source_readiness_completion_evidence_ids": summary.get(
                "source_readiness_completion_evidence_ids"
            ),
            "do_not_mark_goal_complete": summary.get("do_not_mark_goal_complete"),
        },
        "claim_boundary": {
            "post_hoc_existing_metrics_only": boundary.get("post_hoc_existing_metrics_only"),
            "new_simulation_run": boundary.get("new_simulation_run"),
            "new_failed_cell_execution_selected": boundary.get(
                "new_failed_cell_execution_selected"
            ),
            "profile_overlay_is_noncanonical": boundary.get(
                "profile_overlay_is_noncanonical"
            ),
            "failed_cells_closed": boundary.get("failed_cells_closed"),
            "canonical_controller_change": boundary.get("canonical_controller_change"),
            "canonical_orientation_gate_change": boundary.get(
                "canonical_orientation_gate_change"
            ),
            "contact_calibration_claim": boundary.get("contact_calibration_claim"),
            "orientation_gate_acceptance_claim": boundary.get(
                "orientation_gate_acceptance_claim"
            ),
            "robustness_proof": boundary.get("robustness_proof"),
            "strict_paper_equivalent_feasibility": boundary.get(
                "strict_paper_equivalent_feasibility"
            ),
            "hardware_readiness": boundary.get("hardware_readiness"),
            "live_hardware_access_authorized": boundary.get(
                "live_hardware_access_authorized"
            ),
            "execution_authorized": boundary.get("execution_authorized"),
            "robot_motion_authorized": boundary.get("robot_motion_authorized"),
            "hardware_writes_authorized": boundary.get("hardware_writes_authorized"),
            "force_control_authorized": boundary.get("force_control_authorized"),
            "do_not_mark_goal_complete": boundary.get("do_not_mark_goal_complete"),
        },
    }


def robustness_frontier_violations(row: dict[str, Any], metrics: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    evidence = row["evidence"]
    expected = {
        "audit_passed": True,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "robustness_complete": False,
        "accepted_as_robustness_proof": False,
        "candidate_matrix_complete": False,
        "all_failed_cells_closed": False,
        "closed_cell_count": 0,
        "source_failed_cell_count": 4,
        "frontier_row_count": 4,
        "profile_overlay_supported_noncanonical_count": 2,
        "gate_or_contact_acceptance_blocked_count": 2,
        "new_simulation_selected": False,
        "additional_failed_cell_execution_recommended": False,
        "requires_approved_read_only_evidence_for_closure": True,
        "requires_contact_setup_target_acceptance_for_closure": True,
        "requires_orientation_gate_acceptance_for_gate_rows": True,
        "source_approved_read_only_run_count": 0,
        "source_approved_read_only_audit_passed_count": 0,
        "source_accepted_orientation_review_count": 0,
        "source_accepted_contact_setup_target_review_count": 0,
        "source_readiness_completion_evidence_ids": [],
        "do_not_mark_goal_complete": True,
    }
    for key, expected_value in expected.items():
        if evidence.get(key) != expected_value:
            violations.append(
                f"robustness_dependency_frontier_after_v141.evidence.{key} is "
                f"{evidence.get(key)!r}, expected {expected_value!r}"
            )
    if not same_items(
        evidence.get("profile_overlay_supported_noncanonical_cell_ids", []),
        EXPECTED_PROFILE_OVERLAY_CELLS,
    ):
        violations.append(
            "robustness_dependency_frontier_after_v141 profile-overlay cell set drifted"
        )
    if not same_items(
        evidence.get("gate_or_contact_acceptance_blocked_cell_ids", []),
        EXPECTED_GATE_BLOCKED_CELLS,
    ):
        violations.append(
            "robustness_dependency_frontier_after_v141 gate/contact blocked cell set drifted"
        )
    boundary_expected = {
        "post_hoc_existing_metrics_only": True,
        "new_simulation_run": False,
        "new_failed_cell_execution_selected": False,
        "profile_overlay_is_noncanonical": True,
        "failed_cells_closed": False,
        "canonical_controller_change": False,
        "canonical_orientation_gate_change": False,
        "contact_calibration_claim": False,
        "orientation_gate_acceptance_claim": False,
        "robustness_proof": False,
        "strict_paper_equivalent_feasibility": False,
        "hardware_readiness": False,
        "live_hardware_access_authorized": False,
        "execution_authorized": False,
        "robot_motion_authorized": False,
        "hardware_writes_authorized": False,
        "force_control_authorized": False,
        "do_not_mark_goal_complete": True,
    }
    for key, expected_value in boundary_expected.items():
        if row["claim_boundary"].get(key) != expected_value:
            violations.append(
                f"robustness_dependency_frontier_after_v141.claim_boundary.{key} is "
                f"{row['claim_boundary'].get(key)!r}, expected {expected_value!r}"
            )
    for frontier_row in metrics.get("frontier_rows", []):
        cell_id = frontier_row.get("cell_id")
        if frontier_row.get("failed_cell_closed") is not False:
            violations.append(f"{cell_id} unexpectedly closed in robustness frontier")
        if frontier_row.get("canonical_controller_change") is not False:
            violations.append(f"{cell_id} accepted canonical controller change")
        if frontier_row.get("canonical_orientation_gate_change") is not False:
            violations.append(f"{cell_id} accepted canonical orientation gate change")
        if frontier_row.get("robustness_claim") is not False:
            violations.append(f"{cell_id} drifted into robustness claim")
    if row["completion_evidence"]:
        violations.append("robustness_dependency_frontier_after_v141 drifted into completion evidence")
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
    v142_frontier_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    post_v140_payload = build_post_v140_payload(
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
        v139_status_path=v139_status_path,
        v140_continuation_path=v140_continuation_path,
        run_id=run_id,
    )
    violations = list(post_v140_payload["summary"].get("violations", []))
    v142_frontier = load_required_yaml(v142_frontier_path, violations)

    readiness_rows = list(post_v140_payload["readiness_artifacts"])
    frontier_row: dict[str, Any] = {}
    if v142_frontier:
        frontier_row = robustness_frontier_row(v142_frontier)
        readiness_rows.append(frontier_row)
        violations.extend(robustness_frontier_violations(frontier_row, v142_frontier))

    readiness_completion_evidence_ids = [
        row["readiness_id"] for row in readiness_rows if row["completion_evidence"]
    ]
    source_summary = post_v140_payload["summary"]
    completion_claim_allowed = (
        source_summary["completion_claim_allowed"]
        and not readiness_completion_evidence_ids
        and not violations
    )
    frontier_evidence = frontier_row.get("evidence", {})
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
        "status_answer_is_non_evidence": source_summary["status_answer_is_non_evidence"],
        "continuation_boundary_is_non_evidence": source_summary[
            "continuation_boundary_is_non_evidence"
        ],
        "robustness_frontier_is_non_evidence": not frontier_row.get(
            "completion_evidence", True
        ),
        "v142_robustness_complete": frontier_evidence.get("robustness_complete"),
        "v142_accepted_as_robustness_proof": frontier_evidence.get(
            "accepted_as_robustness_proof"
        ),
        "v142_closed_cell_count": frontier_evidence.get("closed_cell_count"),
        "v142_frontier_row_count": frontier_evidence.get("frontier_row_count"),
        "v142_profile_overlay_supported_noncanonical_cell_ids": frontier_evidence.get(
            "profile_overlay_supported_noncanonical_cell_ids"
        ),
        "v142_gate_or_contact_acceptance_blocked_cell_ids": frontier_evidence.get(
            "gate_or_contact_acceptance_blocked_cell_ids"
        ),
        "v142_new_simulation_selected": frontier_evidence.get("new_simulation_selected"),
        "v142_additional_failed_cell_execution_recommended": frontier_evidence.get(
            "additional_failed_cell_execution_recommended"
        ),
    }
    return {
        "run_source": "post-v142 completion gate audit",
        "audit_run_id": run_id,
        "source_files": {
            **post_v140_payload["source_files"],
            "robustness_dependency_frontier_after_v141": rel(v142_frontier_path),
        },
        "actual_scan_roots": post_v140_payload["actual_scan_roots"],
        "summary": summary,
        "completion_checklist": post_v140_payload["completion_checklist"],
        "readiness_artifacts": readiness_rows,
        "claim_boundary": {
            "post_hoc_offline_audit_only": True,
            "readiness_artifacts_do_not_complete_goal": not readiness_completion_evidence_ids,
            "status_answer_is_not_evidence": source_summary["status_answer_is_non_evidence"],
            "continuation_boundary_is_not_evidence": source_summary[
                "continuation_boundary_is_non_evidence"
            ],
            "robustness_frontier_is_not_evidence": not frontier_row.get(
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
            "controller_profile_acceptance_claim": False,
            "failed_robustness_cells_closed": False,
            "strict_paper_equivalent_feasibility": False,
            "robustness_claim": False,
            "hardware_readiness": False,
            "do_not_mark_goal_complete": not completion_claim_allowed,
        },
        "next_actions": [
            "Request exact phase1 read-only approval before any live SOP step.",
            "If exact approval is absent, continue only offline non-final research.",
            "Do not upgrade v142 frontier rows into robustness evidence.",
            "Do not rerun gate-blocked robustness rows as closure evidence before accepted contact/gate evidence exists.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Post-V142 Completion Gate Audit",
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
        f"- Robustness frontier is non-evidence: `{summary['robustness_frontier_is_non_evidence']}`",
        f"- V142 closed cell count: `{summary['v142_closed_cell_count']}`",
        f"- V142 new simulation selected: `{summary['v142_new_simulation_selected']}`",
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
            "configure the robot, accept a controller/profile, accept a",
            "contact/setup target, accept an orientation gate, prove robustness,",
            "or establish hardware readiness.",
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
    parser.add_argument("--v142-frontier-path", default=DEFAULT_V142_FRONTIER)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "post_v142_completion_gate" / run_id
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
        v142_frontier_path=resolve(args.v142_frontier_path),
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
