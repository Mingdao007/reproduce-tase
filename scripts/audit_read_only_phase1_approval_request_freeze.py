#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import subprocess
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

DEFAULT_NEXT_STEP_SELECTION = "runs/read_only_next_step_selection/20260525T111000/metrics.yaml"
DEFAULT_PACKET_METRICS = "runs/read_only_step_approval_packet/20260525T095500/metrics.yaml"
DEFAULT_PACKET_AUDIT = "runs/read_only_step_approval_packet_audit/20260525T095501/metrics.yaml"
DEFAULT_PACKET_MARKDOWN = "runs/read_only_step_approval_packet/20260525T095500/approval_packet.md"

EXPECTED_STEP_ID = "phase1_mounted_stack_tcp_contact_measurement"
EXPECTED_WORKSHEET = "tcp_contact_measurements.csv"
EXPECTED_TITLE = "Mounted stack TCP/contact point read-only measurement"
APPROVAL_PHRASE = "I approve this read-only measurement step"
FORBIDDEN_ACTIONS = [
    "robot_motion",
    "force_control",
    "zeroing_or_biasing",
    "tcp_payload_cog_urcap_onrobot_or_rtde_writes",
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


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def int_value(mapping: dict[str, Any], key: str) -> int:
    return int(mapping.get(key) or 0)


def false_guard(
    *,
    payload: dict[str, Any],
    group: str,
    keys: list[str],
    source_name: str,
    violations: list[str],
) -> None:
    values = payload.get(group, {})
    for key in keys:
        if values.get(key) is not False:
            violations.append(f"{source_name}.{group}.{key} is not false")


def require_text(text: str, expected: str, label: str, violations: list[str]) -> None:
    if expected not in text:
        violations.append(f"approval packet markdown missing {label}: {expected}")


def validate_next_step_selection(selection: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    summary = selection.get("summary", {})
    first = selection.get("first_candidate", {})
    if summary.get("audit_passed") is not True:
        violations.append("v128 next-step selection source is not passed")
    if summary.get("selection_plan_complete") is not True:
        violations.append("v128 next-step selection source is not complete")
    if summary.get("first_candidate_step_id") != EXPECTED_STEP_ID:
        violations.append("v128 first candidate step does not match phase1")
    if summary.get("first_candidate_worksheet") != EXPECTED_WORKSHEET:
        violations.append("v128 first candidate worksheet does not match phase1")
    if summary.get("approval_phrase_required") != APPROVAL_PHRASE:
        violations.append("v128 approval phrase drifted")
    if summary.get("exact_step_id_required") is not True:
        violations.append("v128 no longer requires exact step ID")
    if int_value(summary, "approved_packet_count") != 0:
        violations.append("v128 source contains approved packets")
    if int_value(summary, "execution_authorizing_packet_count") != 0:
        violations.append("v128 source contains execution-authorizing packets")
    if int_value(summary, "live_access_authorizing_packet_count") != 0:
        violations.append("v128 source contains live-access-authorizing packets")
    if summary.get("approved_read_only_evidence_created") is not False:
        violations.append("v128 source claims approved read-only evidence")
    if summary.get("selection_authorizes_live_access") is not False:
        violations.append("v128 source authorizes live access")
    if summary.get("selection_authorizes_execution") is not False:
        violations.append("v128 source authorizes execution")
    if summary.get("selection_creates_approved_evidence") is not False:
        violations.append("v128 source creates approved evidence")
    if summary.get("overall_goal_complete") is not False:
        violations.append("v128 source marks overall goal complete")
    if summary.get("completion_claim_allowed") is not False:
        violations.append("v128 source allows completion claim")
    if summary.get("do_not_mark_goal_complete") is not True:
        violations.append("v128 source no longer blocks goal completion")
    if first.get("step_id") != EXPECTED_STEP_ID:
        violations.append("v128 first candidate row does not match phase1")
    if first.get("worksheet") != EXPECTED_WORKSHEET:
        violations.append("v128 first candidate row worksheet does not match phase1")
    if first.get("packet_coverage_passed") is not True:
        violations.append("v128 first candidate lacks packet coverage")
    if first.get("preflight_ready") is not True:
        violations.append("v128 first candidate lacks preflight readiness")
    return first


def validate_packet(
    *,
    packet_metrics: dict[str, Any],
    packet_audit: dict[str, Any],
    packet_text: str,
    packet_markdown_path: pathlib.Path,
    violations: list[str],
) -> dict[str, Any]:
    step = packet_metrics.get("selected_step", {})
    request = packet_metrics.get("approval_request", {})
    if packet_metrics.get("status") != "approval_packet_created_not_approved":
        violations.append("packet metrics status is not approval_packet_created_not_approved")
    if step.get("step_id") != EXPECTED_STEP_ID:
        violations.append("packet selected step does not match phase1")
    if step.get("title") != EXPECTED_TITLE:
        violations.append("packet selected title does not match phase1")
    if step.get("finalizer_eligible") is not True:
        violations.append("packet selected step is not finalizer eligible")
    if step.get("allowed_worksheets") != [EXPECTED_WORKSHEET]:
        violations.append("packet selected worksheet scope does not match phase1")
    if step.get("minimum_required_rows", {}).get(EXPECTED_WORKSHEET) != 1:
        violations.append("packet minimum required row count does not match phase1")
    if step.get("live_hardware_access_allowed_if_user_approved") is not True:
        violations.append("packet no longer records conditional live access allowance")
    if step.get("forbidden_actions") != FORBIDDEN_ACTIONS:
        violations.append("packet forbidden action list drifted")

    if request.get("approval_status") != "not_approved":
        violations.append("packet approval status is not not_approved")
    if request.get("required_confirmation_phrase") != APPROVAL_PHRASE:
        violations.append("packet confirmation phrase drifted")
    if request.get("required_approved_step_id") != EXPECTED_STEP_ID:
        violations.append("packet required approved step ID drifted")
    for key in ["operator", "approved_at_utc", "approval_source"]:
        if request.get(key) is not None:
            violations.append(f"packet approval_request.{key} is not null")
    if request.get("packet_authorizes_execution") is not False:
        violations.append("packet now authorizes execution")
    if request.get("packet_authorizes_live_access") is not False:
        violations.append("packet now authorizes live access")

    false_guard(
        payload=packet_metrics,
        group="execution",
        keys=[
            "live_hardware_accessed",
            "robot_motion_commanded",
            "configuration_written",
            "zeroing_or_biasing_performed",
            "force_control_run",
        ],
        source_name="packet_metrics",
        violations=violations,
    )
    false_guard(
        payload=packet_metrics,
        group="claim_boundary",
        keys=[
            "approved_read_only_evidence",
            "contact_calibration_claim",
            "setup_target_acceptance_claim",
            "gate_relaxation_claim",
            "strict_paper_equivalent_feasibility",
            "robustness_claim",
            "hardware_readiness",
        ],
        source_name="packet_metrics",
        violations=violations,
    )
    if packet_metrics.get("claim_boundary", {}).get("approval_packet_only") is not True:
        violations.append("packet claim boundary no longer says approval_packet_only")
    if packet_metrics.get("claim_boundary", {}).get("do_not_mark_goal_complete") is not True:
        violations.append("packet claim boundary no longer blocks goal completion")

    if packet_audit.get("audit_passed") is not True:
        violations.append("packet audit source is not passed")
    if packet_audit.get("packet_status") != "approval_packet_created_not_approved":
        violations.append("packet audit status drifted")
    if packet_audit.get("selected_step", {}).get("step_id") != EXPECTED_STEP_ID:
        violations.append("packet audit selected step drifted")
    if packet_audit.get("approval_request", {}).get("approval_status") != "not_approved":
        violations.append("packet audit approval status drifted")
    if packet_audit.get("artifact_audit", {}).get("heavy_payloads") != []:
        violations.append("packet audit found heavy payloads")

    for expected, label in [
        ("Approval status: `not_approved`", "not-approved status"),
        (f"Step ID: `{EXPECTED_STEP_ID}`", "exact step ID"),
        (f"- `{EXPECTED_WORKSHEET}`", "worksheet scope"),
        (f"Confirmation phrase: `{APPROVAL_PHRASE}`", "approval phrase"),
        ("This packet is not an approval record.", "packet-only boundary"),
        ("It does not authorize live access", "non-authorization boundary"),
    ]:
        require_text(packet_text, expected, label, violations)
    for action in FORBIDDEN_ACTIONS:
        require_text(packet_text, f"- `{action}`", f"forbidden action {action}", violations)

    return {
        "packet_markdown_path": rel(packet_markdown_path),
        "packet_markdown_sha256": sha256_file(packet_markdown_path),
        "packet_markdown_bytes": packet_markdown_path.stat().st_size,
        "selected_step": step,
        "approval_request": request,
    }


def build_payload(
    *,
    next_step_selection_path: pathlib.Path,
    packet_metrics_path: pathlib.Path,
    packet_audit_path: pathlib.Path,
    packet_markdown_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    for path in [
        next_step_selection_path,
        packet_metrics_path,
        packet_audit_path,
        packet_markdown_path,
    ]:
        if not path.exists():
            violations.append(f"missing required source file: {rel(path)}")

    selection = load_yaml(next_step_selection_path) if next_step_selection_path.exists() else {}
    packet_metrics = load_yaml(packet_metrics_path) if packet_metrics_path.exists() else {}
    packet_audit = load_yaml(packet_audit_path) if packet_audit_path.exists() else {}
    packet_text = packet_markdown_path.read_text(encoding="utf-8") if packet_markdown_path.exists() else ""

    first_candidate = validate_next_step_selection(selection, violations)
    packet_freeze = validate_packet(
        packet_metrics=packet_metrics,
        packet_audit=packet_audit,
        packet_text=packet_text,
        packet_markdown_path=packet_markdown_path,
        violations=violations,
    )
    command_plan = first_candidate.get("post_approval_command_plan", [])
    if len(command_plan) != 4:
        violations.append("post-approval command plan does not contain four steps")
    if not command_plan or EXPECTED_STEP_ID not in " ".join(command_plan):
        violations.append("post-approval command plan does not name the expected step ID")
    if not command_plan or EXPECTED_WORKSHEET not in " ".join(command_plan):
        violations.append("post-approval command plan does not name the expected worksheet")

    frozen_prompt = {
        "approval_packet_status": "not_approved",
        "approval_request_text": (
            f"Approve read-only step `{EXPECTED_STEP_ID}` only with the exact phrase "
            f"`{APPROVAL_PHRASE}`. Worksheet scope: `{EXPECTED_WORKSHEET}`."
        ),
        "required_confirmation_phrase": APPROVAL_PHRASE,
        "required_approved_step_id": EXPECTED_STEP_ID,
        "allowed_worksheets": [EXPECTED_WORKSHEET],
        "minimum_required_rows": {EXPECTED_WORKSHEET: 1},
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "post_approval_command_plan": command_plan,
        "operator_must_be_recorded_at_finalization": True,
        "live_hardware_accessed_metadata_required_at_finalization": True,
        "fresh_scaffold_required_after_approval": True,
        "approved_read_only_audit_required_after_finalization": True,
    }

    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "approval_request_freeze_complete": not violations,
        "frozen_step_id": EXPECTED_STEP_ID,
        "frozen_worksheet": EXPECTED_WORKSHEET,
        "approval_phrase_required": APPROVAL_PHRASE,
        "exact_step_id_required": True,
        "packet_markdown_sha256": packet_freeze.get("packet_markdown_sha256"),
        "packet_status": packet_metrics.get("status"),
        "packet_audit_passed": packet_audit.get("audit_passed"),
        "packet_approval_status": packet_metrics.get("approval_request", {}).get(
            "approval_status"
        ),
        "approved_packet_count": 0,
        "execution_authorizing_packet_count": 0,
        "live_access_authorizing_packet_count": 0,
        "approved_read_only_evidence_created": False,
        "freeze_authorizes_live_access": False,
        "freeze_authorizes_execution": False,
        "freeze_creates_approved_evidence": False,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }

    return {
        "run_source": "read-only phase1 approval request freeze audit",
        "audit_run_id": run_id,
        "source_files": {
            "read_only_next_step_selection": rel(next_step_selection_path),
            "phase1_packet_metrics": rel(packet_metrics_path),
            "phase1_packet_audit": rel(packet_audit_path),
            "phase1_packet_markdown": rel(packet_markdown_path),
        },
        "summary": summary,
        "frozen_approval_request": frozen_prompt,
        "packet_freeze": packet_freeze,
        "first_candidate_context": {
            "step_id": first_candidate.get("step_id"),
            "worksheet": first_candidate.get("worksheet"),
            "packet_coverage_passed": first_candidate.get("packet_coverage_passed"),
            "preflight_ready": first_candidate.get("preflight_ready"),
            "selection_authorizes_execution": first_candidate.get("selection_authorizes_execution"),
        },
        "claim_boundary": {
            "approval_request_freeze_only": True,
            "readiness_artifacts_are_non_evidence": True,
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
    frozen = payload["frozen_approval_request"]
    lines = [
        "# Read-Only Phase1 Approval Request Freeze Audit",
        "",
        f"Run id: `{payload['audit_run_id']}`",
        "",
        f"Audit passed: `{summary['audit_passed']}`",
        f"Freeze complete: `{summary['approval_request_freeze_complete']}`",
        f"Frozen step ID: `{summary['frozen_step_id']}`",
        f"Frozen worksheet: `{summary['frozen_worksheet']}`",
        f"Approval phrase required: `{summary['approval_phrase_required']}`",
        f"Exact step ID required: `{summary['exact_step_id_required']}`",
        f"Packet status: `{summary['packet_status']}`",
        f"Packet audit passed: `{summary['packet_audit_passed']}`",
        f"Packet approval status: `{summary['packet_approval_status']}`",
        f"Freeze authorizes execution: `{summary['freeze_authorizes_execution']}`",
        f"Approved read-only evidence created: `{summary['approved_read_only_evidence_created']}`",
        f"Completion claim allowed: `{summary['completion_claim_allowed']}`",
        f"Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "Frozen approval request:",
        "",
        f"- {frozen['approval_request_text']}",
        f"- Allowed worksheet: `{frozen['allowed_worksheets'][0]}`",
        f"- Forbidden actions: `{', '.join(frozen['forbidden_actions'])}`",
        "",
        "Post-approval command plan, only after future explicit approval:",
        "",
    ]
    for command in frozen["post_approval_command_plan"]:
        lines.append(f"- {command}")
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
                "The selected phase1 packet is frozen as a not-approved approval "
                "request. This artifact clarifies exactly what a future approval "
                "would need to name, but it is not itself approval and authorizes "
                "no live access or execution."
            ),
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--next-step-selection-path", default=DEFAULT_NEXT_STEP_SELECTION)
    parser.add_argument("--packet-metrics-path", default=DEFAULT_PACKET_METRICS)
    parser.add_argument("--packet-audit-path", default=DEFAULT_PACKET_AUDIT)
    parser.add_argument("--packet-markdown-path", default=DEFAULT_PACKET_MARKDOWN)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "read_only_phase1_approval_request_freeze" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(
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
