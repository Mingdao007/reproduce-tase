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
APPROVAL_PHRASE = "I approve this read-only measurement step"


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


def by_key(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {str(row.get(key)): row for row in rows if row.get(key) is not None}


def int_value(mapping: dict[str, Any], key: str) -> int:
    return int(mapping.get(key) or 0)


def blocker_priority_map(dependency_map: dict[str, Any]) -> dict[str, int]:
    priorities: dict[str, int] = {}
    for row in dependency_map.get("blocker_dependency_rows", []):
        blocker_id = row.get("blocker_id")
        priority = row.get("source_priority_rank")
        if blocker_id is not None and priority is not None:
            priorities[str(blocker_id)] = int(priority)
    return priorities


def priority_score(blocker_ids: list[str], priorities: dict[str, int]) -> float:
    score = 0.0
    for blocker_id in blocker_ids:
        if blocker_id in priorities:
            score += 1.0 / float(priorities[blocker_id] + 1)
    return score


def build_candidate_rows(
    dependency_map: dict[str, Any],
    *,
    violations: list[str],
) -> list[dict[str, Any]]:
    priorities = blocker_priority_map(dependency_map)
    candidates: list[dict[str, Any]] = []
    for order, row in enumerate(dependency_map.get("step_dependency_rows", []), start=1):
        step_id = row.get("step_id")
        blockers = list(row.get("blocker_ids_supported", []))
        if row.get("packet_coverage_passed") is not True:
            violations.append(f"candidate lacks packet coverage: {step_id}")
        if row.get("preflight_ready") is not True:
            violations.append(f"candidate lacks preflight readiness: {step_id}")
        if row.get("approval_required") is not True:
            violations.append(f"candidate no longer requires approval: {step_id}")
        if row.get("live_authorized_now") is not False:
            violations.append(f"candidate now authorizes live access: {step_id}")
        if row.get("execution_authorized_now") is not False:
            violations.append(f"candidate now authorizes execution: {step_id}")
        if row.get("creates_completion_evidence") is not False:
            violations.append(f"candidate now creates completion evidence: {step_id}")
        candidates.append(
            {
                "sequence_index": order,
                "step_id": step_id,
                "readiness_check": row.get("readiness_check"),
                "title": row.get("title"),
                "worksheet": row.get("worksheet"),
                "packet_coverage_passed": row.get("packet_coverage_passed"),
                "preflight_ready": row.get("preflight_ready"),
                "valid_not_approved_packet_count": row.get("valid_not_approved_packet_count"),
                "supported_blocker_count": len(blockers),
                "priority_score": priority_score(blockers, priorities),
                "blocker_ids_supported": blockers,
                "post_approval_command_plan": row.get("post_approval_command_plan", []),
                "approval_phrase_required": APPROVAL_PHRASE,
                "exact_step_id_required": True,
                "approval_record_exists_now": False,
                "live_access_authorized_now": False,
                "execution_authorized_now": False,
                "approved_evidence_created_now": False,
                "selection_authorizes_execution": False,
            }
        )
    return candidates


def best_first_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda row: (
            -int(row["supported_blocker_count"]),
            -float(row["priority_score"]),
            int(row["sequence_index"]),
        ),
    )[0]


def build_frontier_rows(
    *,
    candidates: list[dict[str, Any]],
    dependency_map: dict[str, Any],
) -> list[dict[str, Any]]:
    blocker_rows = dependency_map.get("blocker_dependency_rows", [])
    covered_before: set[str] = set()
    selected: list[str] = []
    frontier_rows: list[dict[str, Any]] = []
    for candidate in candidates:
        selected.append(candidate["step_id"])
        selected_set = set(selected)
        newly_coverable: list[str] = []
        all_coverable: list[str] = []
        for blocker in blocker_rows:
            blocker_id = blocker.get("blocker_id")
            required = set(blocker.get("required_step_ids", []))
            if blocker_id and required and required.issubset(selected_set):
                all_coverable.append(blocker_id)
                if blocker_id not in covered_before:
                    newly_coverable.append(blocker_id)
        covered_before.update(all_coverable)
        frontier_rows.append(
            {
                "after_sequence_index": candidate["sequence_index"],
                "after_step_id": candidate["step_id"],
                "selected_step_ids": list(selected),
                "dependency_only_newly_coverable_blockers": newly_coverable,
                "dependency_only_all_coverable_blockers": all_coverable,
                "approved_evidence_exists": False,
                "completion_claim_allowed": False,
            }
        )
    return frontier_rows


