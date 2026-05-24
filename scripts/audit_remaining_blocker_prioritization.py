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
DEFAULT_STRICT_BLOCKERS = "runs/strict_feasibility_blockers/20260525T051640/metrics.yaml"
DEFAULT_ROBUSTNESS_BLOCKERS = "runs/robustness_blockers/20260525T052457/metrics.yaml"
DEFAULT_MATRIX_RESTATEMENT = "runs/weighted_profile_matrix_restatement/20260525T075040/metrics.yaml"
DEFAULT_MEASURED_GEOMETRY = "runs/measured_geometry_readiness/20260525T000739/metrics.yaml"
DEFAULT_READ_ONLY_AUDIT = "runs/read_only_calibration_measurement_run_audit/20260525T015401/metrics.yaml"
DEFAULT_GATE_REVIEW_AUDIT = "runs/orientation_gate_acceptance_review_audit/20260525T020055/metrics.yaml"


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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


def requirement_by_id(completion: dict[str, Any], requirement_id: str) -> dict[str, Any]:
    for requirement in completion["requirements"]:
        if requirement["id"] == requirement_id:
            return requirement
    raise KeyError(requirement_id)


def blocker_row(
    *,
    blocker_id: str,
    title: str,
    priority_rank: int,
    category: str,
    status: str,
    can_advance_offline: bool,
    requires_explicit_approval: bool,
    evidence_summary: dict[str, Any],
    blockers: list[str],
    next_action: str,
) -> dict[str, Any]:
    return {
        "blocker_id": blocker_id,
        "title": title,
        "priority_rank": int(priority_rank),
        "category": category,
        "status": status,
        "can_advance_offline": bool(can_advance_offline),
        "requires_explicit_approval": bool(requires_explicit_approval),
        "evidence_summary": evidence_summary,
        "blockers": list(blockers),
        "next_action": next_action,
        "completion_claim_allowed": False,
    }


