#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Any

import numpy as np
import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.audit_calibrated_overlay_force_response_after_v149 import measure_row, validate_ladder  # noqa: E402


DEFAULT_CONFIG = "configs/mujoco_ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.yaml"
DEFAULT_PREVIOUS = "runs/calibrated_overlay_force_response_after_v149/20260525T230000/metrics.yaml"
DEFAULT_TARGET_FORCE_N = 5.0
DEFAULT_SCAN_M = [
    0.0,
    1.0e-12,
    1.0e-10,
    1.0e-9,
    1.0e-8,
    1.0e-7,
    1.0e-6,
    2.0e-6,
    5.0e-6,
    1.0e-5,
    2.0e-5,
    5.0e-5,
    1.0e-4,
    2.5e-4,
    5.0e-4,
    1.0e-3,
    1.5e-3,
    2.0e-3,
]
DEFAULT_FORCE_TOLERANCE_N = 0.25


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
    path.parent.mkdir(parents=True, exist_ok=True)
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


def bracket_crosses_target(rows: list[dict[str, Any]], *, target_force_N: float) -> bool:
    forces = [float(row["target_normal_force_N"]) for row in rows]
    target = float(target_force_N)
    return any((a - target) * (b - target) <= 0.0 for a, b in zip(forces, forces[1:]))