def validate_dependency_map(dependency_map: dict[str, Any], violations: list[str]) -> None:
    summary = dependency_map.get("summary", {})
    if summary.get("audit_passed") is not True:
        violations.append("v127 dependency-map source is not passed")
    if summary.get("dependency_map_complete") is not True:
        violations.append("v127 dependency-map source is not complete")
    if int_value(summary, "approved_packet_count") != 0:
        violations.append("v127 dependency-map source contains approved packets")
    if int_value(summary, "execution_authorizing_packet_count") != 0:
        violations.append("v127 dependency-map source contains execution-authorizing packets")
    if int_value(summary, "live_access_authorizing_packet_count") != 0:
        violations.append("v127 dependency-map source contains live-access-authorizing packets")
    if summary.get("approved_read_only_evidence_created") is not False:
        violations.append("v127 dependency-map source claims approved read-only evidence")
    if summary.get("explicit_user_approval_required") is not True:
        violations.append("v127 dependency-map source no longer requires explicit approval")
    if summary.get("live_access_authorized") is not False:
        violations.append("v127 dependency-map source authorizes live access")
    if summary.get("execution_authorized") is not False:
        violations.append("v127 dependency-map source authorizes execution")
    if summary.get("overall_goal_complete") is not False:
        violations.append("v127 dependency-map source now marks goal complete")
    if summary.get("completion_claim_allowed") is not False:
        violations.append("v127 dependency-map source now allows completion claim")
    if summary.get("do_not_mark_goal_complete") is not True:
        violations.append("v127 dependency-map source no longer blocks goal completion")

    guardrails = dependency_map.get("source_guardrails", {})
    if guardrails.get("registry_approval_phrase") != APPROVAL_PHRASE:
        violations.append("registry approval phrase drifted from expected exact phrase")
    if guardrails.get("remaining_top_priority_blocker_id") != "approved_read_only_calibration_evidence":
        violations.append("top remaining blocker is no longer approved read-only calibration evidence")
    if guardrails.get("remaining_overall_goal_complete") is not False:
        violations.append("remaining-blocker guardrail now marks goal complete")
    if guardrails.get("v126_relaxation_budget_acceptance_allowed") is not False:
        violations.append("v126 relaxation-budget guardrail now accepts relaxation")
    if guardrails.get("preflight_authorizes_execution") is not False:
        violations.append("preflight guardrail now authorizes execution")
    if guardrails.get("preflight_authorizes_live_access") is not False:
        violations.append("preflight guardrail now authorizes live access")
    if guardrails.get("approved_read_only_evidence_created") is not False:
        violations.append("preflight guardrail now claims approved evidence")

    boundary = dependency_map.get("claim_boundary", {})
    for key in [
        "approved_read_only_evidence",
        "contact_calibration_claim",
        "setup_target_acceptance_claim",
        "gate_relaxation_claim",
        "strict_terminal_relaxation_accepted",
        "strict_paper_equivalent_feasibility",
        "robustness_claim",
        "hardware_readiness",
        "live_hardware_access_authorized",
        "execution_authorized",
        "robot_motion_authorized",
        "hardware_writes_authorized",
        "force_control_authorized",
    ]:
        if boundary.get(key) is not False:
            violations.append(f"v127 claim boundary drifted true: {key}")


