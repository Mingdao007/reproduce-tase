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

RELAXED_SETUP_METRICS = ROOT / "runs" / "relaxed_setup_budget_eval" / "20260524T111859" / "metrics.yaml"
STRICT_STAGED_SUMMARY = (
    ROOT / "runs" / "staged_orientation_e1e4_posture_regularized" / "20260524T102747" / "summary.yaml"
)
ROBUSTNESS_METRICS = (
    ROOT / "runs" / "stitched_stage_a_handoff_sensitivity" / "20260524T161111" / "metrics.yaml"
)
MEASURED_GEOMETRY_METRICS = (
    ROOT / "runs" / "measured_geometry_readiness" / "20260525T000739" / "metrics.yaml"
)
READ_ONLY_RUN_ROOT = ROOT / "runs" / "read_only_calibration_measurement"
GATE_REVIEW_ROOT = ROOT / "runs" / "orientation_gate_acceptance_review"
HARDWARE_GATE_REPORT = ROOT / "reports" / "hardware_gate_report.md"


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)


def nested_get(payload: dict[str, Any], keys: list[str], default: Any = None) -> Any:
    cursor: Any = payload
    for key in keys:
        if not isinstance(cursor, dict) or key not in cursor:
            return default
        cursor = cursor[key]
    return cursor


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


def relative(path: pathlib.Path) -> str:
    return str(path.relative_to(ROOT))


def discover_read_only_runs() -> list[dict[str, Any]]:
    discovered: list[dict[str, Any]] = []
    if not READ_ONLY_RUN_ROOT.exists():
        return discovered
    for metrics_path in sorted(READ_ONLY_RUN_ROOT.glob("*/metrics.yaml")):
        metrics = load_yaml(metrics_path)
        discovered.append(
            {
                "run_id": metrics.get("run_id"),
                "path": relative(metrics_path.parent),
                "status": metrics.get("status"),
                "user_confirmed_read_only_step": nested_get(
                    metrics, ["execution", "user_confirmed_read_only_step"]
                ),
                "live_hardware_accessed": nested_get(metrics, ["execution", "live_hardware_accessed"]),
                "evidence_status": metrics.get("evidence_status", {}),
                "orientation_gate_decision": nested_get(
                    metrics, ["orientation_gate_acceptance", "decision"]
                ),
                "hardware_readiness": nested_get(metrics, ["claim_boundary", "hardware_readiness"]),
            }
        )
    return discovered


def discover_gate_reviews() -> list[dict[str, Any]]:
    discovered: list[dict[str, Any]] = []
    if not GATE_REVIEW_ROOT.exists():
        return discovered
    for metrics_path in sorted(GATE_REVIEW_ROOT.glob("*/metrics.yaml")):
        metrics = load_yaml(metrics_path)
        discovered.append(
            {
                "review_id": metrics.get("review_id"),
                "path": relative(metrics_path.parent),
                "status": metrics.get("status"),
                "source_read_only_run": nested_get(metrics, ["source_evidence", "source_read_only_run"]),
                "approved_read_only_audit_passed": nested_get(
                    metrics, ["source_evidence", "approved_read_only_audit_passed"]
                ),
                "decision": nested_get(metrics, ["orientation_gate_acceptance", "decision"]),
                "supports_gate_relaxation": nested_get(
                    metrics, ["verdict", "supports_gate_relaxation"]
                ),
                "hardware_readiness": nested_get(metrics, ["claim_boundary", "hardware_readiness"]),
            }
        )
    return discovered


def requirement(
    *,
    requirement_id: str,
    success_criteria: str,
    achieved: bool,
    evidence: list[dict[str, Any]],
    blocked_by: list[str],
    can_advance_offline: bool,
    next_action: str,
) -> dict[str, Any]:
    return {
        "id": requirement_id,
        "success_criteria": success_criteria,
        "achieved": achieved,
        "evidence": evidence,
        "blocked_by": blocked_by,
        "can_advance_offline": can_advance_offline,
        "next_action": next_action,
    }


