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

from audit_read_only_phase1_approval_request_freeze import (  # noqa: E402
    APPROVAL_PHRASE,
    DEFAULT_NEXT_STEP_SELECTION,
    DEFAULT_PACKET_AUDIT,
    DEFAULT_PACKET_MARKDOWN,
    DEFAULT_PACKET_METRICS,
    EXPECTED_STEP_ID,
    EXPECTED_TITLE,
    EXPECTED_WORKSHEET,
    FORBIDDEN_ACTIONS,
    build_payload as build_phase1_freeze_payload,
    load_yaml,
    rel,
    resolve,
    sha256_file,
    write_git_state,
    write_yaml,
)

DEFAULT_REGISTRY = "configs/read_only_sop_step_registry.yaml"
DEFAULT_PHASE1_FREEZE = "runs/read_only_phase1_approval_request_freeze/20260525T112000/metrics.yaml"
DEFAULT_POST_V143_GATE = "runs/post_v142_completion_gate/20260525T170000/metrics.yaml"


def registry_phase1_step(registry: dict[str, Any]) -> dict[str, Any]:
    for step in registry.get("steps", []):
        if step.get("step_id") == EXPECTED_STEP_ID:
            return step
    return {}


def validate_registry(registry: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    step = registry_phase1_step(registry)
    if registry.get("approval_phrase") != APPROVAL_PHRASE:
        violations.append("registry approval phrase drifted")
    boundary = registry.get("claim_boundary", {})
    for key in [
        "registry_authorizes_live_access",
        "registry_authorizes_robot_motion",
        "registry_authorizes_configuration_writes",
        "registry_authorizes_zeroing_or_biasing",
        "registry_authorizes_force_control",
        "registry_accepts_contact_model",
        "registry_accepts_setup_target",
        "registry_accepts_orientation_gate",
        "registry_establishes_hardware_readiness",
    ]:
        if boundary.get(key) is not False:
            violations.append(f"registry claim_boundary.{key} is not false")
    if not step:
        violations.append("registry missing phase1 step")
        return {}
    expected = {
        "title": EXPECTED_TITLE,
        "finalizer_eligible": True,
        "allowed_worksheets": [EXPECTED_WORKSHEET],
        "minimum_required_rows": {EXPECTED_WORKSHEET: 1},
        "live_hardware_access_allowed_if_user_approved": True,
        "forbidden_actions": FORBIDDEN_ACTIONS,
    }
    for key, expected_value in expected.items():
        if step.get(key) != expected_value:
            violations.append(
                f"registry phase1 {key} is {step.get(key)!r}, expected {expected_value!r}"
            )
    return step


def validate_post_v143_gate(metrics: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    expected = {
        "audit_passed": True,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
        "top_blocker": "approved_read_only_calibration_evidence",
        "approved_read_only_run_count": 0,
        "approved_read_only_audit_passed_count": 0,
        "accepted_orientation_review_count": 0,
        "accepted_contact_setup_target_review_count": 0,
        "strict_terminal_pass_count": 0,
        "closed_robustness_cell_count": 0,
        "hardware_gate_report_exists": False,
        "readiness_artifact_count": 7,
        "readiness_completion_evidence_ids": [],
        "readiness_artifacts_are_non_evidence": True,
        "robustness_frontier_is_non_evidence": True,
        "v142_closed_cell_count": 0,
        "v142_new_simulation_selected": False,
        "v142_additional_failed_cell_execution_recommended": False,
    }
    for key, expected_value in expected.items():
        if summary.get(key) != expected_value:
            violations.append(
                f"post_v143_gate.summary.{key} is {summary.get(key)!r}, expected {expected_value!r}"
            )
    return summary


def step_scope_matches_registry(packet_step: dict[str, Any], registry_step: dict[str, Any]) -> bool:
    keys = [
        "step_id",
        "title",
        "finalizer_eligible",
        "allowed_worksheets",
        "minimum_required_rows",
        "live_hardware_access_allowed_if_user_approved",
        "forbidden_actions",
    ]
    return all(packet_step.get(key) == registry_step.get(key) for key in keys)


def build_payload(
    *,
    registry_path: pathlib.Path,
    phase1_freeze_path: pathlib.Path,
    post_v143_gate_path: pathlib.Path,
    next_step_selection_path: pathlib.Path,
    packet_metrics_path: pathlib.Path,
    packet_audit_path: pathlib.Path,
    packet_markdown_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    for path in [
        registry_path,
        phase1_freeze_path,
        post_v143_gate_path,
        next_step_selection_path,
        packet_metrics_path,
        packet_audit_path,
        packet_markdown_path,
    ]:
        if not path.exists():
            violations.append(f"missing required source file: {rel(path)}")

    registry = load_yaml(registry_path) if registry_path.exists() else {}
    frozen = load_yaml(phase1_freeze_path) if phase1_freeze_path.exists() else {}
    post_gate = load_yaml(post_v143_gate_path) if post_v143_gate_path.exists() else {}
    registry_step = validate_registry(registry, violations)
    post_gate_summary = validate_post_v143_gate(post_gate, violations)

    current_freeze = build_phase1_freeze_payload(
        next_step_selection_path=next_step_selection_path,
        packet_metrics_path=packet_metrics_path,
        packet_audit_path=packet_audit_path,
        packet_markdown_path=packet_markdown_path,
        run_id=run_id,
    )
    violations.extend(current_freeze["summary"].get("violations", []))

    frozen_summary = frozen.get("summary", {})
    frozen_request = frozen.get("frozen_approval_request", {})
    current_summary = current_freeze["summary"]
    current_packet = current_freeze["packet_freeze"]
    current_hash = sha256_file(packet_markdown_path) if packet_markdown_path.exists() else None
    expected_hash = frozen_summary.get("packet_markdown_sha256")
    packet_hash_unchanged = current_hash == expected_hash
    if frozen_summary.get("audit_passed") is not True:
        violations.append("v129 frozen approval request source is not passed")
    if frozen_summary.get("approval_request_freeze_complete") is not True:
        violations.append("v129 frozen approval request source is not complete")
    if frozen_summary.get("frozen_step_id") != EXPECTED_STEP_ID:
        violations.append("v129 frozen step ID drifted")
    if frozen_summary.get("frozen_worksheet") != EXPECTED_WORKSHEET:
        violations.append("v129 frozen worksheet drifted")
    if frozen_summary.get("approval_phrase_required") != APPROVAL_PHRASE:
        violations.append("v129 frozen approval phrase drifted")
    if not packet_hash_unchanged:
        violations.append("phase1 packet markdown hash changed since v129 freeze")
    if current_summary.get("packet_approval_status") != "not_approved":
        violations.append("current phase1 packet is no longer not_approved")
    if current_summary.get("freeze_authorizes_live_access") is not False:
        violations.append("current phase1 freeze now authorizes live access")
    if current_summary.get("freeze_authorizes_execution") is not False:
        violations.append("current phase1 freeze now authorizes execution")
    if current_summary.get("freeze_creates_approved_evidence") is not False:
        violations.append("current phase1 freeze now creates approved evidence")
    if frozen_request.get("required_approved_step_id") != EXPECTED_STEP_ID:
        violations.append("frozen request required approved step ID drifted")
    if frozen_request.get("allowed_worksheets") != [EXPECTED_WORKSHEET]:
        violations.append("frozen request worksheet scope drifted")
    registry_matches_packet = bool(
        registry_step and step_scope_matches_registry(current_packet.get("selected_step", {}), registry_step)
    )
    if registry_step and not registry_matches_packet:
        violations.append("current packet selected step no longer matches registry phase1 step")

    phase1_packet_fresh = (
        current_summary.get("audit_passed") is True
        and frozen_summary.get("audit_passed") is True
        and packet_hash_unchanged
        and current_summary.get("packet_approval_status") == "not_approved"
        and registry_matches_packet
        and not violations
    )
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "phase1_packet_fresh": bool(phase1_packet_fresh),
        "registry_matches_frozen_packet": registry_matches_packet,
        "packet_hash_unchanged": packet_hash_unchanged,
        "frozen_packet_markdown_sha256": expected_hash,
        "current_packet_markdown_sha256": current_hash,
        "frozen_step_id": EXPECTED_STEP_ID,
        "frozen_worksheet": EXPECTED_WORKSHEET,
        "approval_phrase_required": APPROVAL_PHRASE,
        "exact_step_id_required": True,
        "phase1_packet_still_not_approved": current_summary.get("packet_approval_status")
        == "not_approved",
        "post_v143_completion_gate_binding": post_gate_summary.get("audit_passed") is True
        and post_gate_summary.get("completion_claim_allowed") is False,
        "approved_read_only_run_count": post_gate_summary.get("approved_read_only_run_count"),
        "approved_read_only_audit_passed_count": post_gate_summary.get(
            "approved_read_only_audit_passed_count"
        ),
        "readiness_completion_evidence_ids": post_gate_summary.get(
            "readiness_completion_evidence_ids"
        ),
        "approval_record_created": False,
        "live_access_authorized_now": False,
        "execution_authorized_now": False,
        "approved_read_only_evidence_created": False,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    return {
        "run_source": "phase1 packet freshness after v143 audit",
        "audit_run_id": run_id,
        "source_files": {
            "registry": rel(registry_path),
            "phase1_approval_request_freeze": rel(phase1_freeze_path),
            "post_v143_completion_gate": rel(post_v143_gate_path),
            "read_only_next_step_selection": rel(next_step_selection_path),
            "phase1_packet_metrics": rel(packet_metrics_path),
            "phase1_packet_audit": rel(packet_audit_path),
            "phase1_packet_markdown": rel(packet_markdown_path),
        },
        "summary": summary,
        "freshness_checks": {
            "registry_phase1_step": registry_step,
            "frozen_approval_request": frozen_request,
            "current_phase1_freeze_summary": current_summary,
            "current_packet_freeze": current_packet,
            "post_v143_gate_summary": post_gate_summary,
        },
        "claim_boundary": {
            "freshness_audit_only": True,
            "approval_record_created": False,
            "approved_read_only_evidence": False,
            "live_hardware_access_authorized": False,
            "execution_authorized": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "contact_calibration_claim": False,
            "setup_target_acceptance_claim": False,
            "orientation_gate_acceptance_claim": False,
            "gate_relaxation_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "robustness_claim": False,
            "hardware_readiness": False,
            "completion_claim_allowed": False,
            "do_not_mark_goal_complete": True,
        },
        "next_actions": [
            "Use this packet only if the user gives the exact approval phrase and exact phase1 step scope.",
            "After approval, instantiate a fresh scaffold and fill only tcp_contact_measurements.csv rows.",
            "Without approval, continue only non-final offline work and do not create approved evidence.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Phase1 Packet Freshness After V143",
        "",
        f"Run id: `{payload['audit_run_id']}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Phase1 packet fresh: `{summary['phase1_packet_fresh']}`",
        f"- Registry matches frozen packet: `{summary['registry_matches_frozen_packet']}`",
        f"- Packet hash unchanged: `{summary['packet_hash_unchanged']}`",
        f"- Frozen step ID: `{summary['frozen_step_id']}`",
        f"- Frozen worksheet: `{summary['frozen_worksheet']}`",
        f"- Approval phrase required: `{summary['approval_phrase_required']}`",
        f"- Phase1 packet still not approved: `{summary['phase1_packet_still_not_approved']}`",
        f"- Post-v143 gate binding: `{summary['post_v143_completion_gate_binding']}`",
        f"- Approved read-only runs: `{summary['approved_read_only_run_count']}`",
        f"- Passed approved-read-only audits: `{summary['approved_read_only_audit_passed_count']}`",
        f"- Completion claim allowed: `{summary['completion_claim_allowed']}`",
        f"- Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "## Violations",
        "",
    ]
    if summary["violations"]:
        lines.extend(f"- {violation}" for violation in summary["violations"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The phase1 packet and frozen approval request are still current and",
            "not approved. This audit does not create an approval record, collect",
            "measurements, authorize live access or execution, or create approved",
            "read-only evidence.",
            "",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--registry-path", default=DEFAULT_REGISTRY)
    parser.add_argument("--phase1-freeze-path", default=DEFAULT_PHASE1_FREEZE)
    parser.add_argument("--post-v143-gate-path", default=DEFAULT_POST_V143_GATE)
    parser.add_argument("--next-step-selection-path", default=DEFAULT_NEXT_STEP_SELECTION)
    parser.add_argument("--packet-metrics-path", default=DEFAULT_PACKET_METRICS)
    parser.add_argument("--packet-audit-path", default=DEFAULT_PACKET_AUDIT)
    parser.add_argument("--packet-markdown-path", default=DEFAULT_PACKET_MARKDOWN)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "phase1_packet_freshness_after_v143" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        registry_path=resolve(args.registry_path),
        phase1_freeze_path=resolve(args.phase1_freeze_path),
        post_v143_gate_path=resolve(args.post_v143_gate_path),
        next_step_selection_path=resolve(args.next_step_selection_path),
        packet_metrics_path=resolve(args.packet_metrics_path),
        packet_audit_path=resolve(args.packet_audit_path),
        packet_markdown_path=resolve(args.packet_markdown_path),
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