def build_payload(
    *,
    dependency_map_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    if not dependency_map_path.exists():
        violations.append(f"missing required source file: {rel(dependency_map_path)}")
    dependency_map = load_yaml(dependency_map_path) if dependency_map_path.exists() else {}

    validate_dependency_map(dependency_map, violations)
    candidates = build_candidate_rows(dependency_map, violations=violations)
    sequence_step_ids = [row["step_id"] for row in candidates]
    first_candidate = best_first_candidate(candidates)
    frontier_rows = build_frontier_rows(candidates=candidates, dependency_map=dependency_map)

    expected_first = "phase1_mounted_stack_tcp_contact_measurement"
    if first_candidate and first_candidate.get("step_id") != expected_first:
        violations.append(
            f"first candidate drifted from {expected_first} to {first_candidate.get('step_id')}"
        )
    if not first_candidate:
        violations.append("no read-only step candidates are available")

    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "selection_plan_complete": bool(candidates) and not violations,
        "candidate_step_count": len(candidates),
        "recommended_sequence_step_ids": sequence_step_ids,
        "first_candidate_step_id": first_candidate.get("step_id") if first_candidate else None,
        "first_candidate_worksheet": first_candidate.get("worksheet") if first_candidate else None,
        "approval_phrase_required": APPROVAL_PHRASE,
        "exact_step_id_required": True,
        "approved_packet_count": int_value(dependency_map.get("summary", {}), "approved_packet_count"),
        "execution_authorizing_packet_count": int_value(
            dependency_map.get("summary", {}), "execution_authorizing_packet_count"
        ),
        "live_access_authorizing_packet_count": int_value(
            dependency_map.get("summary", {}), "live_access_authorizing_packet_count"
        ),
        "approved_read_only_evidence_created": dependency_map.get("summary", {}).get(
            "approved_read_only_evidence_created"
        ),
        "explicit_user_approval_required": True,
        "selection_authorizes_live_access": False,
        "selection_authorizes_execution": False,
        "selection_creates_approved_evidence": False,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }

    return {
        "run_source": "read-only next-step selection audit",
        "audit_run_id": run_id,
        "source_files": {
            "read_only_evidence_dependency_map": rel(dependency_map_path),
        },
        "summary": summary,
        "candidate_rows": candidates,
        "first_candidate": first_candidate,
        "dependency_frontier_rows": frontier_rows,
        "approval_boundary": {
            "approval_phrase_required": APPROVAL_PHRASE,
            "exact_step_id_required": True,
            "first_step_id_to_name_if_user_approves": (
                first_candidate.get("step_id") if first_candidate else None
            ),
            "first_worksheet_scope": first_candidate.get("worksheet") if first_candidate else None,
            "approval_record_exists_now": False,
            "packet_status_required_before_execution": "audited_not_approved_until_user_explicitly_approves",
            "post_approval_must_use_scaffold_finalizer_and_approved_read_only_audit": True,
        },
        "claim_boundary": {
            "selection_audit_only": True,
            "readiness_artifacts_are_non_evidence": True,
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
    first = payload["first_candidate"] or {}
    lines = [
        "# Read-Only Next-Step Selection Audit",
        "",
        f"Run id: `{payload['audit_run_id']}`",
        "",
        f"Audit passed: `{summary['audit_passed']}`",
        f"Selection plan complete: `{summary['selection_plan_complete']}`",
        f"Candidate step count: `{summary['candidate_step_count']}`",
        f"First candidate step: `{summary['first_candidate_step_id']}`",
        f"First candidate worksheet: `{summary['first_candidate_worksheet']}`",
        f"Approval phrase required: `{summary['approval_phrase_required']}`",
        f"Exact step ID required: `{summary['exact_step_id_required']}`",
        f"Approved packets: `{summary['approved_packet_count']}`",
        f"Execution-authorizing packets: `{summary['execution_authorizing_packet_count']}`",
        f"Live-access-authorizing packets: `{summary['live_access_authorizing_packet_count']}`",
        f"Approved read-only evidence created: `{summary['approved_read_only_evidence_created']}`",
        f"Selection authorizes execution: `{summary['selection_authorizes_execution']}`",
        f"Completion claim allowed: `{summary['completion_claim_allowed']}`",
        f"Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "Recommended registry-order sequence:",
        "",
    ]
    for candidate in payload["candidate_rows"]:
        lines.append(
            f"{candidate['sequence_index']}. `{candidate['step_id']}` "
            f"(`{candidate['worksheet']}`)"
        )
    lines.extend(
        [
            "",
            "First candidate command path after future explicit approval:",
            "",
        ]
    )
    for command in first.get("post_approval_command_plan", []):
        lines.append(f"- {command}")
    lines.extend(["", "Dependency frontiers:", ""])
    for row in payload["dependency_frontier_rows"]:
        lines.append(
            f"- After `{row['after_step_id']}`: newly dependency-coverable blockers "
            f"`{row['dependency_only_newly_coverable_blockers']}`"
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
                "The first approval-ready candidate is the phase1 mounted-stack "
                "TCP/contact measurement step because it is packet-covered, "
                "preflight-ready, supports the maximum blocker set, and appears first "
                "in the registered step order. This selection is not approval and "
                "does not authorize live access or execution."
            ),
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--dependency-map-path", default=DEFAULT_DEPENDENCY_MAP)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "read_only_next_step_selection" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(
        dependency_map_path=resolve(args.dependency_map_path),
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
