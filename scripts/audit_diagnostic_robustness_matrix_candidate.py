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

OFFLINE_BLOCKERS_METRICS = ROOT / "runs" / "offline_completion_blockers" / "20260525T020734" / "metrics.yaml"
STRICT_BLOCKERS_METRICS = ROOT / "runs" / "strict_feasibility_blockers" / "20260525T051640" / "metrics.yaml"
ROBUSTNESS_BLOCKERS_METRICS = ROOT / "runs" / "robustness_blockers" / "20260525T052457" / "metrics.yaml"


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)


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


def cell(
    *,
    cell_id: str,
    source: str,
    status: str,
    evidence: dict[str, Any],
    blocker_ids: list[str] | None = None,
    note: str,
) -> dict[str, Any]:
    return {
        "id": cell_id,
        "source": source,
        "status": status,
        "evidence": evidence,
        "blocker_ids": blocker_ids or [],
        "note": note,
    }


def build_cells(robustness: dict[str, Any]) -> list[dict[str, Any]]:
    baseline = robustness["baseline_sensitivity"]
    timing = robustness["timing_margin"]
    base_z = robustness["base_z_recovery"]
    positive = robustness["positive_stitched_sensitivity"]
    qdot012 = robustness["qdot012_positive_recovery"]
    orientation = robustness["weighted_orientation_model_sensitivity"]

    failing_details = positive["failing_scenario_details"]

    return [
        cell(
            cell_id="baseline_nominal",
            source=baseline["path"],
            status="passed_diagnostic",
            evidence={"case": "nominal", "passing_cases": list(baseline["passing_cases"])},
            note="Nominal stitched diagnostic policy passes in the v64 baseline sensitivity set.",
        ),
        cell(
            cell_id="baseline_force_gain_low",
            source=baseline["path"],
            status="passed_diagnostic",
            evidence={"case": "force_gain_5e-5", "passing_cases": list(baseline["passing_cases"])},
            note="Lower force-gain perturbation passes in the v64 baseline sensitivity set.",
        ),
        cell(
            cell_id="baseline_force_gain_high",
            source=baseline["path"],
            status="passed_diagnostic",
            evidence={"case": "force_gain_2e-4", "passing_cases": list(baseline["passing_cases"])},
            note="Higher force-gain perturbation passes in the v64 baseline sensitivity set.",
        ),
        cell(
            cell_id="stage_a_duration_14p5",
            source=timing["path"],
            status="passed_diagnostic",
            evidence=timing["recovered_boundaries"]["stage_a_duration_s"],
            note="The 14.0 s Stage A reference fails, while the tested 14.5 s recovery passes.",
        ),
        cell(
            cell_id="qdot012_stage_a_18p0",
            source=timing["path"],
            status="passed_diagnostic",
            evidence=timing["recovered_boundaries"]["qdot012_stage_a_duration_s"],
            note="The qdot012 Stage A row recovers at the tested 18.0 s timing-margin point.",
        ),
        cell(
            cell_id="paper_time_scale_0p012",
            source=timing["path"],
            status="passed_diagnostic",
            evidence=timing["recovered_boundaries"]["paper_time_scale"],
            note="The tested paper_time_scale 0.012 row passes; 0.0125 remains failing.",
        ),
        cell(
            cell_id="base_z_minus1mm_stage_a_16s",
            source=base_z["path"],
            status="passed_diagnostic",
            evidence={"recovered_cases": base_z["recovered_cases"]},
            note="The -1.0 mm base-z row recovers only in the tested 16.0 s Stage A variant.",
        ),
        cell(
            cell_id="base_z_plus1mm",
            source=base_z["path"],
            status="failed",
            evidence=base_z["status_by_case"]["base_z_plus_1mm"],
            blocker_ids=["base_z_plus_1mm_contact_or_terminal_orientation"],
            note="The +1.0 mm base-z row has no start/terminal recovery in the v66 audit.",
        ),
        cell(
            cell_id="positive_qdot012_full_matrix_18p035",
            source=qdot012["path"],
            status="passed_diagnostic_nonfinal",
            evidence={
                "case_count": qdot012["case_count"],
                "stitched_pass_count": qdot012["stitched_pass_count"],
                "stage_a_duration_s": qdot012["stage_a_duration_s"],
                "qdot_limit_rad_s": qdot012["qdot_limit_rad_s"],
            },
            note="The v75 positive qdot012 matrix passes, but its own claim scope is diagnostic non-final.",
        ),
        cell(
            cell_id="positive_fast_timing_0p0075",
            source=positive["path"],
            status="failed",
            evidence=failing_details["paper_time_scale_0p0075"],
            blocker_ids=["faster_timing_qdot_tail_utilization"],
            note="The positive paper_time_scale 0.0075 scenario still fails the +1.0 mm row.",
        ),
        cell(
            cell_id="positive_orientation_gate_0p119",
            source=positive["path"],
            status="failed",
            evidence=failing_details["orientation_gate_0p119"],
            blocker_ids=["tightened_orientation_gate_plus1mm", "contact_model_calibration_missing"],
            note="The +1.0 mm row still fails the 0.119 rad orientation gate without accepted calibration.",
        ),
        cell(
            cell_id="weighted_plus1mm_0p119_gate",
            source=orientation["path"],
            status="failed",
            evidence={
                "max_stage_b_excess_over_gate_rad": orientation["max_stage_b_excess_over_gate_rad"],
                "max_stage_b_excess_over_gate_deg": orientation["max_stage_b_excess_over_gate_deg"],
                "failing_cases": orientation["failing_cases"],
            },
            blocker_ids=["tightened_orientation_gate_plus1mm", "contact_model_calibration_missing"],
            note="All critical weighted +1.0 mm rows fail the current 0.119 rad orientation gate.",
        ),
    ]


