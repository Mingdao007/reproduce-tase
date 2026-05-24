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

DEFAULT_V98_MATRIX = "runs/diagnostic_robustness_matrix_candidate/20260525T053101/metrics.yaml"
DEFAULT_V99_PLAN = "runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/metrics.yaml"
DEFAULT_EXECUTION_AUDIT = "runs/failed_diagnostic_robustness_experiment_audit/20260525T061328/metrics.yaml"
DEFAULT_PROFILE_BOUNDARY = "runs/weighted_priority_profile_boundary/20260525T074100/metrics.yaml"


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True

PROFILE_OVERLAY_BY_CELL = {
    "base_z_plus1mm": {
        "overlay_face": "relaxed_base_z_plus1mm_handoff",
        "overlay_status": "profile_component_recovered_noncanonical",
        "reason": (
            "V108/V109 recover the relaxed Stage A/path/handoff components, "
            "but the original 0.08 rad exact failed cell is still open."
        ),
    },
    "positive_fast_timing_0p0075": {
        "overlay_face": "positive_fast_timing_full_e1e4",
        "overlay_status": "profile_recovered_noncanonical",
        "reason": (
            "V107 recovers the full E1-E4 face under the named weighted profile, "
            "but the controller/gate are not canonical."
        ),
    },
    "positive_orientation_gate_0p119": {
        "overlay_face": None,
        "overlay_status": "not_profile_recovered_gate_acceptance_blocked",
        "reason": "This row remains an orientation-gate acceptance blocker.",
    },
    "weighted_plus1mm_0p119_gate": {
        "overlay_face": None,
        "overlay_status": "not_profile_recovered_current_gate_blocked",
        "reason": (
            "The named profile uses the run-local 0.12 rad gate; this row is "
            "still the current 0.119 rad weighted gate failure."
        ),
    },
}


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


def cell_by_id(cells: list[dict[str, Any]], cell_id: str) -> dict[str, Any]:
    for cell in cells:
        if cell["id"] == cell_id:
            return cell
    raise KeyError(cell_id)


def experiment_ids(plan: dict[str, Any]) -> list[str]:
    return [str(experiment["id"]) for experiment in plan["experiments"]]


def execution_cell_ids(execution_audit: dict[str, Any]) -> list[str]:
    return [str(cell["cell_id"]) for cell in execution_audit["cell_results"]]


def summarize_profile_boundary(profile: dict[str, Any]) -> dict[str, Any]:
    boundary = profile["profile_boundary"]
    claim = boundary["claim_boundary"]
    return {
        "profile_name": boundary["profile_name"],
        "diagnostic_profile_naming_supported": bool(
            boundary["diagnostic_profile_naming_supported"]
        ),
        "covered_faces": list(boundary["covered_faces"]),
        "weighted_all_faces_recovered": bool(boundary["weighted_all_faces_recovered"]),
        "baseline_failure_reproduced_all_faces": bool(
            boundary["baseline_failure_reproduced_all_faces"]
        ),
        "canonical_controller_change": bool(claim["canonical_controller_change"]),
        "canonical_orientation_gate_change": bool(claim["canonical_orientation_gate_change"]),
        "failed_cell_closed": bool(claim["failed_cell_closed"]),
        "robustness_claim": bool(claim["robustness_claim"]),
        "hardware_readiness": bool(claim["hardware_readiness"]),
    }


