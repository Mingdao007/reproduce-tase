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

DEFAULT_POST_V143_GATE = "runs/post_v142_completion_gate/20260525T170000/metrics.yaml"
DEFAULT_PHASE1_FRESHNESS = "runs/phase1_packet_freshness_after_v143/20260525T180000/metrics.yaml"


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


def rel(path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def write_git_state(out_dir: pathlib.Path, *, command: list[str]) -> None:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
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
        "strict_terminal_pass_count": 0,
        "closed_robustness_cell_count": 0,
        "hardware_gate_report_exists": False,
    }
    for key, expected_value in expected.items():
        if summary.get(key) != expected_value:
            violations.append(
                f"post_v143_gate.summary.{key} is {summary.get(key)!r}, expected {expected_value!r}"
            )
    return summary


def validate_phase1_freshness(metrics: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    expected = {
        "audit_passed": True,
        "phase1_packet_fresh": True,
        "registry_matches_frozen_packet": True,
        "packet_hash_unchanged": True,
        "phase1_packet_still_not_approved": True,
        "approved_read_only_run_count": 0,
        "approved_read_only_audit_passed_count": 0,
        "approval_record_created": False,
        "live_access_authorized_now": False,
        "execution_authorized_now": False,
        "approved_read_only_evidence_created": False,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    for key, expected_value in expected.items():
        if summary.get(key) != expected_value:
            violations.append(
                f"phase1_freshness.summary.{key} is {summary.get(key)!r}, expected {expected_value!r}"
            )
    return summary


def classify_incomplete_requirements(checklist: list[dict[str, Any]]) -> dict[str, Any]:
    incomplete = [row for row in checklist if row.get("achieved") is not True]
    offline_nonfinal = [row for row in incomplete if row.get("can_advance_offline") is True]
    approval_or_live = [row for row in incomplete if row.get("requires_explicit_approval") is True]
    neither = [
        row
        for row in incomplete
        if row.get("can_advance_offline") is not True
        and row.get("requires_explicit_approval") is not True
    ]
    return {
        "incomplete": incomplete,
        "offline_nonfinal": offline_nonfinal,
        "approval_or_live": approval_or_live,
        "neither": neither,
    }


def row_ids(rows: list[dict[str, Any]]) -> list[str]:
    return [str(row.get("requirement_id")) for row in rows]


def build_payload(
    *,
    post_v143_gate_path: pathlib.Path,
    phase1_freshness_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    for path in [post_v143_gate_path, phase1_freshness_path]:
        if not path.exists():
            violations.append(f"missing required source file: {rel(path)}")

    post_gate = load_yaml(post_v143_gate_path) if post_v143_gate_path.exists() else {}
    phase1 = load_yaml(phase1_freshness_path) if phase1_freshness_path.exists() else {}
    post_summary = validate_post_v143_gate(post_gate, violations)
    phase1_summary = validate_phase1_freshness(phase1, violations)
    classification = classify_incomplete_requirements(post_gate.get("completion_checklist", []))

    incomplete = classification["incomplete"]
    offline_nonfinal = classification["offline_nonfinal"]
    approval_or_live = classification["approval_or_live"]
    neither = classification["neither"]

    if post_summary.get("incomplete_requirement_count") != len(incomplete):
        violations.append(
            "post_v143 incomplete requirement count does not match completion_checklist"
        )
    if neither:
        violations.append("some incomplete requirements are neither offline nor approval/live classified")

    only_real_or_explicit_approval_data_missing = bool(incomplete) and not offline_nonfinal and len(
        approval_or_live
    ) == len(incomplete)
    user_completion_criterion_met = (
        post_summary.get("overall_goal_complete") is True
        or only_real_or_explicit_approval_data_missing
    ) and not violations

    answer = (
        "complete_by_user_real_data_only_criterion"
        if user_completion_criterion_met
        else "not_complete_not_only_real_data_missing"
    )
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "answer": answer,
        "user_completion_criterion_met": bool(user_completion_criterion_met),
        "only_real_or_explicit_approval_data_missing": bool(
            only_real_or_explicit_approval_data_missing
        ),
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
        "incomplete_requirement_count": len(incomplete),
        "incomplete_requirement_ids": row_ids(incomplete),
        "approval_or_live_data_blocked_count": len(approval_or_live),
        "approval_or_live_data_blocked_ids": row_ids(approval_or_live),
        "offline_nonfinal_unresolved_count": len(offline_nonfinal),
        "offline_nonfinal_unresolved_ids": row_ids(offline_nonfinal),
        "unclassified_incomplete_count": len(neither),
        "unclassified_incomplete_ids": row_ids(neither),
        "top_blocker": post_summary.get("top_blocker"),
        "approved_read_only_run_count": post_summary.get("approved_read_only_run_count"),
        "approved_read_only_audit_passed_count": post_summary.get(
            "approved_read_only_audit_passed_count"
        ),
        "phase1_packet_fresh": phase1_summary.get("phase1_packet_fresh"),
        "phase1_packet_still_not_approved": phase1_summary.get(
            "phase1_packet_still_not_approved"
        ),
        "live_access_authorized_now": phase1_summary.get("live_access_authorized_now"),
        "execution_authorized_now": phase1_summary.get("execution_authorized_now"),
    }

    return {
        "run_source": "user completion criterion after v144 audit",
        "audit_run_id": run_id,
        "source_files": {
            "post_v143_completion_gate": rel(post_v143_gate_path),
            "phase1_packet_freshness_after_v143": rel(phase1_freshness_path),
        },
        "summary": summary,
        "criterion": {
            "user_statement": (
                "If everything except real-machine data that Codex cannot read is done, "
                "the task may be considered complete."
            ),
            "passed_when": [
                "all incomplete requirements are explicitly approval/live-data blocked",
                "no incomplete requirement can still advance offline",
                "current metrics have no validation violations",
            ],
            "failed_because": [
                "offline_nonfinal_unresolved_count is nonzero"
            ]
            if offline_nonfinal
            else [],
        },
        "requirement_classification": {
            "offline_nonfinal_unresolved": offline_nonfinal,
            "approval_or_live_data_blocked": approval_or_live,
            "unclassified_incomplete": neither,
        },
        "post_v143_summary": post_summary,
        "phase1_freshness_summary": phase1_summary,
        "claim_boundary": {
            "post_hoc_audit_only": True,
            "live_hardware_access_authorized": False,
            "execution_authorized": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "approved_read_only_evidence": False,
            "contact_calibration_claim": False,
            "setup_target_acceptance_claim": False,
            "orientation_gate_acceptance_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "robustness_claim": False,
            "hardware_readiness": False,
            "completion_claim_allowed": False,
            "do_not_mark_goal_complete": True,
        },
        "next_actions": [
            "Do not mark the goal complete from the current repository state.",
            "Use the phase1 packet only after exact user approval for the exact registered scope.",
            "Without approval, continue only non-final offline work that does not repeat v113-v116.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# User Completion Criterion After V144 Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Answer: `{summary['answer']}`",
        f"- User completion criterion met: `{summary['user_completion_criterion_met']}`",
        f"- Only real/explicit-approval data missing: `{summary['only_real_or_explicit_approval_data_missing']}`",
        f"- Completion claim allowed: `{summary['completion_claim_allowed']}`",
        f"- Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        f"- Incomplete requirements: `{summary['incomplete_requirement_count']}`",
        f"- Approval/live-data blocked: `{summary['approval_or_live_data_blocked_count']}`",
        f"- Offline non-final unresolved: `{summary['offline_nonfinal_unresolved_count']}`",
        f"- Offline non-final IDs: `{', '.join(summary['offline_nonfinal_unresolved_ids'])}`",
        f"- Approval/live-data IDs: `{', '.join(summary['approval_or_live_data_blocked_ids'])}`",
        "",
        "Interpretation:",
        "",
        "- The current state is not complete by the user's real-data-only criterion.",
        "- The phase1 packet is fresh but still not approved, so no live access or execution is authorized.",
        "- Strict feasibility and robustness remain unresolved offline/non-final blockers.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-v143-gate", default=DEFAULT_POST_V143_GATE)
    parser.add_argument("--phase1-freshness", default=DEFAULT_PHASE1_FRESHNESS)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "user_completion_criterion_after_v144" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        post_v143_gate_path=(ROOT / args.post_v143_gate).resolve(),
        phase1_freshness_path=(ROOT / args.phase1_freshness).resolve(),
        run_id=run_id,
    )
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.dump(payload, f, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0 if payload["summary"]["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