def build_priority_rows(
    *,
    completion: dict[str, Any],
    strict: dict[str, Any],
    robustness: dict[str, Any],
    matrix: dict[str, Any],
    geometry: dict[str, Any],
    read_only: dict[str, Any],
    gate_review: dict[str, Any],
) -> list[dict[str, Any]]:
    read_only_req = requirement_by_id(completion, "approved_read_only_calibration_evidence")
    contact_req = requirement_by_id(completion, "calibrated_contact_geometry")
    gate_req = requirement_by_id(completion, "orientation_gate_acceptance")
    strict_req = requirement_by_id(completion, "strict_paper_equivalent_full_staged_feasibility")
    robustness_req = requirement_by_id(completion, "robustness_to_contact_model_perturbations")
    hardware_req = requirement_by_id(completion, "hardware_readiness")

    geometry_checks = geometry["readiness_checks"]
    insufficient_geometry_checks = [
        check["name"] for check in geometry_checks if not bool(check["constrains_v85_margin"])
    ]

    return [
        blocker_row(
            blocker_id="approved_read_only_calibration_evidence",
            title="Approved read-only calibration evidence",
            priority_rank=0,
            category="approval_blocked_prerequisite",
            status="approval_required_prerequisite",
            can_advance_offline=False,
            requires_explicit_approval=True,
            evidence_summary={
                "approved_read_only_run_count": int(read_only_req["evidence"][0]["approved_read_only_run_count"]),
                "latest_audit_mode": str(read_only["audit_mode"]),
                "latest_audit_passed": bool(read_only["audit_passed"]),
                "live_hardware_accessed": bool(read_only["execution"]["live_hardware_accessed"]),
                "robot_motion_commanded": bool(read_only["execution"]["robot_motion_commanded"]),
                "configuration_written": bool(read_only["execution"]["configuration_written"]),
            },
            blockers=list(read_only_req["blocked_by"]),
            next_action=str(read_only_req["next_action"]),
        ),
        blocker_row(
            blocker_id="orientation_gate_acceptance",
            title="Orientation gate acceptance",
            priority_rank=1,
            category="evidence_and_review_blocked",
            status="blocked_on_evidence_and_separate_review",
            can_advance_offline=False,
            requires_explicit_approval=True,
            evidence_summary={
                "decision": str(gate_review["orientation_gate_acceptance"]["decision"]),
                "review_status": str(gate_review["review_status"]),
                "accepted_review_count": int(gate_req["evidence"][0]["accepted_review_count"]),
                "gate_acceptance_blocked_cell_ids": list(
                    matrix["summary"]["gate_acceptance_blocked_cell_ids"]
                ),
                "accepted_gate_value_rad": gate_review["orientation_gate_acceptance"][
                    "accepted_gate_value_rad"
                ],
            },
            blockers=list(gate_req["blocked_by"]),
            next_action=str(gate_req["next_action"]),
        ),
        blocker_row(
            blocker_id="calibrated_contact_geometry",
            title="Calibrated contact geometry and force-frame evidence",
            priority_rank=2,
            category="measurement_blocked",
            status="blocked_on_approved_measurements",
            can_advance_offline=False,
            requires_explicit_approval=True,
            evidence_summary={
                "records_sufficient_for_v85_margin": bool(
                    geometry["verdict"]["records_sufficient_for_v85_margin"]
                ),
                "supports_accepting_v85_margin": bool(
                    geometry["verdict"]["supports_accepting_v85_margin"]
                ),
                "insufficient_check_count": len(insufficient_geometry_checks),
                "insufficient_checks": insufficient_geometry_checks,
                "force_source_frame_status": next(
                    check["status"] for check in geometry_checks if check["name"] == "force_source_frame"
                ),
            },
            blockers=list(contact_req["blocked_by"]),
            next_action=str(contact_req["next_action"]),
        ),
        blocker_row(
            blocker_id="strict_paper_equivalent_full_staged_feasibility",
            title="Strict paper-equivalent full staged feasibility",
            priority_rank=3,
            category="offline_actionable_nonfinal",
            status="offline_actionable_nonfinal",
            can_advance_offline=True,
            requires_explicit_approval=False,
            evidence_summary={
                "strict_feasibility_complete": bool(strict["strict_feasibility_complete"]),
                "strict_setup_gate_complete": bool(strict["strict_setup_gate_complete"]),
                "strict_full_staged_feasibility_pass_count": int(
                    strict["blocker_summary"]["strict_full_staged_feasibility_pass_count"]
                ),
                "strict_full_staged_feasibility_case_count": int(
                    strict["blocker_summary"]["strict_case_count"]
                ),
                "three_phase_setup_terminal_state_pass_count": int(
                    strict["blocker_summary"]["setup_terminal_state_pass_count"]
                ),
                "three_phase_setup_terminal_state_case_count": int(
                    strict["blocker_summary"]["three_phase_case_count"]
                ),
                "three_phase_trajectory_feasibility_pass_count": int(
                    strict["blocker_summary"]["trajectory_feasibility_pass_count"]
                ),
                "three_phase_trajectory_feasibility_case_count": int(
                    strict["blocker_summary"]["three_phase_case_count"]
                ),
                "primary_blocker": str(strict["blocker_summary"]["primary_blocker"]),
            },
            blockers=list(strict_req["blocked_by"]),
            next_action=str(strict_req["next_action"]),
        ),
        blocker_row(
            blocker_id="robustness_to_contact_model_perturbations",
            title="Robustness matrix completion under accepted model",
            priority_rank=4,
            category="offline_actionable_nonfinal_but_gate_contact_blocked",
            status="offline_actionable_but_final_claim_blocked",
            can_advance_offline=True,
            requires_explicit_approval=False,
            evidence_summary={
                "robustness_complete": bool(robustness["robustness_complete"]),
                "restatement_supported": bool(matrix["summary"]["restatement_supported"]),
                "profile_overlay_supported_count": int(
                    matrix["summary"]["profile_overlay_supported_count"]
                ),
                "gate_acceptance_blocked_cell_ids": list(
                    matrix["summary"]["gate_acceptance_blocked_cell_ids"]
                ),
                "closed_cell_count": int(matrix["summary"]["closed_cell_count"]),
                "accepted_as_robustness_proof": bool(
                    matrix["summary"]["accepted_as_robustness_proof"]
                ),
            },
            blockers=list(robustness_req["blocked_by"]),
            next_action=(
                "Continue only non-final stress bookkeeping until gate/contact "
                "dependencies are accepted."
            ),
        ),
        blocker_row(
            blocker_id="hardware_readiness",
            title="Hardware readiness",
            priority_rank=5,
            category="approval_and_evidence_blocked_terminal",
            status="blocked_on_evidence_chain",
            can_advance_offline=False,
            requires_explicit_approval=True,
            evidence_summary={
                "hardware_readiness_claim": False,
                "hardware_gate_report_exists": bool(hardware_req["evidence"][0]["exists"]),
                "latest_read_only_runs_have_hardware_readiness": list(
                    hardware_req["evidence"][0]["latest_read_only_runs_have_hardware_readiness"]
                ),
                "latest_gate_reviews_have_hardware_readiness": list(
                    hardware_req["evidence"][0]["latest_gate_reviews_have_hardware_readiness"]
                ),
            },
            blockers=list(hardware_req["blocked_by"]),
            next_action=str(hardware_req["next_action"]),
        ),
    ]


def prioritize_blockers(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: row["priority_rank"])


