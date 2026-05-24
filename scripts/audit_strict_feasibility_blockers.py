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

ACCEPTANCE_CONFIG = ROOT / "configs" / "ur10e_adapted_acceptance.yaml"
POSTURE_REGULARIZED_SUMMARY = (
    ROOT / "runs" / "staged_orientation_e1e4_posture_regularized" / "20260524T102747" / "summary.yaml"
)
THREE_PHASE_SUMMARY = (
    ROOT / "runs" / "staged_orientation_three_phase_settle" / "20260524T110039" / "summary.yaml"
)
OFFLINE_BLOCKERS_METRICS = ROOT / "runs" / "offline_completion_blockers" / "20260525T020734" / "metrics.yaml"


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


def pass_leq(value: float | None, threshold: float) -> bool | None:
    if value is None:
        return None
    return value <= threshold


def pass_geq(value: float | None, threshold: float) -> bool | None:
    if value is None:
        return None
    return value >= threshold


def metric_gap(value: float | None, threshold: float) -> float | None:
    if value is None:
        return None
    return value - threshold


def best_min(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    candidates = [row for row in rows if row.get(key) is not None]
    if not candidates:
        return {"case": None, "value": None, "setup_terminal_state_pass": None, "failed_criteria": []}
    best = min(candidates, key=lambda row: row[key])
    return {
        "case": best.get("case") or best.get("trajectory"),
        "value": best[key],
        "setup_terminal_state_pass": best.get("setup_terminal_state_pass"),
        "trajectory_feasibility_pass": best.get("trajectory_feasibility_pass"),
        "full_staged_feasibility_pass": best.get("full_staged_feasibility_pass"),
        "failed_criteria": list(best.get("setup_terminal_state_failed_criteria", [])),
    }


def count_true(rows: list[dict[str, Any]], key: str) -> int:
    return sum(1 for row in rows if row.get(key) is True)


def count_failed_criteria(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        for criterion in row.get("setup_terminal_state_failed_criteria", []):
            counts[criterion] = counts.get(criterion, 0) + 1
    return dict(sorted(counts.items()))


def count_threshold_failures(
    rows: list[dict[str, Any]], *, key: str, threshold: float, comparison: str = "leq"
) -> int:
    count = 0
    for row in rows:
        value = row.get(key)
        if value is None:
            continue
        if comparison == "leq" and value > threshold:
            count += 1
        elif comparison == "geq" and value < threshold:
            count += 1
    return count


def count_missing(rows: list[dict[str, Any]], key: str) -> int:
    return sum(1 for row in rows if row.get(key) is None)


def audit_posture_regularized(summary: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    rows = []
    tangential_threshold = thresholds["max_final_tangential_error_m"]
    orientation_threshold = thresholds["max_final_orientation_error_rad"]
    for row in summary["rows"]:
        tangential = row.get("approach_max_tangential_position_error_m")
        orientation = row.get("approach_final_orientation_error_rad")
        rows.append(
            {
                "trajectory": row["trajectory"],
                "approach_feasibility_pass": row.get("approach_feasibility_pass"),
                "trajectory_feasibility_pass": row.get("trajectory_feasibility_pass"),
                "full_staged_feasibility_pass": row.get("full_staged_feasibility_pass"),
                "strict_setup_checks": {
                    "final_tangential_position_error_m": {
                        "actual": tangential,
                        "threshold": tangential_threshold,
                        "passed": pass_leq(tangential, tangential_threshold),
                        "gap": metric_gap(tangential, tangential_threshold),
                    },
                    "final_orientation_error_rad": {
                        "actual": orientation,
                        "threshold": orientation_threshold,
                        "passed": pass_leq(orientation, orientation_threshold),
                        "gap": metric_gap(orientation, orientation_threshold),
                    },
                },
            }
        )
    tangential_failures = count_threshold_failures(
        summary["rows"], key="approach_max_tangential_position_error_m", threshold=tangential_threshold
    )
    orientation_failures = count_threshold_failures(
        summary["rows"], key="approach_final_orientation_error_rad", threshold=orientation_threshold
    )
    return {
        "path": relative(POSTURE_REGULARIZED_SUMMARY),
        "case_count": summary.get("case_count"),
        "approach_terminal_orientation_pass_count": summary.get(
            "approach_terminal_orientation_pass_count"
        ),
        "approach_feasibility_pass_count": summary.get("approach_feasibility_pass_count"),
        "trajectory_feasibility_pass_count": summary.get("trajectory_feasibility_pass_count"),
        "trajectory_after_approach_pass_count": summary.get("trajectory_after_approach_pass_count"),
        "full_staged_feasibility_pass_count": summary.get("full_staged_feasibility_pass_count"),
        "all_approaches_orientation_within_strict_gate": orientation_failures == 0,
        "all_approaches_tangential_outside_strict_gate": tangential_failures
        == summary.get("case_count"),
        "strict_failure_counts": {
            "final_tangential_position_error_m": tangential_failures,
            "final_orientation_error_rad": orientation_failures,
        },
        "dominant_blocker": "strict_setup_terminal_tangential_error",
        "rows": rows,
    }


def audit_three_phase(summary: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, Any]:
    rows = []
    tangential_threshold = thresholds["max_final_tangential_error_m"]
    orientation_threshold = thresholds["max_final_orientation_error_rad"]
    force_threshold = thresholds["max_tail_mean_abs_force_error_N"]
    qdot_saturation_threshold = thresholds["qdot_saturation_fraction_max"]
    for row in summary["rows"]:
        tangential = row.get("setup_final_tangential_position_error_m")
        orientation = row.get("setup_final_orientation_error_rad")
        force_candidates = [
            row.get("settle_tail_mean_abs_force_error_N"),
            row.get("recenter_tail_mean_abs_force_error_N"),
        ]
        force_values = [value for value in force_candidates if value is not None]
        force = force_values[0] if force_values else None
        qdot_saturation = row.get("settle_qdot_saturation_fraction")
        rows.append(
            {
                "case": row["case"],
                "setup_terminal_state_pass": row.get("setup_terminal_state_pass"),
                "full_staged_feasibility_pass": row.get("full_staged_feasibility_pass"),
                "failed_criteria": list(row.get("setup_terminal_state_failed_criteria", [])),
                "strict_setup_checks": {
                    "final_tangential_position_error_m": {
                        "actual": tangential,
                        "threshold": tangential_threshold,
                        "passed": pass_leq(tangential, tangential_threshold),
                        "gap": metric_gap(tangential, tangential_threshold),
                    },
                    "final_orientation_error_rad": {
                        "actual": orientation,
                        "threshold": orientation_threshold,
                        "passed": pass_leq(orientation, orientation_threshold),
                        "gap": metric_gap(orientation, orientation_threshold),
                    },
                    "tail_mean_abs_force_error_N": {
                        "actual": force,
                        "threshold": force_threshold,
                        "passed": pass_leq(force, force_threshold),
                        "gap": metric_gap(force, force_threshold),
                    },
                    "qdot_saturation_fraction": {
                        "actual": qdot_saturation,
                        "threshold": qdot_saturation_threshold,
                        "passed": pass_leq(qdot_saturation, qdot_saturation_threshold),
                        "gap": metric_gap(qdot_saturation, qdot_saturation_threshold),
                    },
                },
            }
        )
    bests = {
        "best_tangential_position_error_m": best_min(summary["rows"], "setup_final_tangential_position_error_m"),
        "best_orientation_error_rad": best_min(summary["rows"], "setup_final_orientation_error_rad"),
        "best_settle_tail_mean_abs_force_error_N": best_min(summary["rows"], "settle_tail_mean_abs_force_error_N"),
    }
    qdot_saturation_exceedance_count = count_threshold_failures(
        summary["rows"], key="settle_qdot_saturation_fraction", threshold=qdot_saturation_threshold
    )
    qdot_saturation_missing_count = count_missing(summary["rows"], "settle_qdot_saturation_fraction")
    return {
        "path": relative(THREE_PHASE_SUMMARY),
        "case_count": summary.get("case_count"),
        "setup_terminal_state_pass_count": summary.get("setup_terminal_state_pass_count"),
        "trajectory_feasibility_pass_count": summary.get("trajectory_feasibility_pass_count"),
        "legacy_trajectory_after_approach_pass_count": summary.get(
            "legacy_trajectory_after_approach_pass_count"
        ),
        "planned_setup_then_trajectory_pass_count": summary.get(
            "planned_setup_then_trajectory_pass_count"
        ),
        "full_staged_feasibility_pass_count": summary.get("full_staged_feasibility_pass_count"),
        "setup_failed_criteria_counts": count_failed_criteria(summary["rows"]),
        "trajectory_feasibility_pass_fraction": count_true(
            summary["rows"], "trajectory_feasibility_pass"
        )
        / summary["case_count"],
        "qdot_saturation_summary": {
            "threshold": qdot_saturation_threshold,
            "exceedance_count": qdot_saturation_exceedance_count,
            "missing_count": qdot_saturation_missing_count,
            "settled_rows_all_exceed": qdot_saturation_exceedance_count
            == summary["case_count"] - qdot_saturation_missing_count,
        },
        "observed_tradeoff": (
            "Rows that reduce tangential error either fail orientation or qdot/force criteria; "
            "rows that preserve trajectory feasibility still fail strict setup."
        ),
        "best_observed_metrics": bests,
        "rows": rows,
    }


def build_audit() -> dict[str, Any]:
    acceptance = load_yaml(ACCEPTANCE_CONFIG)
    thresholds = acceptance["strict_setup_terminal_gate"]
    posture = load_yaml(POSTURE_REGULARIZED_SUMMARY)
    three_phase = load_yaml(THREE_PHASE_SUMMARY)
    blockers = load_yaml(OFFLINE_BLOCKERS_METRICS)

    posture_audit = audit_posture_regularized(posture, thresholds)
    three_phase_audit = audit_three_phase(three_phase, thresholds)
    full_pass_count = posture.get("full_staged_feasibility_pass_count", 0)
    three_phase_full_pass_count = three_phase.get("full_staged_feasibility_pass_count", 0)
    strict_case_count = posture.get("case_count")
    three_phase_case_count = three_phase.get("case_count")
    strict_complete = full_pass_count == strict_case_count and strict_case_count is not None
    three_phase_setup_complete = (
        three_phase.get("setup_terminal_state_pass_count") == three_phase_case_count
        and three_phase_case_count is not None
    )
    trajectory_gate_often_passes = (
        three_phase.get("trajectory_feasibility_pass_count", 0) >= 0.5 * three_phase_case_count
        if three_phase_case_count
        else False
    )

    return {
        "audit_source": "v96 strict feasibility blockers",
        "overall_goal_complete": False,
        "strict_feasibility_complete": strict_complete,
        "strict_setup_gate_complete": three_phase_setup_complete,
        "strict_paper_equivalent_full_staged_feasibility_achieved": strict_complete,
        "trajectory_gate_often_passes": trajectory_gate_often_passes,
        "completion_claim_allowed": False,
        "offline_actionable_from_v95": "strict_paper_equivalent_full_staged_feasibility"
        in blockers.get("offline_actionable_nonfinal_requirement_ids", []),
        "source_files": {
            "acceptance_config": relative(ACCEPTANCE_CONFIG),
            "posture_regularized_summary": relative(POSTURE_REGULARIZED_SUMMARY),
            "three_phase_summary": relative(THREE_PHASE_SUMMARY),
            "offline_blockers_metrics": relative(OFFLINE_BLOCKERS_METRICS),
        },
        "strict_thresholds": {
            "max_final_tangential_error_m": thresholds["max_final_tangential_error_m"],
            "max_final_orientation_error_rad": thresholds["max_final_orientation_error_rad"],
            "max_tail_mean_abs_force_error_N": thresholds["max_tail_mean_abs_force_error_N"],
            "qdot_saturation_fraction_max": thresholds["qdot_saturation_fraction_max"],
        },
        "posture_regularized": posture_audit,
        "three_phase_settle": three_phase_audit,
        "blocker_summary": {
            "strict_case_count": strict_case_count,
            "strict_full_staged_feasibility_pass_count": full_pass_count,
            "three_phase_case_count": three_phase_case_count,
            "setup_terminal_state_pass_count": three_phase.get("setup_terminal_state_pass_count"),
            "trajectory_feasibility_pass_count": three_phase.get("trajectory_feasibility_pass_count"),
            "three_phase_full_staged_feasibility_pass_count": three_phase_full_pass_count,
            "primary_blocker": "strict_setup_terminal_tradeoff",
            "blocker_ids": [
                "strict_setup_terminal_tradeoff",
                "strict_setup_terminal_tangential_error",
                "settle_qdot_saturation",
            ],
            "primary_blockers": [
                "strict_setup_terminal_tradeoff",
                "strict_setup_terminal_tangential_error",
                "settle_qdot_saturation",
            ],
            "secondary_blockers": [
                "paper_platform_parity_split_claim",
                "uncalibrated_contact_geometry_for_gate_definition",
            ],
        },
        "claim_boundary": {
            "do_not_mark_goal_complete": True,
            "paper_equivalent_feasibility": False,
            "robustness_claim": False,
            "contact_calibration_claim": False,
            "hardware_readiness": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "hardware_readiness_claim": False,
        },
        "next_offline_actions": [
            "Search for a strict setup terminal policy that meets tangential, orientation, force, and qdot gates simultaneously.",
            "Keep any relaxed setup or diagnostic gate result separate from paper-equivalent feasibility.",
            "Do not use calibrated-contact or hardware-ready language until the read-only evidence chain is closed.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    blockers = payload["blocker_summary"]
    lines = [
        "# Strict Feasibility Blockers Audit",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Strict paper-equivalent achieved: `{payload['strict_paper_equivalent_full_staged_feasibility_achieved']}`",
        f"- Strict setup gate complete: `{payload['strict_setup_gate_complete']}`",
        f"- Trajectory gate often passes: `{payload['trajectory_gate_often_passes']}`",
        f"- Completion claim allowed: `{payload['completion_claim_allowed']}`",
        f"- Offline-actionable from v95: `{payload['offline_actionable_from_v95']}`",
        f"- Strict full staged pass count: `{blockers['strict_full_staged_feasibility_pass_count']} / {blockers['strict_case_count']}`",
        f"- Three-phase setup pass count: `{blockers['setup_terminal_state_pass_count']} / {blockers['three_phase_case_count']}`",
        f"- Three-phase trajectory pass count: `{blockers['trajectory_feasibility_pass_count']} / {blockers['three_phase_case_count']}`",
        f"- Primary blocker: `{blockers['primary_blocker']}`",
        f"- Blocker IDs: `{blockers['blocker_ids']}`",
        "",
        "## Observed Tradeoff",
        "",
        payload["three_phase_settle"]["observed_tradeoff"],
        "",
        "## Claim Boundary",
        "",
        "- This audit is offline simulation bookkeeping only.",
        "- It does not prove strict paper-equivalent feasibility, robustness,",
        "  contact calibration, or hardware readiness.",
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
        else ROOT / "runs" / "strict_feasibility_blockers" / run_id
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