def restate_failed_cell(
    *,
    cell: dict[str, Any],
    profile_summary: dict[str, Any],
    planned_ids: set[str],
    executed_ids: set[str],
    unresolved_ids: set[str],
) -> dict[str, Any]:
    overlay = PROFILE_OVERLAY_BY_CELL[cell["id"]]
    overlay_face = overlay["overlay_face"]
    face_covered = overlay_face in profile_summary["covered_faces"] if overlay_face else False
    can_apply_profile_overlay = (
        bool(profile_summary["diagnostic_profile_naming_supported"]) and face_covered
    )
    return {
        "cell_id": str(cell["id"]),
        "original_status": str(cell["status"]),
        "planned_in_v99": str(cell["id"]) in planned_ids,
        "executed_in_v100_v103": str(cell["id"]) in executed_ids,
        "unresolved_after_execution": str(cell["id"]) in unresolved_ids,
        "blocker_ids": list(cell["blocker_ids"]),
        "profile_overlay_face": overlay_face,
        "profile_overlay_status": overlay["overlay_status"],
        "profile_overlay_supported": can_apply_profile_overlay,
        "profile_overlay_reason": overlay["reason"],
        "restated_status": (
            "failed_with_noncanonical_profile_overlay"
            if can_apply_profile_overlay
            else "failed_without_profile_overlay"
        ),
        "failed_cell_closed": False,
        "canonical_controller_change": False,
        "canonical_orientation_gate_change": False,
        "robustness_claim": False,
    }