def summarize_cells(cells: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    blocker_counts: dict[str, int] = {}
    for item in cells:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1
        for blocker in item["blocker_ids"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    failed = [item["id"] for item in cells if item["status"] == "failed"]
    passed = [item["id"] for item in cells if item["status"].startswith("passed")]
    nonfinal = [item["id"] for item in cells if item["status"] == "passed_diagnostic_nonfinal"]
    return {
        "cell_count": len(cells),
        "status_counts": dict(sorted(status_counts.items())),
        "passed_or_recovered_cell_ids": passed,
        "nonfinal_recovered_cell_ids": nonfinal,
        "failed_cell_ids": failed,
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "all_cells_passed": not failed,
    }


def build_audit() -> dict[str, Any]:
    offline = load_yaml(OFFLINE_BLOCKERS_METRICS)
    strict = load_yaml(STRICT_BLOCKERS_METRICS)
    robustness = load_yaml(ROBUSTNESS_BLOCKERS_METRICS)

    cells = build_cells(robustness)
    matrix_summary = summarize_cells(cells)
    claim_dependencies = {
        "strict_feasibility_complete": strict.get("strict_feasibility_complete"),
        "robustness_complete_from_v97": robustness.get("robustness_complete"),
        "approved_read_only_calibration_evidence": False,
        "orientation_gate_acceptance": False,
        "contact_calibration_claim": False,
    }
    blocking_dependencies = [
        key for key, value in claim_dependencies.items() if value is not True
    ]
    candidate_complete = matrix_summary["all_cells_passed"] and not blocking_dependencies

    return {
        "audit_source": "v98 diagnostic robustness matrix candidate",
        "overall_goal_complete": False,
        "candidate_matrix_complete": candidate_complete,
        "accepted_as_robustness_proof": False,
        "completion_claim_allowed": False,
        "offline_actionable_from_v95": "robustness_to_contact_model_perturbations"
        in offline.get("offline_actionable_nonfinal_requirement_ids", []),
        "source_files": {
            "offline_blockers_metrics": relative(OFFLINE_BLOCKERS_METRICS),
            "strict_blockers_metrics": relative(STRICT_BLOCKERS_METRICS),
            "robustness_blockers_metrics": relative(ROBUSTNESS_BLOCKERS_METRICS),
        },
        "matrix_definition": {
            "scope": "diagnostic_candidate_only",
            "description": (
                "A single bookkeeping matrix over the currently recovered and failing diagnostic "
                "robustness faces. It is not an accepted robustness proof."
            ),
            "cells": cells,
        },
        "matrix_summary": matrix_summary,
        "claim_dependencies": claim_dependencies,
        "blocking_dependencies": blocking_dependencies,
        "claim_boundary": {
            "do_not_mark_goal_complete": True,
            "robustness_claim": False,
            "paper_equivalent_feasibility": False,
            "contact_calibration_claim": False,
            "orientation_gate_acceptance": False,
            "hardware_readiness": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "hardware_readiness_claim": False,
        },
        "next_offline_actions": [
            "Convert failed cells into a concrete offline experiment matrix before adding more recovery variants.",
            "Keep positive qdot012 recovery separate from an accepted robustness proof until all cells and dependencies pass.",
            "Do not accept the 0.119 rad orientation gate or contact-model correction without approved read-only evidence.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["matrix_summary"]
    lines = [
        "# Diagnostic Robustness Matrix Candidate",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Candidate matrix complete: `{payload['candidate_matrix_complete']}`",
        f"- Accepted as robustness proof: `{payload['accepted_as_robustness_proof']}`",
        f"- Completion claim allowed: `{payload['completion_claim_allowed']}`",
        f"- Cell count: `{summary['cell_count']}`",
        f"- Status counts: `{summary['status_counts']}`",
        f"- Failed cells: `{summary['failed_cell_ids']}`",
        f"- Blocking dependencies: `{payload['blocking_dependencies']}`",
        "",
        "## Claim Boundary",
        "",
        "- This matrix is diagnostic bookkeeping only.",
        "- It does not prove robustness, strict paper-equivalent feasibility,",
        "  contact calibration, gate acceptance, or hardware readiness.",
    ]
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
        else ROOT / "runs" / "diagnostic_robustness_matrix_candidate" / run_id
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
