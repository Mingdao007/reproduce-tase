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
DEFAULT_POST_V141_GATE = (
    "runs/post_v140_completion_gate/20260525T150000/metrics.yaml"
)
DEFAULT_MATRIX_RESTATEMENT = (
    "runs/weighted_profile_matrix_restatement/20260525T075040/metrics.yaml"
)
EXPECTED_FAILED_CELLS = [
    "base_z_plus1mm",
    "positive_fast_timing_0p0075",
    "positive_orientation_gate_0p119",
    "weighted_plus1mm_0p119_gate",
]
EXPECTED_PROFILE_OVERLAY_CELLS = [
    "base_z_plus1mm",
    "positive_fast_timing_0p0075",
]
EXPECTED_GATE_BLOCKED_CELLS = [
    "positive_orientation_gate_0p119",
    "weighted_plus1mm_0p119_gate",
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


def same_items(left: list[str], right: list[str]) -> bool:
    return sorted(left) == sorted(right)


def classify_frontier_row(row: dict[str, Any]) -> dict[str, Any]:
    cell_id = row["cell_id"]
    if row.get("profile_overlay_supported") is True:
        frontier_class = "profile_overlay_supported_noncanonical"
        blocking_dependencies = [
            "canonical_controller_or_profile_acceptance",
            "contact_setup_target_acceptance",
            "approved_read_only_calibration_evidence",
        ]
        next_nonfinal_action = (
            "Keep the profile overlay diagnostic; do not close the original failed cell "
            "until controller/profile and contact evidence are accepted."
        )
    else:
        frontier_class = "gate_or_contact_acceptance_blocked"
        blocking_dependencies = [
            "orientation_gate_acceptance",
            "contact_setup_target_acceptance",
            "approved_read_only_calibration_evidence",
        ]
        next_nonfinal_action = (
            "Do not rerun this cell as closure evidence; wait for approved contact/gate "
            "evidence or a separate accepted review."
        )
    return {
        "cell_id": cell_id,
        "frontier_class": frontier_class,
        "original_status": row.get("original_status"),
        "restated_status": row.get("restated_status"),
        "blocker_ids": row.get("blocker_ids", []),
        "profile_overlay_supported": row.get("profile_overlay_supported"),
        "profile_overlay_face": row.get("profile_overlay_face"),
        "profile_overlay_status": row.get("profile_overlay_status"),
        "failed_cell_closed": row.get("failed_cell_closed"),
        "canonical_controller_change": row.get("canonical_controller_change"),
        "canonical_orientation_gate_change": row.get("canonical_orientation_gate_change"),
        "robustness_claim": row.get("robustness_claim"),
        "blocking_dependencies": blocking_dependencies,
        "next_nonfinal_action": next_nonfinal_action,
    }


def build_payload(
    *,
    post_v141_gate_path: pathlib.Path,
    matrix_restatement_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    if not post_v141_gate_path.exists():
        violations.append(f"missing post-v141 completion gate metrics: {rel(post_v141_gate_path)}")
        post_gate: dict[str, Any] = {}
    else:
        post_gate = load_yaml(post_v141_gate_path)
    if not matrix_restatement_path.exists():
        violations.append(f"missing weighted-profile restatement metrics: {rel(matrix_restatement_path)}")
        restatement: dict[str, Any] = {}
    else:
        restatement = load_yaml(matrix_restatement_path)

    gate_summary = post_gate.get("summary", {})
    restated_matrix = restatement.get("restated_matrix", {})
    restatement_summary = restatement.get("summary", {})
    profile_summary = restatement.get("profile_summary", {})
    claim_boundary = restatement.get("claim_boundary", {})
    frontier_rows = [
        classify_frontier_row(row)
        for row in restatement.get("failed_cell_restatement_rows", [])
    ]
    frontier_by_class: dict[str, list[str]] = {}
    for row in frontier_rows:
        frontier_by_class.setdefault(row["frontier_class"], []).append(row["cell_id"])

    expected_gate_values = {
        "audit_passed": True,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
        "top_blocker": "approved_read_only_calibration_evidence",
        "approved_read_only_run_count": 0,
        "approved_read_only_audit_passed_count": 0,
        "accepted_orientation_review_count": 0,
        "accepted_contact_setup_target_review_count": 0,
        "closed_robustness_cell_count": 0,
        "status_answer_is_non_evidence": True,
        "continuation_boundary_is_non_evidence": True,
    }
    for key, expected in expected_gate_values.items():
        if gate_summary.get(key) != expected:
            violations.append(
                f"post_v141_completion_gate.summary.{key} is {gate_summary.get(key)!r}, "
                f"expected {expected!r}"
            )

    expected_restatement_values = {
        "restatement_supported": True,
        "restatement_complete": True,
        "source_failed_cell_count": 4,
        "profile_overlay_supported_count": 2,
        "closed_cell_count": 0,
        "candidate_matrix_complete": False,
        "accepted_as_robustness_proof": False,
        "all_failed_cells_closed": False,
        "canonical_controller_change": False,
        "canonical_orientation_gate_change": False,
        "robustness_claim": False,
        "hardware_readiness": False,
        "do_not_mark_goal_complete": True,
    }
    for key, expected in expected_restatement_values.items():
        if restatement_summary.get(key) != expected:
            violations.append(
                f"weighted_profile_matrix_restatement.summary.{key} is "
                f"{restatement_summary.get(key)!r}, expected {expected!r}"
            )
    if not same_items(restated_matrix.get("source_failed_cell_ids", []), EXPECTED_FAILED_CELLS):
        violations.append("source failed cell set drifted")
    if not same_items(
        restated_matrix.get("profile_overlay_supported_cell_ids", []),
        EXPECTED_PROFILE_OVERLAY_CELLS,
    ):
        violations.append("profile overlay supported cell set drifted")
    if not same_items(
        restated_matrix.get("gate_acceptance_blocked_cell_ids", []),
        EXPECTED_GATE_BLOCKED_CELLS,
    ):
        violations.append("gate acceptance blocked cell set drifted")
    if len(frontier_rows) != len(EXPECTED_FAILED_CELLS):
        violations.append(
            f"frontier row count is {len(frontier_rows)}, expected {len(EXPECTED_FAILED_CELLS)}"
        )
    for row in frontier_rows:
        if row["failed_cell_closed"] is not False:
            violations.append(f"{row['cell_id']} unexpectedly closed")
        if row["canonical_controller_change"] is not False:
            violations.append(f"{row['cell_id']} accepted canonical controller change")
        if row["canonical_orientation_gate_change"] is not False:
            violations.append(f"{row['cell_id']} accepted canonical orientation gate change")
        if row["robustness_claim"] is not False:
            violations.append(f"{row['cell_id']} drifted into a robustness claim")
    expected_claim_boundary = {
        "post_hoc_offline_audit_only": True,
        "can_restate_matrix_with_named_profile": True,
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
    }
    for key, expected in expected_claim_boundary.items():
        if claim_boundary.get(key) != expected:
            violations.append(
                f"weighted_profile_matrix_restatement.claim_boundary.{key} is "
                f"{claim_boundary.get(key)!r}, expected {expected!r}"
            )

    profile_overlay_rows = frontier_by_class.get("profile_overlay_supported_noncanonical", [])
    gate_blocked_rows = frontier_by_class.get("gate_or_contact_acceptance_blocked", [])
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "robustness_complete": False,
        "accepted_as_robustness_proof": False,
        "candidate_matrix_complete": False,
        "all_failed_cells_closed": False,
        "closed_cell_count": restatement_summary.get("closed_cell_count"),
        "source_failed_cell_count": restatement_summary.get("source_failed_cell_count"),
        "frontier_row_count": len(frontier_rows),
        "profile_overlay_supported_noncanonical_count": len(profile_overlay_rows),
        "profile_overlay_supported_noncanonical_cell_ids": profile_overlay_rows,
        "gate_or_contact_acceptance_blocked_count": len(gate_blocked_rows),
        "gate_or_contact_acceptance_blocked_cell_ids": gate_blocked_rows,
        "new_simulation_selected": False,
        "additional_failed_cell_execution_recommended": False,
        "requires_approved_read_only_evidence_for_closure": True,
        "requires_contact_setup_target_acceptance_for_closure": True,
        "requires_orientation_gate_acceptance_for_gate_rows": True,
        "source_approved_read_only_run_count": gate_summary.get("approved_read_only_run_count"),
        "source_approved_read_only_audit_passed_count": gate_summary.get(
            "approved_read_only_audit_passed_count"
        ),
        "source_accepted_orientation_review_count": gate_summary.get(
            "accepted_orientation_review_count"
        ),
        "source_accepted_contact_setup_target_review_count": gate_summary.get(
            "accepted_contact_setup_target_review_count"
        ),
        "source_readiness_completion_evidence_ids": gate_summary.get(
            "readiness_completion_evidence_ids"
        ),
        "do_not_mark_goal_complete": True,
    }
    return {
        "run_source": "robustness dependency frontier after v141",
        "audit_run_id": run_id,
        "source_files": {
            "post_v141_completion_gate": rel(post_v141_gate_path),
            "weighted_profile_matrix_restatement": rel(matrix_restatement_path),
        },
        "profile_summary": {
            "profile_name": profile_summary.get("profile_name"),
            "diagnostic_profile_naming_supported": profile_summary.get(
                "diagnostic_profile_naming_supported"
            ),
            "canonical_controller_change": profile_summary.get("canonical_controller_change"),
            "canonical_orientation_gate_change": profile_summary.get(
                "canonical_orientation_gate_change"
            ),
            "robustness_claim": profile_summary.get("robustness_claim"),
            "hardware_readiness": profile_summary.get("hardware_readiness"),
        },
        "summary": summary,
        "frontier_rows": frontier_rows,
        "claim_boundary": {
            "post_hoc_existing_metrics_only": True,
            "new_simulation_run": False,
            "new_failed_cell_execution_selected": False,
            "profile_overlay_is_noncanonical": True,
            "failed_cells_closed": False,
            "canonical_controller_change": False,
            "canonical_orientation_gate_change": False,
            "contact_calibration_claim": False,
            "orientation_gate_acceptance_claim": False,
            "robustness_proof": False,
            "strict_paper_equivalent_feasibility": False,
            "hardware_readiness": False,
            "live_hardware_access_authorized": False,
            "execution_authorized": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "do_not_mark_goal_complete": True,
        },
        "next_actions": [
            "Do not treat profile-overlay rows as closed robustness cells.",
            "Do not rerun gate-blocked cells as closure evidence before approved contact/gate evidence exists.",
            "Use exact phase1 read-only approval if the user provides it; otherwise continue only non-final offline audits.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Robustness Dependency Frontier After V141",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Robustness complete: `{summary['robustness_complete']}`",
        f"- Accepted as robustness proof: `{summary['accepted_as_robustness_proof']}`",
        f"- Closed cell count: `{summary['closed_cell_count']}`",
        f"- Frontier rows: `{summary['frontier_row_count']}`",
        f"- Profile-overlay noncanonical rows: `{summary['profile_overlay_supported_noncanonical_cell_ids']}`",
        f"- Gate/contact blocked rows: `{summary['gate_or_contact_acceptance_blocked_cell_ids']}`",
        f"- New simulation selected: `{summary['new_simulation_selected']}`",
        f"- Additional failed-cell execution recommended: `{summary['additional_failed_cell_execution_recommended']}`",
        f"- Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "## Frontier Rows",
        "",
    ]
    for row in payload["frontier_rows"]:
        lines.extend(
            [
                f"- `{row['cell_id']}`: `{row['frontier_class']}`",
                f"  - restated status: `{row['restated_status']}`",
                f"  - blocking dependencies: `{', '.join(row['blocking_dependencies'])}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This audit is offline bookkeeping only. It does not run simulations,",
            "close failed robustness cells, accept a controller or gate, collect",
            "live evidence, prove robustness, or establish hardware readiness.",
            "",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-v141-gate-path", default=DEFAULT_POST_V141_GATE)
    parser.add_argument("--matrix-restatement-path", default=DEFAULT_MATRIX_RESTATEMENT)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "robustness_dependency_frontier_after_v141" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        post_v141_gate_path=resolve(args.post_v141_gate_path),
        matrix_restatement_path=resolve(args.matrix_restatement_path),
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
