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
DEFAULT_POST_V138_COMPLETION_GATE = (
    "runs/post_v137_completion_gate/20260525T125000/metrics.yaml"
)
REQUIRED_INCOMPLETE_IDS = [
    "approved_read_only_calibration_evidence",
    "contact_setup_target_acceptance",
    "orientation_gate_acceptance",
    "strict_terminal_or_full_staged_feasibility",
    "robustness_to_contact_model_perturbations",
    "hardware_readiness",
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


def build_payload(*, post_v138_completion_gate_path: pathlib.Path, run_id: str) -> dict[str, Any]:
    violations: list[str] = []
    if not post_v138_completion_gate_path.exists():
        violations.append(
            f"missing post-v138 completion gate metrics: {rel(post_v138_completion_gate_path)}"
        )
        gate: dict[str, Any] = {}
    else:
        gate = load_yaml(post_v138_completion_gate_path)

    gate_summary = gate.get("summary", {})
    gate_boundary = gate.get("claim_boundary", {})
    incomplete_ids = gate_summary.get("incomplete_requirement_ids", [])
    missing_required_ids = [
        requirement_id for requirement_id in REQUIRED_INCOMPLETE_IDS if requirement_id not in incomplete_ids
    ]
    unexpected_complete = bool(gate_summary.get("overall_goal_complete"))
    unexpected_completion_claim = bool(gate_summary.get("completion_claim_allowed"))

    expected_summary = {
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
        "readiness_artifacts_are_non_evidence": True,
        "finalization_rehearsal_is_non_evidence": True,
        "margin_separation_is_non_evidence": True,
    }
    for key, expected_value in expected_summary.items():
        if gate_summary.get(key) != expected_value:
            violations.append(
                f"post_v138_completion_gate.summary.{key} is "
                f"{gate_summary.get(key)!r}, expected {expected_value!r}"
            )
    if missing_required_ids:
        violations.append(f"post_v138 completion gate missing incomplete IDs: {missing_required_ids}")
    if gate_boundary.get("robot_motion_authorized") is not False:
        violations.append("post_v138 completion gate authorizes robot motion")
    if gate_boundary.get("hardware_writes_authorized") is not False:
        violations.append("post_v138 completion gate authorizes hardware writes")
    if gate_boundary.get("force_control_authorized") is not False:
        violations.append("post_v138 completion gate authorizes force control")

    full_reproduction_complete = (
        gate_summary.get("overall_goal_complete") is True
        and gate_summary.get("completion_claim_allowed") is True
        and not missing_required_ids
        and not violations
    )
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "user_question_answer": "not_fully_reproduced" if not full_reproduction_complete else "complete",
        "full_reproduction_complete": full_reproduction_complete,
        "continue_required": not full_reproduction_complete,
        "safe_continuation_mode": (
            "explicit_read_only_approval_or_nonfinal_offline"
            if not full_reproduction_complete
            else "none"
        ),
        "source_completion_gate_audit_passed": gate_summary.get("audit_passed"),
        "source_overall_goal_complete": gate_summary.get("overall_goal_complete"),
        "source_completion_claim_allowed": gate_summary.get("completion_claim_allowed"),
        "source_do_not_mark_goal_complete": gate_summary.get("do_not_mark_goal_complete"),
        "top_blocker": gate_summary.get("top_blocker"),
        "incomplete_requirement_count": gate_summary.get("incomplete_requirement_count"),
        "incomplete_requirement_ids": incomplete_ids,
        "required_incomplete_ids_present": not missing_required_ids,
        "missing_required_incomplete_ids": missing_required_ids,
        "approved_read_only_run_count": gate_summary.get("approved_read_only_run_count"),
        "approved_read_only_audit_passed_count": gate_summary.get(
            "approved_read_only_audit_passed_count"
        ),
        "accepted_orientation_review_count": gate_summary.get(
            "accepted_orientation_review_count"
        ),
        "accepted_contact_setup_target_review_count": gate_summary.get(
            "accepted_contact_setup_target_review_count"
        ),
        "strict_terminal_pass_count": gate_summary.get("strict_terminal_pass_count"),
        "closed_robustness_cell_count": gate_summary.get("closed_robustness_cell_count"),
        "hardware_gate_report_exists": gate_summary.get("hardware_gate_report_exists"),
        "readiness_artifact_count": gate_summary.get("readiness_artifact_count"),
        "readiness_completion_evidence_ids": gate_summary.get(
            "readiness_completion_evidence_ids"
        ),
        "readiness_artifacts_are_non_evidence": gate_summary.get(
            "readiness_artifacts_are_non_evidence"
        ),
        "margin_separation_is_non_evidence": gate_summary.get(
            "margin_separation_is_non_evidence"
        ),
        "unexpected_complete_source": unexpected_complete,
        "unexpected_completion_claim_source": unexpected_completion_claim,
        "do_not_mark_goal_complete": not full_reproduction_complete,
    }
    return {
        "run_source": "full reproduction status after v138 audit",
        "audit_run_id": run_id,
        "source_files": {
            "post_v138_completion_gate": rel(post_v138_completion_gate_path),
        },
        "summary": summary,
        "prompt_to_artifact_checklist": [
            {
                "prompt_requirement": "Answer whether the reproduction is fully complete.",
                "evidence": "post-v138 completion gate overall/completion flags",
                "status": "not_complete" if not full_reproduction_complete else "complete",
            },
            {
                "prompt_requirement": "If it is not complete, continue safely.",
                "evidence": "safe_continuation_mode and missing requirement IDs",
                "status": "continue_offline_or_after_explicit_read_only_approval",
            },
            {
                "prompt_requirement": "Do not overclaim partial artifacts as completion.",
                "evidence": "readiness_completion_evidence_ids and claim boundary flags",
                "status": "guarded" if not violations else "violated",
            },
        ],
        "claim_boundary": {
            "status_answer_only": True,
            "post_hoc_existing_metrics_only": True,
            "new_simulation_run": False,
            "live_hardware_access": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "full_reproduction_claim_allowed": full_reproduction_complete,
            "strict_paper_equivalent_feasibility": False,
            "ur10e_hardware_readiness": False,
            "do_not_mark_goal_complete": not full_reproduction_complete,
        },
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Full Reproduction Status After V138",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- User question answer: `{summary['user_question_answer']}`",
        f"- Full reproduction complete: `{summary['full_reproduction_complete']}`",
        f"- Continue required: `{summary['continue_required']}`",
        f"- Safe continuation mode: `{summary['safe_continuation_mode']}`",
        f"- Top blocker: `{summary['top_blocker']}`",
        f"- Incomplete requirement count: `{summary['incomplete_requirement_count']}`",
        f"- Approved read-only runs: `{summary['approved_read_only_run_count']}`",
        f"- Passed approved-read-only audits: `{summary['approved_read_only_audit_passed_count']}`",
        f"- Strict terminal pass count: `{summary['strict_terminal_pass_count']}`",
        f"- Closed robustness cells: `{summary['closed_robustness_cell_count']}`",
        f"- Hardware gate report exists: `{summary['hardware_gate_report_exists']}`",
        f"- Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "## Missing Requirements",
        "",
    ]
    lines.extend(f"- `{requirement_id}`" for requirement_id in summary["incomplete_requirement_ids"])
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The current evidence does not support a full reproduction claim. The",
            "safe continuation path is either explicit approval for one exact",
            "read-only SOP step or non-final offline work that preserves the",
            "existing claim boundary.",
            "",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-v138-completion-gate-path", default=DEFAULT_POST_V138_COMPLETION_GATE)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "full_reproduction_status_after_v138" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        post_v138_completion_gate_path=resolve(args.post_v138_completion_gate_path),
        run_id=run_id,
    )
    payload["audit_root"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[str(pathlib.Path(sys.argv[0]).resolve()), *sys.argv[1:]])
    print(out_dir)
    return 0 if payload["summary"]["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
