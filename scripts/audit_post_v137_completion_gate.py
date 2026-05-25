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

from audit_post_v135_completion_gate import (  # noqa: E402
    DEFAULT_COMPLETION_BLOCKERS,
    DEFAULT_CONTACT_AUDIT_ROOT,
    DEFAULT_CONTACT_REVIEW_ROOT,
    DEFAULT_EXECUTION_PREFLIGHT,
    DEFAULT_FINALIZATION_REHEARSAL,
    DEFAULT_MATRIX_RESTATEMENT,
    DEFAULT_ORIENTATION_AUDIT_ROOT,
    DEFAULT_ORIENTATION_REVIEW_ROOT,
    DEFAULT_PACKET_COVERAGE,
    DEFAULT_READ_ONLY_AUDIT_ROOT,
    DEFAULT_READ_ONLY_RUN_ROOT,
    DEFAULT_STRICT_TERMINAL,
    build_payload as build_post_v135_payload,
    load_required_yaml,
    rel,
    resolve,
    write_git_state,
    write_yaml,
)

DEFAULT_MARGIN_SEPARATION = (
    "runs/strict_vs_diagnostic_margin_separation/20260525T124000/metrics.yaml"
)
MIN_EXPECTED_MARGIN_RATIO = 10.0


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


def margin_separation_row(metrics: dict[str, Any]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    boundary = metrics.get("claim_boundary", {})
    completion_evidence = (
        summary.get("v85_margin_can_close_strict_paper_equivalent_goal") is True
        or summary.get("replacement_gate_accepted") is True
        or summary.get("overall_goal_complete") is True
        or summary.get("completion_claim_allowed") is True
        or int(summary.get("approved_read_only_run_count") or 0) > 0
        or int(summary.get("approved_read_only_audit_passed_count") or 0) > 0
        or boundary.get("strict_terminal_relaxation_accepted") is True
        or boundary.get("strict_paper_equivalent_feasibility") is True
        or boundary.get("canonical_orientation_gate_change") is True
        or boundary.get("contact_calibration_claim") is True
        or boundary.get("robustness_claim") is True
        or boundary.get("hardware_readiness") is True
        or boundary.get("robot_motion_authorized") is True
        or boundary.get("hardware_writes_authorized") is True
        or boundary.get("force_control_authorized") is True
    )
    status = (
        "diagnostic_margin_separated_not_evidence"
        if summary.get("audit_passed") is True
        and summary.get("strict_vs_diagnostic_margin_separation_complete") is True
        else "audit_not_passed"
    )
    return {
        "readiness_id": "strict_vs_diagnostic_margin_separation",
        "purpose": (
            "Confirm the v85 diagnostic orientation/contact margin stays separate "
            "from strict paper-equivalent feasibility and completion evidence."
        ),
        "status": status,
        "completion_evidence": bool(completion_evidence),
        "evidence": {
            "audit_run_id": metrics.get("audit_run_id"),
            "strict_vs_diagnostic_margin_separation_complete": summary.get(
                "strict_vs_diagnostic_margin_separation_complete"
            ),
            "source_calibration_margin_present": summary.get(
                "source_calibration_margin_present"
            ),
            "source_relaxation_budget_audit_passed": summary.get(
                "source_relaxation_budget_audit_passed"
            ),
            "source_completion_gate_audit_passed": summary.get(
                "source_completion_gate_audit_passed"
            ),
            "diagnostic_required_normal_rotation_rad": summary.get(
                "diagnostic_required_normal_rotation_rad"
            ),
            "strict_orientation_increase_rad": summary.get(
                "strict_orientation_increase_rad"
            ),
            "strict_tangential_increase_m": summary.get("strict_tangential_increase_m"),
            "strict_force_increase_N": summary.get("strict_force_increase_N"),
            "strict_to_diagnostic_orientation_margin_ratio": summary.get(
                "strict_to_diagnostic_orientation_margin_ratio"
            ),
            "minimum_uniform_multiplier": summary.get("minimum_uniform_multiplier"),
            "minimum_uniform_requires_all_three_scalar_gates": summary.get(
                "minimum_uniform_requires_all_three_scalar_gates"
            ),
            "v85_margin_can_close_strict_orientation": summary.get(
                "v85_margin_can_close_strict_orientation"
            ),
            "v85_margin_can_close_strict_uniform_relaxation": summary.get(
                "v85_margin_can_close_strict_uniform_relaxation"
            ),
            "v85_margin_can_close_strict_paper_equivalent_goal": summary.get(
                "v85_margin_can_close_strict_paper_equivalent_goal"
            ),
            "replacement_gate_accepted": summary.get("replacement_gate_accepted"),
            "approved_read_only_run_count": summary.get("approved_read_only_run_count"),
            "approved_read_only_audit_passed_count": summary.get(
                "approved_read_only_audit_passed_count"
            ),
            "overall_goal_complete": summary.get("overall_goal_complete"),
            "completion_claim_allowed": summary.get("completion_claim_allowed"),
            "do_not_mark_goal_complete": summary.get("do_not_mark_goal_complete"),
        },
        "claim_boundary": {
            "post_hoc_existing_metrics_only": boundary.get("post_hoc_existing_metrics_only"),
            "new_optimization_run": boundary.get("new_optimization_run"),
            "diagnostic_margin_only": boundary.get("diagnostic_margin_only"),
            "strict_terminal_relaxation_accepted": boundary.get(
                "strict_terminal_relaxation_accepted"
            ),
            "strict_paper_equivalent_feasibility": boundary.get(
                "strict_paper_equivalent_feasibility"
            ),
            "canonical_orientation_gate_change": boundary.get(
                "canonical_orientation_gate_change"
            ),
            "contact_calibration_claim": boundary.get("contact_calibration_claim"),
            "robustness_claim": boundary.get("robustness_claim"),
            "hardware_readiness": boundary.get("hardware_readiness"),
            "robot_motion_authorized": boundary.get("robot_motion_authorized"),
            "hardware_writes_authorized": boundary.get("hardware_writes_authorized"),
            "force_control_authorized": boundary.get("force_control_authorized"),
            "do_not_mark_goal_complete": boundary.get("do_not_mark_goal_complete"),
        },
    }


def margin_safety_violations(row: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    evidence = row["evidence"]
    expected = {
        "strict_vs_diagnostic_margin_separation_complete": True,
        "source_calibration_margin_present": True,
        "source_relaxation_budget_audit_passed": True,
        "source_completion_gate_audit_passed": True,
        "minimum_uniform_requires_all_three_scalar_gates": True,
        "v85_margin_can_close_strict_orientation": False,
        "v85_margin_can_close_strict_uniform_relaxation": False,
        "v85_margin_can_close_strict_paper_equivalent_goal": False,
        "replacement_gate_accepted": False,
        "approved_read_only_run_count": 0,
        "approved_read_only_audit_passed_count": 0,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    for key, expected_value in expected.items():
        if evidence.get(key) != expected_value:
            violations.append(
                f"strict_vs_diagnostic_margin_separation.evidence.{key} is "
                f"{evidence.get(key)!r}, expected {expected_value!r}"
            )
    ratio = evidence.get("strict_to_diagnostic_orientation_margin_ratio")
    if not isinstance(ratio, (int, float)) or ratio < MIN_EXPECTED_MARGIN_RATIO:
        violations.append(
            "strict_vs_diagnostic_margin_separation.evidence."
            f"strict_to_diagnostic_orientation_margin_ratio is {ratio!r}, "
            f"expected at least {MIN_EXPECTED_MARGIN_RATIO}"
        )
    if row["completion_evidence"]:
        violations.append("strict_vs_diagnostic_margin_separation drifted into completion evidence")

    boundary = row["claim_boundary"]
    boundary_expected = {
        "post_hoc_existing_metrics_only": True,
        "new_optimization_run": False,
        "diagnostic_margin_only": True,
        "strict_terminal_relaxation_accepted": False,
        "strict_paper_equivalent_feasibility": False,
        "canonical_orientation_gate_change": False,
        "contact_calibration_claim": False,
        "robustness_claim": False,
        "hardware_readiness": False,
        "robot_motion_authorized": False,
        "hardware_writes_authorized": False,
        "force_control_authorized": False,
        "do_not_mark_goal_complete": True,
    }
    for key, expected_value in boundary_expected.items():
        if boundary.get(key) != expected_value:
            violations.append(
                f"strict_vs_diagnostic_margin_separation.claim_boundary.{key} is "
                f"{boundary.get(key)!r}, expected {expected_value!r}"
            )
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
    run_id: str,
) -> dict[str, Any]:
    post_v135_payload = build_post_v135_payload(
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
        run_id=run_id,
    )
    violations = list(post_v135_payload["summary"].get("violations", []))
    margin_separation = load_required_yaml(margin_separation_path, violations)

    readiness_rows = list(post_v135_payload["readiness_artifacts"])
    margin_row: dict[str, Any] = {}
    if margin_separation:
        margin_row = margin_separation_row(margin_separation)
        readiness_rows.append(margin_row)
        violations.extend(margin_safety_violations(margin_row))

    readiness_completion_evidence_ids = [
        row["readiness_id"] for row in readiness_rows if row["completion_evidence"]
    ]
    post_summary = post_v135_payload["summary"]
    completion_claim_allowed = (
        post_summary["completion_claim_allowed"]
        and not readiness_completion_evidence_ids
        and not violations
    )
    margin_evidence = margin_row.get("evidence", {})
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "overall_goal_complete": completion_claim_allowed,
        "completion_claim_allowed": completion_claim_allowed,
        "do_not_mark_goal_complete": not completion_claim_allowed,
        "top_blocker": post_summary["top_blocker"],
        "incomplete_requirement_count": post_summary["incomplete_requirement_count"],
        "incomplete_requirement_ids": post_summary["incomplete_requirement_ids"],
        "approved_read_only_run_count": post_summary["approved_read_only_run_count"],
        "approved_read_only_audit_passed_count": post_summary[
            "approved_read_only_audit_passed_count"
        ],
        "accepted_orientation_review_count": post_summary["accepted_orientation_review_count"],
        "accepted_contact_setup_target_review_count": post_summary[
            "accepted_contact_setup_target_review_count"
        ],
        "strict_terminal_pass_count": post_summary["strict_terminal_pass_count"],
        "closed_robustness_cell_count": post_summary["closed_robustness_cell_count"],
        "hardware_gate_report_exists": post_summary["hardware_gate_report_exists"],
        "readiness_artifact_count": len(readiness_rows),
        "readiness_completion_evidence_ids": readiness_completion_evidence_ids,
        "readiness_artifacts_are_non_evidence": not readiness_completion_evidence_ids,
        "finalization_rehearsal_is_non_evidence": post_summary[
            "finalization_rehearsal_is_non_evidence"
        ],
        "margin_separation_is_non_evidence": not margin_row.get("completion_evidence", True),
        "margin_strict_to_diagnostic_orientation_ratio": margin_evidence.get(
            "strict_to_diagnostic_orientation_margin_ratio"
        ),
        "margin_v85_can_close_strict_paper_equivalent_goal": margin_evidence.get(
            "v85_margin_can_close_strict_paper_equivalent_goal"
        ),
        "margin_replacement_gate_accepted": margin_evidence.get("replacement_gate_accepted"),
        "margin_minimum_uniform_requires_all_three_scalar_gates": margin_evidence.get(
            "minimum_uniform_requires_all_three_scalar_gates"
        ),
    }
    return {
        "run_source": "post-v137 completion gate audit",
        "audit_run_id": run_id,
        "source_files": {
            **post_v135_payload["source_files"],
            "strict_vs_diagnostic_margin_separation": rel(margin_separation_path),
        },
        "actual_scan_roots": post_v135_payload["actual_scan_roots"],
        "summary": summary,
        "completion_checklist": post_v135_payload["completion_checklist"],
        "readiness_artifacts": readiness_rows,
        "claim_boundary": {
            "post_hoc_offline_audit_only": True,
            "readiness_artifacts_do_not_complete_goal": not readiness_completion_evidence_ids,
            "finalization_rehearsal_is_not_evidence": post_summary[
                "finalization_rehearsal_is_non_evidence"
            ],
            "margin_separation_is_not_evidence": not margin_row.get("completion_evidence", True),
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
            "Treat v137 margin separation as claim-boundary evidence, not completion evidence.",
            "Do not accept contact/setup-target or orientation-gate changes from simulation recovery alone.",
            "Avoid repeating v113-v116 policy, timing, seed, and terminal-objective families.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Post-V137 Completion Gate Audit",
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
        f"- Strict terminal pass count: `{summary['strict_terminal_pass_count']}`",
        f"- Closed robustness cells: `{summary['closed_robustness_cell_count']}`",
        f"- Hardware gate report exists: `{summary['hardware_gate_report_exists']}`",
        f"- Readiness artifacts are non-evidence: `{summary['readiness_artifacts_are_non_evidence']}`",
        f"- Margin separation is non-evidence: `{summary['margin_separation_is_non_evidence']}`",
        f"- Margin strict/diagnostic orientation ratio: `{summary['margin_strict_to_diagnostic_orientation_ratio']}`",
        f"- Replacement gate accepted: `{summary['margin_replacement_gate_accepted']}`",
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
    parser.add_argument("--margin-separation-path", default=DEFAULT_MARGIN_SEPARATION)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "post_v137_completion_gate" / run_id
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