def build_audit() -> dict[str, Any]:
    relaxed = load_yaml(RELAXED_SETUP_METRICS)
    strict = load_yaml(STRICT_STAGED_SUMMARY)
    robustness = load_yaml(ROBUSTNESS_METRICS)
    geometry = load_yaml(MEASURED_GEOMETRY_METRICS)
    read_only_runs = discover_read_only_runs()
    gate_reviews = discover_gate_reviews()

    approved_read_only_runs = [
        run for run in read_only_runs if run["status"] == "approved_read_only_evidence"
    ]
    accepted_gate_reviews = [
        review for review in gate_reviews if review["decision"] == "accepted"
    ]
    readiness_checks = {
        check["name"]: check for check in geometry.get("readiness_checks", [])
    }

    strict_pass_count = strict.get("full_staged_feasibility_pass_count")
    strict_case_count = strict.get("case_count")
    adapted_pass_count = relaxed.get("ur10e_adapted_trajectory_after_relaxed_setup_pass_count")
    adapted_case_count = relaxed.get("case_count")
    robustness_aggregate = robustness.get("aggregate", {})

    requirements = [
        requirement(
            requirement_id="ur10e_adapted_relaxed_simulation",
            success_criteria="Slowed UR10e adapted E1-E4 trajectory-after-relaxed-setup matrix passes 4 / 4.",
            achieved=adapted_pass_count == adapted_case_count == 4,
            evidence=[
                {
                    "path": relative(RELAXED_SETUP_METRICS),
                    "ur10e_adapted_trajectory_after_relaxed_setup_pass_count": adapted_pass_count,
                    "case_count": adapted_case_count,
                    "strict_full_staged_feasibility_pass_count": relaxed.get(
                        "strict_full_staged_feasibility_pass_count"
                    ),
                }
            ],
            blocked_by=[],
            can_advance_offline=False,
            next_action="Preserve as scoped simulation evidence only; do not upgrade claim scope.",
        ),
        requirement(
            requirement_id="strict_paper_equivalent_full_staged_feasibility",
            success_criteria="Strict full staged feasibility passes every E1-E4 row under the paper-equivalent gate.",
            achieved=strict_pass_count == strict_case_count and strict_case_count is not None,
            evidence=[
                {
                    "path": relative(STRICT_STAGED_SUMMARY),
                    "full_staged_feasibility_pass_count": strict_pass_count,
                    "case_count": strict_case_count,
                }
            ],
            blocked_by=["strict_setup_gate_failure", "paper_platform_parity_split_claim"],
            can_advance_offline=True,
            next_action=(
                "Continue simulation or paper-platform parity work offline, but do not claim completion "
                "until strict rows pass under the target claim definition."
            ),
        ),
        requirement(
            requirement_id="approved_read_only_calibration_evidence",
            success_criteria="At least one read-only calibration measurement run is finalized as approved_read_only_evidence.",
            achieved=bool(approved_read_only_runs),
            evidence=[
                {
                    "run_count": len(read_only_runs),
                    "approved_read_only_run_count": len(approved_read_only_runs),
                    "runs": read_only_runs,
                }
            ],
            blocked_by=["explicit_user_read_only_approval_missing"],
            can_advance_offline=False,
            next_action=(
                "Wait for explicit approval for a specific read-only SOP step; then collect worksheet rows, "
                "finalize, and audit with approved-read-only mode."
            ),
        ),
        requirement(
            requirement_id="calibrated_contact_geometry",
            success_criteria=(
                "Mounted TCP/contact point, KSM contact patch, plane normal, and force-source/frame evidence "
                "are measured or reconciled tightly enough for the v85 margin."
            ),
            achieved=all(
                readiness_checks.get(name, {}).get("constrains_v85_margin") is True
                for name in [
                    "mounted_stack_tcp_contact_point",
                    "contact_patch_convention",
                    "plane_contact_normal",
                    "force_source_frame",
                ]
            ),
            evidence=[
                {
                    "path": relative(MEASURED_GEOMETRY_METRICS),
                    "checks": {
                        name: {
                            "status": readiness_checks.get(name, {}).get("status"),
                            "has_measured_record": readiness_checks.get(name, {}).get(
                                "has_measured_record"
                            ),
                            "constrains_v85_margin": readiness_checks.get(name, {}).get(
                                "constrains_v85_margin"
                            ),
                        }
                        for name in [
                            "mounted_stack_tcp_contact_point",
                            "contact_patch_convention",
                            "plane_contact_normal",
                            "force_source_frame",
                        ]
                    },
                }
            ],
            blocked_by=["approved_read_only_calibration_evidence_missing"],
            can_advance_offline=False,
            next_action=(
                "Collect the v87/v93 read-only measurement worksheets after explicit user approval."
            ),
        ),
        requirement(
            requirement_id="orientation_gate_acceptance",
            success_criteria="A separate gate-acceptance review accepts a replacement gate from passed approved-read-only evidence.",
            achieved=bool(accepted_gate_reviews),
            evidence=[
                {
                    "review_count": len(gate_reviews),
                    "accepted_review_count": len(accepted_gate_reviews),
                    "reviews": gate_reviews,
                }
            ],
            blocked_by=["approved_read_only_calibration_evidence_missing", "separate_gate_review_not_authorized"],
            can_advance_offline=False,
            next_action=(
                "Keep gate acceptance review unused until approved-read-only evidence exists and a separate review is authorized."
            ),
        ),
        requirement(
            requirement_id="robustness_to_contact_model_perturbations",
            success_criteria="Robustness/stress matrix passes all declared perturbation cases under the accepted claim model.",
            achieved=robustness_aggregate.get("all_cases_passed") is True,
            evidence=[
                {
                    "path": relative(ROBUSTNESS_METRICS),
                    "stitched_pass_count": robustness_aggregate.get("stitched_pass_count"),
                    "case_count": robustness_aggregate.get("case_count"),
                    "all_cases_passed": robustness_aggregate.get("all_cases_passed"),
                    "failing_cases": robustness_aggregate.get("failing_cases"),
                }
            ],
            blocked_by=["current_stress_failures", "calibrated_contact_geometry_missing"],
            can_advance_offline=True,
            next_action=(
                "Additional simulation stress tests can continue offline, but final robustness remains blocked "
                "until the contact/gate model is calibrated."
            ),
        ),
        requirement(
            requirement_id="hardware_readiness",
            success_criteria="Hardware gate report exists and proves measured TCP/payload/CoG, force source, logging readiness, and low-risk SOP.",
            achieved=HARDWARE_GATE_REPORT.exists(),
            evidence=[
                {
                    "path": relative(HARDWARE_GATE_REPORT),
                    "exists": HARDWARE_GATE_REPORT.exists(),
                    "latest_read_only_runs_have_hardware_readiness": [
                        run for run in read_only_runs if run.get("hardware_readiness") is True
                    ],
                    "latest_gate_reviews_have_hardware_readiness": [
                        review for review in gate_reviews if review.get("hardware_readiness") is True
                    ],
                }
            ],
            blocked_by=[
                "approved_read_only_calibration_evidence_missing",
                "force_source_frame_unresolved",
                "hardware_gate_report_missing",
            ],
            can_advance_offline=False,
            next_action=(
                "Do not prepare robot motion; collect/read-only evidence first and keep hardware readiness false."
            ),
        ),
    ]

    incomplete = [item for item in requirements if not item["achieved"]]
    offline_actionable = [
        item["id"] for item in incomplete if item["can_advance_offline"]
    ]
    live_or_approval_blocked = [
        item["id"] for item in incomplete if not item["can_advance_offline"]
    ]
    return {
        "audit_source": "v95 offline completion blockers",
        "overall_goal_complete": not incomplete,
        "completion_blocked": bool(incomplete),
        "incomplete_requirement_ids": [item["id"] for item in incomplete],
        "offline_actionable_nonfinal_requirement_ids": offline_actionable,
        "live_or_explicit_approval_blocked_requirement_ids": live_or_approval_blocked,
        "requirements": requirements,
        "claim_boundary": {
            "do_not_mark_goal_complete": bool(incomplete),
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "hardware_readiness_claim": False,
        },
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Offline Completion Blockers Audit",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Overall goal complete: `{payload['overall_goal_complete']}`",
        f"- Completion blocked: `{payload['completion_blocked']}`",
        f"- Incomplete requirements: `{payload['incomplete_requirement_ids']}`",
        f"- Offline-actionable non-final items: `{payload['offline_actionable_nonfinal_requirement_ids']}`",
        f"- Live or explicit-approval blocked items: `{payload['live_or_explicit_approval_blocked_requirement_ids']}`",
        "",
        "## Requirements",
        "",
    ]
    for item in payload["requirements"]:
        lines.extend(
            [
                f"### {item['id']}",
                "",
                f"- Achieved: `{item['achieved']}`",
                f"- Can advance offline: `{item['can_advance_offline']}`",
                f"- Blocked by: `{item['blocked_by']}`",
                f"- Next action: {item['next_action']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "- No robot motion, hardware write, zeroing, force control, or hardware",
            "  readiness claim is authorized by this audit.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "offline_completion_blockers" / run_id
    )
    if out_dir.exists():
        raise FileExistsError(out_dir)
    out_dir.mkdir(parents=True)

    payload = build_audit()
    payload["audit_run_id"] = run_id
    payload["audit_root"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
