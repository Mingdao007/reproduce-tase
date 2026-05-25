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

DEFAULT_V145_CRITERION = "runs/user_completion_criterion_after_v144/20260525T190000/metrics.yaml"
DEFAULT_STRICT_TERMINAL = "runs/strict_terminal_constrained_optimization/20260525T085000/metrics.yaml"
DEFAULT_ROBUSTNESS_FRONTIER = (
    "runs/robustness_dependency_frontier_after_v141/20260525T160000/metrics.yaml"
)


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
        return yaml.safe_load(f) or {}


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


def require(summary: dict[str, Any], key: str, expected: Any, label: str, violations: list[str]) -> None:
    if summary.get(key) != expected:
        violations.append(f"{label}.{key} is {summary.get(key)!r}, expected {expected!r}")


def validate_v145(metrics: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    expected = {
        "audit_passed": True,
        "answer": "not_complete_not_only_real_data_missing",
        "user_completion_criterion_met": False,
        "only_real_or_explicit_approval_data_missing": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
        "offline_nonfinal_unresolved_count": 2,
        "offline_nonfinal_unresolved_ids": [
            "strict_terminal_or_full_staged_feasibility",
            "robustness_to_contact_model_perturbations",
        ],
    }
    for key, expected_value in expected.items():
        require(summary, key, expected_value, "v145.summary", violations)
    return summary


def validate_strict(metrics: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    expected = {
        "strict_terminal_pass_count": 0,
        "strict_terminal_constrained_optimization_complete": False,
        "strict_paper_equivalent_feasibility": False,
    }
    for key, expected_value in expected.items():
        require(summary, key, expected_value, "strict.summary", violations)
    if summary.get("best_max_gate_ratio", 0) <= 1.0:
        violations.append("strict.summary.best_max_gate_ratio is not above the strict pass boundary")
    return summary


def validate_robustness(metrics: dict[str, Any], violations: list[str]) -> dict[str, Any]:
    summary = metrics.get("summary", {})
    expected = {
        "audit_passed": True,
        "robustness_complete": False,
        "accepted_as_robustness_proof": False,
        "closed_cell_count": 0,
        "gate_or_contact_acceptance_blocked_count": 2,
        "new_simulation_selected": False,
        "additional_failed_cell_execution_recommended": False,
        "requires_approved_read_only_evidence_for_closure": True,
        "requires_contact_setup_target_acceptance_for_closure": True,
        "requires_orientation_gate_acceptance_for_gate_rows": True,
        "do_not_mark_goal_complete": True,
    }
    for key, expected_value in expected.items():
        require(summary, key, expected_value, "robustness.summary", violations)
    return summary


def build_payload(
    *,
    v145_criterion_path: pathlib.Path,
    strict_terminal_path: pathlib.Path,
    robustness_frontier_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    for path in [v145_criterion_path, strict_terminal_path, robustness_frontier_path]:
        if not path.exists():
            violations.append(f"missing required source file: {rel(path)}")

    v145 = load_yaml(v145_criterion_path) if v145_criterion_path.exists() else {}
    strict = load_yaml(strict_terminal_path) if strict_terminal_path.exists() else {}
    robustness = load_yaml(robustness_frontier_path) if robustness_frontier_path.exists() else {}
    v145_summary = validate_v145(v145, violations)
    strict_summary = validate_strict(strict, violations)
    robustness_summary = validate_robustness(robustness, violations)

    boundary_rows = [
        {
            "blocker_id": "strict_terminal_or_full_staged_feasibility",
            "status": "offline_unresolved_nonfinal",
            "completion_closing_offline_shortcut_known": False,
            "safe_nonrepeating_closure_action": None,
            "repeat_family_disallowed": "v113-v116 strict-policy/terminal family",
            "evidence": {
                "strict_terminal_pass_count": strict_summary.get("strict_terminal_pass_count"),
                "best_max_gate_ratio": strict_summary.get("best_max_gate_ratio"),
                "strict_paper_equivalent_feasibility": strict_summary.get(
                    "strict_paper_equivalent_feasibility"
                ),
            },
            "next_action": (
                "Continue only non-final strict-feasibility research; do not treat it "
                "as completion without a strict pass or accepted setup/contact change."
            ),
        },
        {
            "blocker_id": "robustness_to_contact_model_perturbations",
            "status": "offline_unresolved_but_closure_dependency_blocked",
            "completion_closing_offline_shortcut_known": False,
            "safe_nonrepeating_closure_action": None,
            "repeat_family_disallowed": "gate-blocked robustness cell reruns as closure evidence",
            "evidence": {
                "closed_cell_count": robustness_summary.get("closed_cell_count"),
                "accepted_as_robustness_proof": robustness_summary.get(
                    "accepted_as_robustness_proof"
                ),
                "gate_or_contact_acceptance_blocked_cell_ids": robustness_summary.get(
                    "gate_or_contact_acceptance_blocked_cell_ids"
                ),
                "additional_failed_cell_execution_recommended": robustness_summary.get(
                    "additional_failed_cell_execution_recommended"
                ),
            },
            "next_action": (
                "Keep robustness non-final until approved read-only evidence and "
                "contact/gate acceptance exist."
            ),
        },
    ]
    completion_closing_offline_shortcut_count = sum(
        1 for row in boundary_rows if row["completion_closing_offline_shortcut_known"]
    )
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
        "user_completion_criterion_met": False,
        "offline_nonfinal_unresolved_count": v145_summary.get(
            "offline_nonfinal_unresolved_count"
        ),
        "offline_nonfinal_unresolved_ids": v145_summary.get(
            "offline_nonfinal_unresolved_ids"
        ),
        "completion_closing_offline_shortcut_count": completion_closing_offline_shortcut_count,
        "completion_closing_offline_shortcut_known": completion_closing_offline_shortcut_count > 0,
        "safe_nonrepeating_completion_action_available": False,
        "live_or_approval_data_still_blocking": True,
        "exact_phase1_approval_still_required": True,
    }
    return {
        "run_source": "post-v145 offline blocker boundary audit",
        "audit_run_id": run_id,
        "source_files": {
            "v145_user_completion_criterion": rel(v145_criterion_path),
            "strict_terminal_constrained_optimization": rel(strict_terminal_path),
            "robustness_dependency_frontier": rel(robustness_frontier_path),
        },
        "summary": summary,
        "boundary_rows": boundary_rows,
        "v145_summary": v145_summary,
        "strict_summary": strict_summary,
        "robustness_summary": robustness_summary,
        "claim_boundary": {
            "post_hoc_audit_only": True,
            "new_simulation_run": False,
            "new_optimizer_run": False,
            "failed_cell_rerun": False,
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
            "Without approval, do not repeat v113-v116 or gate-blocked robustness rows as closure evidence.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Post-V145 Offline Blocker Boundary Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- User completion criterion met: `{summary['user_completion_criterion_met']}`",
        f"- Completion claim allowed: `{summary['completion_claim_allowed']}`",
        f"- Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        f"- Offline non-final unresolved: `{summary['offline_nonfinal_unresolved_count']}`",
        f"- Completion-closing offline shortcuts known: `{summary['completion_closing_offline_shortcut_count']}`",
        f"- Safe non-repeating completion action available: `{summary['safe_nonrepeating_completion_action_available']}`",
        "",
        "| blocker | status | closure shortcut known | disallowed repeat family |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["boundary_rows"]:
        lines.append(
            "| `{blocker}` | `{status}` | `{known}` | `{repeat}` |".format(
                blocker=row["blocker_id"],
                status=row["status"],
                known=row["completion_closing_offline_shortcut_known"],
                repeat=row["repeat_family_disallowed"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The current state is still not complete by the user's criterion.",
            "- No safe non-repeating offline action currently closes the two offline/non-final blockers.",
            "- This does not authorize live access or execution; exact phase1 approval remains required.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v145-criterion", default=DEFAULT_V145_CRITERION)
    parser.add_argument("--strict-terminal", default=DEFAULT_STRICT_TERMINAL)
    parser.add_argument("--robustness-frontier", default=DEFAULT_ROBUSTNESS_FRONTIER)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "post_v145_offline_blocker_boundary" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        v145_criterion_path=(ROOT / args.v145_criterion).resolve(),
        strict_terminal_path=(ROOT / args.strict_terminal).resolve(),
        robustness_frontier_path=(ROOT / args.robustness_frontier).resolve(),
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