def build_payload(
    *,
    config_path: pathlib.Path,
    previous_metrics_path: pathlib.Path,
    run_id: str,
    target_force_N: float,
    scan_m: list[float],
    force_tolerance_N: float,
) -> dict[str, Any]:
    violations: list[str] = []
    config = load_yaml(config_path)
    previous = load_yaml(previous_metrics_path)
    ur = config["ur10e_mujoco"]
    contact = ur["contact"]
    model_path = resolve(ur["mjcf_path"])
    seed_path = resolve(ur["source_seed_path"])
    seed = load_yaml(seed_path)
    q = np.asarray(seed["current_rtde_state"]["actual_q_rad"], dtype=float)
    normal = np.asarray(contact["expected_normal_world"], dtype=float)
    normal = normal / np.linalg.norm(normal)
    scan = validate_ladder(scan_m)

    previous_summary = previous.get("summary", {})
    if previous_summary.get("force_response_ladder_passed") is not True:
        violations.append("previous v150 force-response ladder did not pass")
    if previous_summary.get("diagnostic_overlay_acceptance_status") != "not_accepted":
        violations.append("previous v150 ladder drifted into accepted contact status")
    if previous_summary.get("completion_claim_allowed") is not False:
        violations.append("previous v150 ladder drifted into completion claim")

    rows = [
        measure_row(
            model_path=model_path,
            q=q,
            normal_world=normal,
            penetration_m=value,
            plane_geom_name=str(contact["plane_geom_name"]),
            tip_geom_name=str(contact["tip_geom_name"]),
        )
        for value in scan
    ]
    clean_all_rows = all(
        row["target_contact_pair_count"] == 1
        and row["non_target_contact_count"] == 0
        and row["counted_force_contacts"] == 1
        for row in rows
    )
    forces = [float(row["target_normal_force_N"]) for row in rows]
    positive_rows = [row for row in rows if row["penetration_m"] > 0.0]
    positive_forces = [float(row["target_normal_force_N"]) for row in positive_rows]
    minimum_positive_force_N = min(positive_forces)
    maximum_force_N = max(forces)
    zero_penetration_force_N = float(rows[0]["target_normal_force_N"])
    best_row = min(rows, key=lambda row: abs(float(row["target_normal_force_N"]) - float(target_force_N)))
    best_abs_error_N = abs(float(best_row["target_normal_force_N"]) - float(target_force_N))
    target_within_tolerance = best_abs_error_N <= float(force_tolerance_N)
    target_bracketed_by_scan = bracket_crosses_target(rows, target_force_N=target_force_N)
    positive_response_starts_above_target = minimum_positive_force_N > float(target_force_N)
    target_force_reachable_in_scan = target_within_tolerance or (
        target_bracketed_by_scan and not positive_response_starts_above_target
    )

    if not clean_all_rows:
        violations.append("target-force coverage scan includes non-target contacts")
    if target_force_reachable_in_scan:
        violations.append("unexpectedly reached target force in an audit meant to expose the current coverage gap")

    return {
        "run_source": "diagnostic overlay target force coverage audit after v150",
        "audit_run_id": run_id,
        "source_files": {
            "config": rel(config_path),
            "previous_force_response": rel(previous_metrics_path),
            "mjcf": rel(model_path),
            "seed": rel(seed_path),
        },
        "summary": {
            "audit_passed": not violations,
            "violations": violations,
            "target_force_N": float(target_force_N),
            "force_tolerance_N": float(force_tolerance_N),
            "scan_row_count": len(rows),
            "clean_target_contact_all_rows": clean_all_rows,
            "zero_penetration_force_N": zero_penetration_force_N,
            "minimum_positive_force_N": float(minimum_positive_force_N),
            "maximum_force_N": float(maximum_force_N),
            "best_penetration_m": float(best_row["penetration_m"]),
            "best_force_N": float(best_row["target_normal_force_N"]),
            "best_abs_error_N": float(best_abs_error_N),
            "target_within_tolerance": target_within_tolerance,
            "target_bracketed_by_scan": target_bracketed_by_scan,
            "positive_response_starts_above_target": positive_response_starts_above_target,
            "target_force_reachable_in_scan": target_force_reachable_in_scan,
            "coverage_gap_identified": not target_force_reachable_in_scan,
            "diagnostic_overlay_acceptance_status": "not_accepted",
            "approved_read_only_evidence_claim": False,
            "contact_setup_target_acceptance_claim": False,
            "orientation_gate_acceptance_claim": False,
            "hardware_readiness_claim": False,
            "completion_claim_allowed": False,
            "do_not_mark_goal_complete": True,
        },
        "rows": rows,
        "claim_boundary": {
            "offline_diagnostic_target_force_coverage_only": True,
            "live_hardware_accessed_by_this_audit": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "approved_read_only_evidence": False,
            "contact_calibration_claim": False,
            "contact_setup_target_acceptance": False,
            "setup_target_acceptance_claim": False,
            "orientation_gate_acceptance_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "robustness_claim": False,
            "hardware_readiness": False,
            "completion_claim_allowed": False,
            "do_not_mark_goal_complete": True,
        },
        "next_actions": [
            "Treat the current diagnostic overlay contact response as unable to cover the 5 N target without contact parameter or target-definition changes.",
            "Do not tune accepted contact stiffness from this audit; use it to guide a non-final contact-parameter diagnostic.",
            "Keep contact/setup-target acceptance review separate before any claim-closing use.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Overlay Target Force Coverage Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Target force: `{summary['target_force_N']}` N",
        f"- Target force reachable in scan: `{summary['target_force_reachable_in_scan']}`",
        f"- Coverage gap identified: `{summary['coverage_gap_identified']}`",
        f"- Minimum positive force: `{summary['minimum_positive_force_N']}` N",
        f"- Best penetration: `{summary['best_penetration_m']}` m",
        f"- Best force: `{summary['best_force_N']}` N",
        f"- Best absolute error: `{summary['best_abs_error_N']}` N",
        f"- Completion claim allowed: `{summary['completion_claim_allowed']}`",
        "",
        "| penetration m | target force N | target contacts | non-target contacts |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            "| "
            f"`{row['penetration_m']}` | "
            f"`{row['target_normal_force_N']}` | "
            f"`{row['target_contact_pair_count']}` | "
            f"`{row['non_target_contact_count']}` |"
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The current diagnostic overlay jumps from zero force at tangent contact to a minimum positive force above the 5 N target.",
            "- This is a non-final simulation-debugging blocker, not accepted contact calibration.",
        ]
    )
    if payload["summary"]["violations"]:
        lines.extend(["", "## Violations", ""])
        lines.extend(f"- {violation}" for violation in payload["summary"]["violations"])
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--previous-metrics", default=DEFAULT_PREVIOUS)
    parser.add_argument("--target-force-N", type=float, default=DEFAULT_TARGET_FORCE_N)
    parser.add_argument("--scan-m", type=float, nargs="+", default=DEFAULT_SCAN_M)
    parser.add_argument("--force-tolerance-N", type=float, default=DEFAULT_FORCE_TOLERANCE_N)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "overlay_target_force_coverage_after_v150" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    command = ["python3", "scripts/audit_overlay_target_force_coverage_after_v150.py", "--run-id", run_id]
    payload = build_payload(
        config_path=resolve(args.config),
        previous_metrics_path=resolve(args.previous_metrics),
        run_id=run_id,
        target_force_N=float(args.target_force_N),
        scan_m=[float(v) for v in args.scan_m],
        force_tolerance_N=float(args.force_tolerance_N),
    )
    payload["output_dir"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=command)
    print(json.dumps(payload["summary"], indent=2))
    return 0 if payload["summary"]["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
