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

DEFAULT_COMPLETION_BLOCKERS = "runs/offline_completion_blockers/20260525T020734/metrics.yaml"
DEFAULT_STRICT_TERMINAL = "runs/strict_terminal_constrained_optimization/20260525T085000/metrics.yaml"
DEFAULT_MATRIX_RESTATEMENT = "runs/weighted_profile_matrix_restatement/20260525T075040/metrics.yaml"
DEFAULT_READ_ONLY_RUN_ROOT = "runs/read_only_calibration_measurement"
DEFAULT_READ_ONLY_AUDIT_ROOT = "runs/read_only_calibration_measurement_run_audit"
DEFAULT_ORIENTATION_REVIEW_ROOT = "runs/orientation_gate_acceptance_review"
DEFAULT_ORIENTATION_AUDIT_ROOT = "runs/orientation_gate_acceptance_review_audit"
DEFAULT_CONTACT_REVIEW_ROOT = "runs/contact_setup_target_acceptance_review"
DEFAULT_CONTACT_AUDIT_ROOT = "runs/contact_setup_target_acceptance_review_audit"


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


def nested_get(payload: dict[str, Any], path: list[str], default: Any = None) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


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


def scan_metrics(root: pathlib.Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for metrics_path in sorted(root.glob("*/metrics.yaml")):
        metrics = load_yaml(metrics_path)
        rows.append(
            {
                "run_id": metrics_path.parent.name,
                "path": rel(metrics_path),
                "metrics": metrics,
            }
        )
    return rows


def count_where(rows: list[dict[str, Any]], predicate: Any) -> int:
    return sum(1 for row in rows if predicate(row["metrics"]))


def latest_row(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    return sorted(rows, key=lambda row: row["run_id"])[-1]


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row["metrics"].get("status", row["metrics"].get("run_status", "unknown")))
        counts[status] = counts.get(status, 0) + 1
    return counts


def requirement_row(
    *,
    requirement_id: str,
    success_criteria: str,
    achieved: bool,
    evidence: dict[str, Any],
    missing: list[str],
    next_action: str,
    can_advance_offline: bool,
    requires_explicit_approval: bool,
) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "success_criteria": success_criteria,
        "achieved": bool(achieved),
        "evidence": evidence,
        "missing": list(missing),
        "can_advance_offline": bool(can_advance_offline),
        "requires_explicit_approval": bool(requires_explicit_approval),
        "next_action": next_action,
    }


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
    run_id: str,
) -> dict[str, Any]:
    completion = load_yaml(completion_blockers_path)
    strict_terminal = load_yaml(strict_terminal_path)
    matrix = load_yaml(matrix_restatement_path)

    read_only_runs = scan_metrics(read_only_run_root)
    read_only_audits = scan_metrics(read_only_audit_root)
    orientation_reviews = scan_metrics(orientation_review_root)
    orientation_audits = scan_metrics(orientation_audit_root)
    contact_reviews = scan_metrics(contact_review_root)
    contact_audits = scan_metrics(contact_audit_root)

    approved_read_only_run_count = count_where(
        read_only_runs,
        lambda metrics: metrics.get("status") == "approved_read_only_evidence"
        and nested_get(metrics, ["execution", "user_confirmed_read_only_step"]) is True,
    )
    approved_read_only_audit_passed_count = count_where(
        read_only_audits,
        lambda metrics: metrics.get("audit_mode") == "approved-read-only"
        and metrics.get("audit_passed") is True,
    )
    accepted_orientation_review_count = count_where(
        orientation_reviews,
        lambda metrics: nested_get(metrics, ["orientation_gate_acceptance", "decision"]) == "accepted",
    )
    accepted_orientation_audit_count = count_where(
        orientation_audits,
        lambda metrics: nested_get(metrics, ["orientation_gate_acceptance", "decision"]) == "accepted"
        and metrics.get("audit_passed") is True,
    )
    accepted_contact_review_count = count_where(
        contact_reviews,
        lambda metrics: nested_get(metrics, ["contact_setup_target_acceptance", "decision"]) == "accepted",
    )
    accepted_contact_audit_count = count_where(
        contact_audits,
        lambda metrics: nested_get(metrics, ["contact_setup_target_acceptance", "decision"]) == "accepted"
        and metrics.get("audit_passed") is True,
    )

    strict_terminal_pass_count = int(nested_get(strict_terminal, ["summary", "strict_terminal_pass_count"], 0))
    best_max_gate_ratio = nested_get(strict_terminal, ["summary", "best_max_gate_ratio"])
    closed_cell_count = int(nested_get(matrix, ["summary", "closed_cell_count"], 0))
    accepted_as_robustness_proof = bool(
        nested_get(matrix, ["summary", "accepted_as_robustness_proof"], False)
    )
    hardware_gate_report = ROOT / "reports" / "hardware_gate_report.md"

    checklist = [
        requirement_row(
            requirement_id="approved_read_only_calibration_evidence",
            success_criteria=(
                "At least one read-only measurement run is finalized as approved_read_only_evidence "
                "and has a passed approved-read-only audit."
            ),
            achieved=approved_read_only_run_count > 0 and approved_read_only_audit_passed_count > 0,
            evidence={
                "run_root": rel(read_only_run_root),
                "run_count": len(read_only_runs),
                "status_counts": status_counts(read_only_runs),
                "approved_read_only_run_count": approved_read_only_run_count,
                "audit_root": rel(read_only_audit_root),
                "audit_count": len(read_only_audits),
                "approved_read_only_audit_passed_count": approved_read_only_audit_passed_count,
                "latest_run": latest_row(read_only_runs)["path"] if latest_row(read_only_runs) else None,
                "latest_audit": latest_row(read_only_audits)["path"] if latest_row(read_only_audits) else None,
            },
            missing=["explicit approved read-only measurement evidence run"],
            can_advance_offline=False,
            requires_explicit_approval=True,
            next_action="Ask for explicit approval for one exact read-only SOP step before collecting rows.",
        ),
        requirement_row(
            requirement_id="contact_setup_target_acceptance",
            success_criteria=(
                "A separate contact/setup-target review accepts the contact model, setup target, "
                "TCP/contact datum, surface normal, and force source from approved read-only evidence."
            ),
            achieved=accepted_contact_review_count > 0 and accepted_contact_audit_count > 0,
            evidence={
                "review_root": rel(contact_review_root),
                "review_count": len(contact_reviews),
                "accepted_review_count": accepted_contact_review_count,
                "audit_root": rel(contact_audit_root),
                "audit_count": len(contact_audits),
                "accepted_audit_count": accepted_contact_audit_count,
                "latest_audit_passed": nested_get(
                    latest_row(contact_audits)["metrics"] if latest_row(contact_audits) else {},
                    ["audit_passed"],
                ),
                "latest_decision": nested_get(
                    latest_row(contact_audits)["metrics"] if latest_row(contact_audits) else {},
                    ["contact_setup_target_acceptance", "decision"],
                ),
            },
            missing=["accepted contact/setup-target review"],
            can_advance_offline=False,
            requires_explicit_approval=True,
            next_action="Use the v117 scaffold only after approved read-only evidence exists.",
        ),
        requirement_row(
            requirement_id="orientation_gate_acceptance",
            success_criteria=(
                "A separate orientation-gate review accepts a replacement gate from approved read-only evidence."
            ),
            achieved=accepted_orientation_review_count > 0 and accepted_orientation_audit_count > 0,
            evidence={
                "review_root": rel(orientation_review_root),
                "review_count": len(orientation_reviews),
                "accepted_review_count": accepted_orientation_review_count,
                "audit_root": rel(orientation_audit_root),
                "audit_count": len(orientation_audits),
                "accepted_audit_count": accepted_orientation_audit_count,
                "latest_decision": nested_get(
                    latest_row(orientation_audits)["metrics"] if latest_row(orientation_audits) else {},
                    ["orientation_gate_acceptance", "decision"],
                ),
            },
            missing=["accepted orientation-gate review"],
            can_advance_offline=False,
            requires_explicit_approval=True,
            next_action="Keep the gate review not accepted until evidence exists and a separate review is approved.",
        ),
        requirement_row(
            requirement_id="strict_terminal_or_full_staged_feasibility",
            success_criteria="Strict paper-equivalent setup/full staged feasibility is recovered.",
            achieved=False,
            evidence={
                "strict_terminal_path": rel(strict_terminal_path),
                "strict_terminal_pass_count": strict_terminal_pass_count,
                "best_max_gate_ratio": best_max_gate_ratio,
                "strict_paper_equivalent_feasibility": bool(
                    nested_get(strict_terminal, ["summary", "strict_paper_equivalent_feasibility"], False)
                ),
                "v95_requirement_still_incomplete": "strict_paper_equivalent_full_staged_feasibility"
                in completion.get("incomplete_requirement_ids", []),
            },
            missing=["strict terminal/setup pass count remains zero"],
            can_advance_offline=True,
            requires_explicit_approval=False,
            next_action="Continue only non-final strict-feasibility research that does not repeat v113-v116.",
        ),
        requirement_row(
            requirement_id="robustness_to_contact_model_perturbations",
            success_criteria="Robustness matrix closes all failed cells under the accepted model.",
            achieved=closed_cell_count > 0 and accepted_as_robustness_proof,
            evidence={
                "matrix_restatement_path": rel(matrix_restatement_path),
                "closed_cell_count": closed_cell_count,
                "accepted_as_robustness_proof": accepted_as_robustness_proof,
                "gate_acceptance_blocked_cell_ids": nested_get(
                    matrix, ["summary", "gate_acceptance_blocked_cell_ids"], []
                ),
                "profile_overlay_supported_cell_ids": nested_get(
                    matrix, ["summary", "profile_overlay_supported_cell_ids"], []
                ),
            },
            missing=["accepted model robustness proof"],
            can_advance_offline=True,
            requires_explicit_approval=False,
            next_action="Keep robustness as non-final until contact/gate dependencies are accepted.",
        ),
        requirement_row(
            requirement_id="hardware_readiness",
            success_criteria="Hardware gate report exists and proves measured TCP/payload/CoG, force source, logging, and low-risk SOP readiness.",
            achieved=hardware_gate_report.exists(),
            evidence={
                "hardware_gate_report": rel(hardware_gate_report),
                "exists": hardware_gate_report.exists(),
                "robot_motion_authorized": False,
                "hardware_writes_authorized": False,
                "force_control_authorized": False,
            },
            missing=["hardware gate report and approval/evidence chain"],
            can_advance_offline=False,
            requires_explicit_approval=True,
            next_action="Do not prepare motion; collect approved read-only evidence first.",
        ),
    ]

    achieved_count = sum(1 for row in checklist if row["achieved"])
    incomplete = [row["requirement_id"] for row in checklist if not row["achieved"]]
    approval_blocked = [row["requirement_id"] for row in checklist if row["requires_explicit_approval"]]
    offline_nonfinal = [
        row["requirement_id"]
        for row in checklist
        if row["can_advance_offline"] and not row["achieved"]
    ]

    completion_claim_allowed = not incomplete
    summary = {
        "overall_goal_complete": completion_claim_allowed,
        "completion_claim_allowed": completion_claim_allowed,
        "do_not_mark_goal_complete": not completion_claim_allowed,
        "achieved_requirement_count": achieved_count,
        "incomplete_requirement_count": len(incomplete),
        "incomplete_requirement_ids": incomplete,
        "approval_blocked_requirement_ids": approval_blocked,
        "offline_actionable_nonfinal_requirement_ids": offline_nonfinal,
        "top_blocker": "approved_read_only_calibration_evidence",
        "approved_read_only_run_count": approved_read_only_run_count,
        "approved_read_only_audit_passed_count": approved_read_only_audit_passed_count,
        "accepted_orientation_review_count": accepted_orientation_review_count,
        "accepted_contact_setup_target_review_count": accepted_contact_review_count,
        "strict_terminal_pass_count": strict_terminal_pass_count,
        "closed_robustness_cell_count": closed_cell_count,
        "hardware_gate_report_exists": hardware_gate_report.exists(),
    }

    return {
        "run_source": "v118 post-v117 evidence readiness audit",
        "audit_run_id": run_id,
        "source_files": {
            "completion_blockers": rel(completion_blockers_path),
            "strict_terminal_constrained_optimization": rel(strict_terminal_path),
            "weighted_profile_matrix_restatement": rel(matrix_restatement_path),
        },
        "actual_scan_roots": {
            "read_only_runs": rel(read_only_run_root),
            "read_only_audits": rel(read_only_audit_root),
            "orientation_gate_reviews": rel(orientation_review_root),
            "orientation_gate_audits": rel(orientation_audit_root),
            "contact_setup_target_reviews": rel(contact_review_root),
            "contact_setup_target_audits": rel(contact_audit_root),
        },
        "summary": summary,
        "completion_checklist": checklist,
        "claim_boundary": {
            "post_hoc_offline_audit_only": True,
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
            "Do not accept contact/setup-target or orientation-gate changes from simulation recovery alone.",
            "Avoid repeating v113-v116 policy, timing, seed, and terminal-objective families.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Post-V117 Evidence Readiness Audit",
        "",
        f"Run root: `{out_dir}`",
        "",
        "## Summary",
        "",
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
        "",
        "## Checklist",
        "",
    ]
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
            "This audit is offline bookkeeping only. It does not collect live evidence,",
            "move or configure the robot, accept a contact/setup target, accept an",
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
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "post_v117_evidence_readiness" / run_id
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
        run_id=run_id,
    )
    payload["audit_root"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