def aggregate_rows(rows: list[dict[str, Any]], *, matrix: dict[str, Any]) -> dict[str, Any]:
    gate_blocked_ids = list(matrix["summary"]["gate_acceptance_blocked_cell_ids"])
    profile_overlay_ids = list(matrix["summary"]["profile_overlay_supported_cell_ids"])
    return {
        "remaining_blocker_count": len(rows),
        "approval_required_count": sum(1 for row in rows if row["requires_explicit_approval"]),
        "live_or_approval_blocked_count": sum(
            1 for row in rows if row["requires_explicit_approval"]
        ),
        "offline_actionable_nonfinal_count": sum(1 for row in rows if row["can_advance_offline"]),
        "completion_claim_allowed_count": sum(1 for row in rows if row["completion_claim_allowed"]),
        "top_priority_blocker_id": min(rows, key=lambda row: row["priority_rank"])["blocker_id"],
        "offline_actionable_blocker_ids": [
            row["blocker_id"] for row in rows if row["can_advance_offline"]
        ],
        "approval_required_blocker_ids": [
            row["blocker_id"] for row in rows if row["requires_explicit_approval"]
        ],
        "profile_overlay_supported_cell_ids": profile_overlay_ids,
        "profile_overlay_supported_cell_count": len(profile_overlay_ids),
        "gate_acceptance_blocked_cell_ids": gate_blocked_ids,
        "gate_acceptance_blocked_cell_count": len(gate_blocked_ids),
        "non_profile_covered_gate_blocked_cell_ids": gate_blocked_ids,
        "closed_cell_count": int(matrix["summary"]["closed_cell_count"]),
        "candidate_matrix_complete": bool(matrix["summary"]["candidate_matrix_complete"]),
        "accepted_as_robustness_proof": bool(matrix["summary"]["accepted_as_robustness_proof"]),
    }


