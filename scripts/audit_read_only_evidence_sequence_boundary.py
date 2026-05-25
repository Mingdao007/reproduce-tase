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

DEFAULT_DEPENDENCY_MAP = "runs/read_only_evidence_dependency_map/20260525T110000/metrics.yaml"
DEFAULT_NEXT_STEP_SELECTION = "runs/read_only_next_step_selection/20260525T111000/metrics.yaml"
DEFAULT_ACCEPTANCE_BOUNDARY = (
    "runs/phase1_approved_evidence_acceptance_boundary/20260525T114000/metrics.yaml"
)

APPROVAL_PHRASE = "I approve this read-only measurement step"
FIRST_STEP_ID = "phase1_mounted_stack_tcp_contact_measurement"
FIRST_WORKSHEET = "tcp_contact_measurements.csv"
EXPECTED_SEQUENCE = [
    "phase1_mounted_stack_tcp_contact_measurement",
    "phase2_ksm_contact_patch_convention",
    "phase3_plane_normal_external_measurement",
    "phase4_force_source_read_only_comparison",
    "phase5_orientation_gate_semantics_evidence",
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


def load_required_yaml(path: pathlib.Path, violations: list[str]) -> dict[str, Any]:
    if not path.exists():
        violations.append(f"missing required metrics file: {rel(path)}")
        return {}
    return load_yaml(path)


def require_value(
    mapping: dict[str, Any],
    key: str,
    expected: Any,
    label: str,
    violations: list[str],
) -> None:
    if mapping.get(key) != expected:
        violations.append(f"{label}.{key} is {mapping.get(key)!r}, expected {expected!r}")


def require_false(mapping: dict[str, Any], key: str, label: str, violations: list[str]) -> None:
    if mapping.get(key) is not False:
        violations.append(f"{label}.{key} is not false")


def require_true(mapping: dict[str, Any], key: str, label: str, violations: list[str]) -> None:
    if mapping.get(key) is not True:
        violations.append(f"{label}.{key} is not true")


def validate_dependency_map(metrics: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    for key in ["audit_passed", "dependency_map_complete", "explicit_user_approval_required"]:
        require_true(summary, key, "v127.summary", violations)
    for key in [
        "mapped_readiness_check_count",
        "finalizer_step_count",
        "mapped_step_count",
        "packet_covered_step_count",
        "preflight_ready_step_count",
    ]:
        require_value(summary, key, 5, "v127.summary", violations)
    for key in [
        "approved_packet_count",
        "execution_authorizing_packet_count",
        "live_access_authorizing_packet_count",
    ]:
        require_value(summary, key, 0, "v127.summary", violations)
    for key in [
        "approved_read_only_evidence_created",
        "live_access_authorized",
        "execution_authorized",
        "overall_goal_complete",
        "completion_claim_allowed",
    ]:
        require_false(summary, key, "v127.summary", violations)
    require_true(summary, "do_not_mark_goal_complete", "v127.summary", violations)

    rows = metrics.get("step_dependency_rows", [])
    if len(rows) != len(EXPECTED_SEQUENCE):
        violations.append(
            f"v127.step_dependency_rows count is {len(rows)}, expected {len(EXPECTED_SEQUENCE)}"
        )
    row_by_step = {row.get("step_id"): row for row in rows}
    for step_id in EXPECTED_SEQUENCE:
        if step_id not in row_by_step:
            violations.append(f"v127.step_dependency_rows missing expected step: {step_id}")
            continue
        row = row_by_step[step_id]
        for key in ["finalizer_eligible", "packet_coverage_passed", "preflight_ready"]:
            require_true(row, key, f"v127.step[{step_id}]", violations)
        require_true(row, "approval_required", f"v127.step[{step_id}]", violations)
        for key in ["live_authorized_now", "execution_authorized_now", "creates_completion_evidence"]:
            require_false(row, key, f"v127.step[{step_id}]", violations)
    return row_by_step


def validate_next_step_selection(metrics: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    for key in ["audit_passed", "selection_plan_complete", "exact_step_id_required"]:
        require_true(summary, key, "v128.summary", violations)
    require_value(summary, "candidate_step_count", 5, "v128.summary", violations)
    require_value(summary, "recommended_sequence_step_ids", EXPECTED_SEQUENCE, "v128.summary", violations)
    require_value(summary, "first_candidate_step_id", FIRST_STEP_ID, "v128.summary", violations)
    require_value(summary, "first_candidate_worksheet", FIRST_WORKSHEET, "v128.summary", violations)
    require_value(summary, "approval_phrase_required", APPROVAL_PHRASE, "v128.summary", violations)
    for key in [
        "approved_packet_count",
        "execution_authorizing_packet_count",
        "live_access_authorizing_packet_count",
    ]:
        require_value(summary, key, 0, "v128.summary", violations)
    for key in [
        "approved_read_only_evidence_created",
        "selection_authorizes_live_access",
        "selection_authorizes_execution",
        "selection_creates_approved_evidence",
        "overall_goal_complete",
        "completion_claim_allowed",
    ]:
        require_false(summary, key, "v128.summary", violations)
    for key in ["explicit_user_approval_required", "do_not_mark_goal_complete"]:
        require_true(summary, key, "v128.summary", violations)

    candidate_rows = metrics.get("candidate_rows", [])
    candidate_by_step = {row.get("step_id"): row for row in candidate_rows}
    for index, step_id in enumerate(EXPECTED_SEQUENCE, start=1):
        if step_id not in candidate_by_step:
            violations.append(f"v128.candidate_rows missing expected step: {step_id}")
            continue
        row = candidate_by_step[step_id]
        require_value(row, "sequence_index", index, f"v128.candidate[{step_id}]", violations)
        for key in ["packet_coverage_passed", "preflight_ready", "exact_step_id_required"]:
            require_true(row, key, f"v128.candidate[{step_id}]", violations)
        for key in [
            "approval_record_exists_now",
            "live_access_authorized_now",
            "execution_authorized_now",
            "approved_evidence_created_now",
            "selection_authorizes_execution",
        ]:
            require_false(row, key, f"v128.candidate[{step_id}]", violations)
    return candidate_by_step


def validate_acceptance_boundary(metrics: dict[str, Any], violations: list[str]) -> None:
    summary = metrics.get("summary", {})
    for key in [
        "audit_passed",
        "phase1_acceptance_boundary_complete",
        "readiness_artifacts_are_non_evidence",
        "current_repository_scan_finds_no_approved_evidence",
        "explicit_user_approval_required",
        "do_not_mark_goal_complete",
    ]:
        require_true(summary, key, "v131.summary", violations)
    for key in [
        "approved_read_only_run_count",
        "phase1_approved_read_only_run_count",
        "read_only_evidence_finalization_present_count",
        "approved_read_only_audit_passed_count",
        "phase1_approved_read_only_audit_passed_count",
        "approved_packet_count",
        "execution_authorizing_packet_count",
        "live_access_authorizing_packet_count",
        "guard_approved_evidence_created_count",
    ]:
        require_value(summary, key, 0, "v131.summary", violations)
    for key in [
        "repository_evidence_run_created_by_guard",
        "approved_read_only_evidence_created",
        "live_access_authorized",
        "execution_authorized",
        "overall_goal_complete",
        "completion_claim_allowed",
    ]:
        require_false(summary, key, "v131.summary", violations)
    require_value(summary, "selected_phase1_step_id", FIRST_STEP_ID, "v131.summary", violations)
    require_value(summary, "selected_phase1_worksheet", FIRST_WORKSHEET, "v131.summary", violations)


def sequence_rows(
    row_by_step: dict[str, dict[str, Any]],
    candidate_by_step: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, step_id in enumerate(EXPECTED_SEQUENCE, start=1):
        dependency = row_by_step.get(step_id, {})
        candidate = candidate_by_step.get(step_id, {})
        rows.append(
            {
                "sequence_index": index,
                "step_id": step_id,
                "readiness_check": dependency.get("readiness_check"),
                "title": dependency.get("title") or candidate.get("title"),
                "worksheet": dependency.get("worksheet") or candidate.get("worksheet"),
                "chain_role": "first_selected_phase1" if index == 1 else "remaining_required_step",
                "is_selected_phase1_first_step": index == 1,
                "would_remain_after_phase1_only": index > 1,
                "packet_coverage_passed": dependency.get("packet_coverage_passed"),
                "preflight_ready": dependency.get("preflight_ready"),
                "valid_not_approved_packet_count": dependency.get("valid_not_approved_packet_count"),
                "approval_required": dependency.get("approval_required"),
                "separate_exact_user_approval_required": True,
                "approval_record_exists_now": candidate.get("approval_record_exists_now"),
                "live_access_authorized_now": dependency.get("live_authorized_now"),
                "execution_authorized_now": dependency.get("execution_authorized_now"),
                "approved_evidence_created_now": candidate.get("approved_evidence_created_now"),
                "bundle_authorized": False,
                "creates_completion_evidence_now": dependency.get("creates_completion_evidence"),
                "supported_blocker_count": candidate.get("supported_blocker_count"),
                "blocker_ids_supported": dependency.get("blocker_ids_supported", []),
                "post_approval_command_plan": dependency.get("post_approval_command_plan", []),
            }
        )
    return rows


def build_payload(
    *,
    dependency_map_path: pathlib.Path,
    next_step_selection_path: pathlib.Path,
    acceptance_boundary_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    dependency_map = load_required_yaml(dependency_map_path, violations)
    next_step_selection = load_required_yaml(next_step_selection_path, violations)
    acceptance_boundary = load_required_yaml(acceptance_boundary_path, violations)

    row_by_step: dict[str, dict[str, Any]] = {}
    candidate_by_step: dict[str, dict[str, Any]] = {}
    if dependency_map:
        row_by_step = validate_dependency_map(dependency_map, violations)
    if next_step_selection:
        candidate_by_step = validate_next_step_selection(next_step_selection, violations)
    if acceptance_boundary:
        validate_acceptance_boundary(acceptance_boundary, violations)

    rows = sequence_rows(row_by_step, candidate_by_step)
    remaining_after_phase1 = [row["step_id"] for row in rows if row["would_remain_after_phase1_only"]]
    all_steps_packet_covered = all(row.get("packet_coverage_passed") is True for row in rows)
    all_steps_preflight_ready = all(row.get("preflight_ready") is True for row in rows)
    all_steps_separate_approval_required = all(
        row.get("separate_exact_user_approval_required") is True for row in rows
    )
    any_current_approved = any(row.get("approved_evidence_created_now") is True for row in rows)
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "sequence_boundary_complete": not violations,
        "ordered_step_count": len(rows),
        "expected_step_count": len(EXPECTED_SEQUENCE),
        "first_step_id": FIRST_STEP_ID,
        "first_worksheet": FIRST_WORKSHEET,
        "approval_phrase_required": APPROVAL_PHRASE,
        "remaining_step_count_after_phase1": len(remaining_after_phase1),
        "remaining_step_ids_after_phase1": remaining_after_phase1,
        "all_steps_packet_covered": all_steps_packet_covered,
        "all_steps_preflight_ready": all_steps_preflight_ready,
        "all_steps_separate_approval_required": all_steps_separate_approval_required,
        "phase1_alone_completes_measured_geometry_chain": False,
        "phase1_alone_completes_overall_goal": False,
        "current_approved_read_only_run_count": acceptance_boundary.get("summary", {}).get(
            "approved_read_only_run_count"
        ),
        "current_phase1_approved_read_only_run_count": acceptance_boundary.get("summary", {}).get(
            "phase1_approved_read_only_run_count"
        ),
        "current_finalization_record_count": acceptance_boundary.get("summary", {}).get(
            "read_only_evidence_finalization_present_count"
        ),
        "current_approved_read_only_audit_passed_count": acceptance_boundary.get("summary", {}).get(
            "approved_read_only_audit_passed_count"
        ),
        "approved_packet_count": dependency_map.get("summary", {}).get("approved_packet_count"),
        "execution_authorizing_packet_count": dependency_map.get("summary", {}).get(
            "execution_authorizing_packet_count"
        ),
        "live_access_authorizing_packet_count": dependency_map.get("summary", {}).get(
            "live_access_authorizing_packet_count"
        ),
        "current_any_approved_step_evidence": any_current_approved,
        "bundle_approval_authorized": False,
        "approved_read_only_evidence_created": False,
        "explicit_user_approval_required": True,
        "live_access_authorized": False,
        "execution_authorized": False,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    if len(rows) != len(EXPECTED_SEQUENCE):
        summary["audit_passed"] = False
        summary["sequence_boundary_complete"] = False
    return {
        "run_source": "read-only evidence sequence boundary audit",
        "audit_run_id": run_id,
        "source_files": {
            "read_only_evidence_dependency_map": rel(dependency_map_path),
            "read_only_next_step_selection": rel(next_step_selection_path),
            "phase1_approved_evidence_acceptance_boundary": rel(acceptance_boundary_path),
        },
        "summary": summary,
        "sequence_rows": rows,
        "prompt_to_artifact_checklist": [
            {
                "requirement": "The first exact step remains phase1 mounted-stack TCP/contact measurement.",
                "evidence": rel(next_step_selection_path),
                "passed": summary["first_step_id"] == FIRST_STEP_ID
                and summary["first_worksheet"] == FIRST_WORKSHEET,
            },
            {
                "requirement": "The read-only evidence chain has five registered finalizer steps.",
                "evidence": rel(dependency_map_path),
                "passed": summary["ordered_step_count"] == len(EXPECTED_SEQUENCE),
            },
            {
                "requirement": "Four downstream evidence steps remain after phase1 only.",
                "evidence": "sequence_rows",
                "passed": summary["remaining_step_count_after_phase1"] == 4,
            },
            {
                "requirement": "Every step still requires separate exact user approval.",
                "evidence": "sequence_rows",
                "passed": summary["all_steps_separate_approval_required"] is True,
            },
            {
                "requirement": "Current repository evidence scan contains no approved evidence.",
                "evidence": rel(acceptance_boundary_path),
                "passed": summary["current_approved_read_only_run_count"] == 0
                and summary["current_approved_read_only_audit_passed_count"] == 0,
            },
        ],
        "claim_boundary": {
            "post_hoc_offline_audit_only": True,
            "sequence_boundary_only": True,
            "approval_record_created": False,
            "approved_read_only_evidence": False,
            "phase1_alone_completes_measured_geometry_chain": False,
            "phase1_alone_completes_overall_goal": False,
            "bundle_approval_authorized": False,
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
            "If phase1 is later approved and audited, keep the four remaining evidence steps separate.",
            "Do not bundle phase2-phase5 into phase1 approval.",
            "Do not use the sequence boundary as approved evidence or hardware authorization.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Read-Only Evidence Sequence Boundary Audit",
        "",
        f"Run id: `{payload['audit_run_id']}`",
        "",
        f"Audit passed: `{summary['audit_passed']}`",
        f"Sequence boundary complete: `{summary['sequence_boundary_complete']}`",
        f"Ordered step count: `{summary['ordered_step_count']}`",
        f"First step ID: `{summary['first_step_id']}`",
        f"First worksheet: `{summary['first_worksheet']}`",
        f"Remaining steps after phase1: `{summary['remaining_step_count_after_phase1']}`",
        f"All steps packet-covered: `{summary['all_steps_packet_covered']}`",
        f"All steps preflight-ready: `{summary['all_steps_preflight_ready']}`",
        f"Every step requires separate approval: `{summary['all_steps_separate_approval_required']}`",
        f"Phase1 alone completes measured geometry chain: `{summary['phase1_alone_completes_measured_geometry_chain']}`",
        f"Phase1 alone completes overall goal: `{summary['phase1_alone_completes_overall_goal']}`",
        f"Bundle approval authorized: `{summary['bundle_approval_authorized']}`",
        f"Current approved read-only runs: `{summary['current_approved_read_only_run_count']}`",
        f"Completion claim allowed: `{summary['completion_claim_allowed']}`",
        f"Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "## Sequence",
        "",
        "| Index | Step ID | Worksheet | Role | Approval required |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in payload["sequence_rows"]:
        lines.append(
            f"| {row['sequence_index']} | `{row['step_id']}` | `{row['worksheet']}` | "
            f"`{row['chain_role']}` | `{row['separate_exact_user_approval_required']}` |"
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
                "The selected phase1 step is only the first exact read-only "
                "evidence step. Four downstream registered evidence steps remain "
                "after phase1, and each still requires separate explicit approval. "
                "This audit creates no approved evidence and authorizes no live "
                "access or execution."
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
    parser.add_argument("--acceptance-boundary-path", default=DEFAULT_ACCEPTANCE_BOUNDARY)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "read_only_evidence_sequence_boundary" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        dependency_map_path=resolve(args.dependency_map_path),
        next_step_selection_path=resolve(args.next_step_selection_path),
        acceptance_boundary_path=resolve(args.acceptance_boundary_path),
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