def build_payload(
    *,
    v98_matrix_path: pathlib.Path,
    v99_plan_path: pathlib.Path,
    execution_audit_path: pathlib.Path,
    profile_boundary_path: pathlib.Path,
) -> dict[str, Any]:
    v98 = load_yaml(v98_matrix_path)
    v99 = load_yaml(v99_plan_path)
    execution_audit = load_yaml(execution_audit_path)
    profile = load_yaml(profile_boundary_path)

    matrix = v98["matrix_definition"]
    cells = list(matrix["cells"])
    failed_ids = list(v98["matrix_summary"]["failed_cell_ids"])
    planned_ids = set(experiment_ids(v99))
    executed_ids = set(execution_cell_ids(execution_audit))
    unresolved_ids = set(execution_audit["summary"]["unresolved_executed_cell_ids"])
    profile_summary = summarize_profile_boundary(profile)
    failed_rows = [
        restate_failed_cell(
            cell=cell_by_id(cells, cell_id),
            profile_summary=profile_summary,
            planned_ids=planned_ids,
            executed_ids=executed_ids,
            unresolved_ids=unresolved_ids,
        )
        for cell_id in failed_ids
    ]
    overlay_supported = [row for row in failed_rows if row["profile_overlay_supported"]]
    gate_blocked = [
        row
        for row in failed_rows
        if "gate" in row["profile_overlay_status"] or "gate" in " ".join(row["blocker_ids"])
    ]
    restated_matrix = {
        "source_cell_count": int(v98["matrix_summary"]["cell_count"]),
        "source_status_counts": dict(v98["matrix_summary"]["status_counts"]),
        "source_failed_cell_ids": failed_ids,
        "v99_planned_failed_cell_ids": sorted(planned_ids),
        "executed_failed_cell_ids": sorted(executed_ids),
        "unresolved_executed_cell_ids": sorted(unresolved_ids),
        "profile_overlay_supported_cell_ids": [row["cell_id"] for row in overlay_supported],
        "profile_overlay_supported_count": len(overlay_supported),
        "gate_acceptance_blocked_cell_ids": [row["cell_id"] for row in gate_blocked],
        "closed_cell_count": 0,
        "restated_failed_cell_count": len(failed_rows),
        "restatement_supported": bool(
            profile_summary["diagnostic_profile_naming_supported"]
            and set(failed_ids) == planned_ids
            and set(failed_ids) == executed_ids
            and set(failed_ids) == unresolved_ids
        ),
        "restatement_complete": True,
        "candidate_matrix_complete": False,
        "accepted_as_robustness_proof": False,
        "all_failed_cells_closed": False,
    }
    return {
        "run_source": "v111 weighted profile matrix restatement",
        "source_files": {
            "v98_diagnostic_robustness_matrix": str(v98_matrix_path),
            "v99_failed_experiment_matrix": str(v99_plan_path),
            "v103_execution_audit": str(execution_audit_path),
            "v110_weighted_profile_boundary": str(profile_boundary_path),
        },
        "profile_summary": profile_summary,
        "restated_matrix": restated_matrix,
        "failed_cell_restatement_rows": failed_rows,
        "summary": {
            "profile_name": profile_summary["profile_name"],
            "restatement_supported": restated_matrix["restatement_supported"],
            "restatement_complete": restated_matrix["restatement_complete"],
            "source_cell_count": restated_matrix["source_cell_count"],
            "source_failed_cell_count": len(failed_ids),
            "profile_overlay_supported_count": restated_matrix[
                "profile_overlay_supported_count"
            ],
            "profile_overlay_supported_cell_ids": restated_matrix[
                "profile_overlay_supported_cell_ids"
            ],
            "gate_acceptance_blocked_cell_ids": restated_matrix[
                "gate_acceptance_blocked_cell_ids"
            ],
            "closed_cell_count": 0,
            "candidate_matrix_complete": False,
            "accepted_as_robustness_proof": False,
            "all_failed_cells_closed": False,
            "canonical_controller_change": False,
            "canonical_orientation_gate_change": False,
            "robustness_claim": False,
            "hardware_readiness": False,
            "do_not_mark_goal_complete": True,
        },
        "claim_boundary": {
            "post_hoc_offline_audit_only": True,
            "can_restate_matrix_with_named_profile": restated_matrix["restatement_supported"],
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
            "Do not convert the profile restatement into a robustness proof.",
            "Keep all original v99 failed cells open until canonical gate/controller/contact evidence exists.",
            "Treat gate-acceptance-blocked rows as requiring approved evidence or a separate accepted gate review.",
            "Keep live read-only SOP work blocked until explicit user approval exists for the exact step.",
        ],
        "warnings": [
            "post-hoc offline audit of existing metrics only",
            "does not rerun MuJoCo",
            "does not accept weighted priority as canonical",
            "does not accept the 0.12 rad orientation gate as canonical",
            "does not close original v99 failed cells",
            "not strict paper-equivalent feasibility",
            "not a robustness proof",
            "not contact-model calibration",
            "not hardware-ready",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Weighted Profile Matrix Restatement Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Profile name: `{summary['profile_name']}`",
        f"- Restatement supported: `{summary['restatement_supported']}`",
        f"- Source cells: `{summary['source_cell_count']}`",
        f"- Source failed cells: `{summary['source_failed_cell_count']}`",
        f"- Profile overlay supported cells: `{', '.join(summary['profile_overlay_supported_cell_ids']) or 'none'}`",
        f"- Gate-acceptance blocked cells: `{', '.join(summary['gate_acceptance_blocked_cell_ids']) or 'none'}`",
        f"- Closed cells: `{summary['closed_cell_count']}`",
        f"- Accepted as robustness proof: `{summary['accepted_as_robustness_proof']}`",
        f"- Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "| failed cell | profile overlay | supported | restated status | closed |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["failed_cell_restatement_rows"]:
        lines.append(
            "| `{cell}` | `{overlay}` | `{supported}` | `{status}` | `{closed}` |".format(
                cell=row["cell_id"],
                overlay=row["profile_overlay_face"] or "none",
                supported=row["profile_overlay_supported"],
                status=row["restated_status"],
                closed=row["failed_cell_closed"],
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The v98/v99 matrix can be restated with the named weighted diagnostic profile as a non-canonical overlay.",
            "- The overlay touches `base_z_plus1mm` and `positive_fast_timing_0p0075`; orientation-gate rows remain gate-acceptance blocked.",
            "- The restatement does not close failed cells, prove robustness, accept a controller or gate, or authorize hardware work.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v98-matrix", default=DEFAULT_V98_MATRIX)
    parser.add_argument("--v99-plan", default=DEFAULT_V99_PLAN)
    parser.add_argument("--execution-audit", default=DEFAULT_EXECUTION_AUDIT)
    parser.add_argument("--profile-boundary", default=DEFAULT_PROFILE_BOUNDARY)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run_id = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "weighted_profile_matrix_restatement" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        v98_matrix_path=(ROOT / args.v98_matrix).resolve(),
        v99_plan_path=(ROOT / args.v99_plan).resolve(),
        execution_audit_path=(ROOT / args.execution_audit).resolve(),
        profile_boundary_path=(ROOT / args.profile_boundary).resolve(),
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