def build_payload(
    *,
    completion_blockers_path: pathlib.Path,
    strict_blockers_path: pathlib.Path,
    robustness_blockers_path: pathlib.Path,
    matrix_restatement_path: pathlib.Path,
    measured_geometry_path: pathlib.Path,
    read_only_audit_path: pathlib.Path,
    gate_review_audit_path: pathlib.Path,
) -> dict[str, Any]:
    completion = load_yaml(completion_blockers_path)
    strict = load_yaml(strict_blockers_path)
    robustness = load_yaml(robustness_blockers_path)
    matrix = load_yaml(matrix_restatement_path)
    geometry = load_yaml(measured_geometry_path)
    read_only = load_yaml(read_only_audit_path)
    gate_review = load_yaml(gate_review_audit_path)
    rows = build_priority_rows(
        completion=completion,
        strict=strict,
        robustness=robustness,
        matrix=matrix,
        geometry=geometry,
        read_only=read_only,
        gate_review=gate_review,
    )
    rows = prioritize_blockers(rows)
    aggregate = aggregate_rows(rows, matrix=matrix)
    return {
        "run_source": "v112 remaining blocker prioritization",
        "source_files": {
            "completion_blockers": str(completion_blockers_path),
            "strict_blockers": str(strict_blockers_path),
            "robustness_blockers": str(robustness_blockers_path),
            "weighted_profile_matrix_restatement": str(matrix_restatement_path),
            "measured_geometry_readiness": str(measured_geometry_path),
            "read_only_measurement_audit": str(read_only_audit_path),
            "orientation_gate_acceptance_review_audit": str(gate_review_audit_path),
        },
        "blocker_rows": rows,
        "aggregate": aggregate,
        "summary": {
            "overall_goal_complete": False,
            "completion_blocked": True,
            "do_not_mark_goal_complete": True,
            "top_priority_blocker_id": aggregate["top_priority_blocker_id"],
            "remaining_blocker_count": aggregate["remaining_blocker_count"],
            "approval_required_count": aggregate["approval_required_count"],
            "live_or_approval_blocked_count": aggregate["live_or_approval_blocked_count"],
            "offline_actionable_nonfinal_count": aggregate[
                "offline_actionable_nonfinal_count"
            ],
            "completion_claim_allowed_count": aggregate["completion_claim_allowed_count"],
            "offline_actionable_blocker_ids": aggregate["offline_actionable_blocker_ids"],
            "approval_required_blocker_ids": aggregate["approval_required_blocker_ids"],
            "non_profile_covered_gate_blocked_cell_ids": aggregate[
                "non_profile_covered_gate_blocked_cell_ids"
            ],
            "profile_overlay_supported_cell_count": aggregate[
                "profile_overlay_supported_cell_count"
            ],
            "profile_overlay_supported_cell_ids": aggregate[
                "profile_overlay_supported_cell_ids"
            ],
            "gate_acceptance_blocked_cell_count": aggregate[
                "gate_acceptance_blocked_cell_count"
            ],
            "gate_acceptance_blocked_cell_ids": aggregate[
                "gate_acceptance_blocked_cell_ids"
            ],
            "closed_cell_count": aggregate["closed_cell_count"],
            "candidate_matrix_complete": aggregate["candidate_matrix_complete"],
            "accepted_as_robustness_proof": aggregate["accepted_as_robustness_proof"],
        },
        "claim_boundary": {
            "post_hoc_offline_audit_only": True,
            "failed_cell_closed": False,
            "canonical_controller_change": False,
            "canonical_orientation_gate_change": False,
            "robustness_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "contact_calibration_claim": False,
            "hardware_readiness": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
        },
        "next_offline_actions": [
            "Do not claim completion from this prioritization audit.",
            "If no live approval exists, strict feasibility is the most direct offline-actionable technical blocker.",
            "Gate acceptance, contact calibration, and hardware readiness remain blocked on approved read-only evidence.",
            "Keep the read-only SOP path explicit and separate from any simulation restatement.",
        ],
        "warnings": [
            "post-hoc offline audit of existing metrics only",
            "does not run MuJoCo",
            "does not execute read-only hardware steps",
            "does not accept a replacement orientation gate",
            "does not calibrate contact geometry or force frames",
            "not strict paper-equivalent feasibility",
            "not a robustness proof",
            "not hardware-ready",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Remaining Blocker Prioritization Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Overall goal complete: `{summary['overall_goal_complete']}`",
        f"- Completion blocked: `{summary['completion_blocked']}`",
        f"- Top priority blocker: `{summary['top_priority_blocker_id']}`",
        f"- Remaining blockers: `{summary['remaining_blocker_count']}`",
        f"- Live or approval blocked blockers: `{summary['live_or_approval_blocked_count']}`",
        f"- Offline-actionable non-final blockers: `{summary['offline_actionable_nonfinal_count']}`",
        f"- Profile-overlay supported cells: `{summary['profile_overlay_supported_cell_count']}`",
        f"- Gate-acceptance blocked cells: `{summary['gate_acceptance_blocked_cell_count']}`",
        f"- Closed cells: `{summary['closed_cell_count']}`",
        f"- Approval-required blockers: `{', '.join(summary['approval_required_blocker_ids'])}`",
        f"- Offline-actionable non-final blockers: `{', '.join(summary['offline_actionable_blocker_ids'])}`",
        f"- Non-profile-covered gate-blocked cells: `{', '.join(summary['non_profile_covered_gate_blocked_cell_ids'])}`",
        "",
        "| rank | blocker | category | status | offline | approval | completion claim |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["blocker_rows"]:
        lines.append(
            "| `{rank}` | `{blocker}` | `{category}` | `{status}` | `{offline}` | `{approval}` | `{completion}` |".format(
                rank=row["priority_rank"],
                blocker=row["blocker_id"],
                category=row["category"],
                status=row["status"],
                offline=row["can_advance_offline"],
                approval=row["requires_explicit_approval"],
                completion=row["completion_claim_allowed"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- Approved read-only calibration evidence is the prerequisite for gate acceptance, contact calibration, and hardware readiness.",
            "- Strict feasibility and robustness bookkeeping can still advance offline, but only as non-final evidence.",
            "- The v111 named-profile restatement does not remove the gate-acceptance blocked rows.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--completion-blockers", default=DEFAULT_COMPLETION_BLOCKERS)
    parser.add_argument("--strict-blockers", default=DEFAULT_STRICT_BLOCKERS)
    parser.add_argument("--robustness-blockers", default=DEFAULT_ROBUSTNESS_BLOCKERS)
    parser.add_argument("--matrix-restatement", default=DEFAULT_MATRIX_RESTATEMENT)
    parser.add_argument("--measured-geometry", default=DEFAULT_MEASURED_GEOMETRY)
    parser.add_argument("--read-only-audit", default=DEFAULT_READ_ONLY_AUDIT)
    parser.add_argument("--gate-review-audit", default=DEFAULT_GATE_REVIEW_AUDIT)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "remaining_blocker_prioritization" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        completion_blockers_path=(ROOT / args.completion_blockers).resolve(),
        strict_blockers_path=(ROOT / args.strict_blockers).resolve(),
        robustness_blockers_path=(ROOT / args.robustness_blockers).resolve(),
        matrix_restatement_path=(ROOT / args.matrix_restatement).resolve(),
        measured_geometry_path=(ROOT / args.measured_geometry).resolve(),
        read_only_audit_path=(ROOT / args.read_only_audit).resolve(),
        gate_review_audit_path=(ROOT / args.gate_review_audit).resolve(),
    )
    payload["run_id"] = run_id
    with (out_dir / "metrics.yaml").open("w", encoding="utf-8") as f:
        yaml.dump(payload, f, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True)
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
