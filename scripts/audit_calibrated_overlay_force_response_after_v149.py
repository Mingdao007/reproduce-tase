#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Any

import mujoco
import numpy as np
import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.audit_calibrated_contact_overlay_after_v147 import contact_pair_counts, geom_id  # noqa: E402
from tase_repro.contact_ladder import positive_contact_normal_force_between  # noqa: E402
from tase_repro.kinematics import load_model, make_data, set_qpos  # noqa: E402


DEFAULT_CONFIG = "configs/mujoco_ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.yaml"
DEFAULT_PREVIOUS = "runs/calibrated_contact_overlay_after_v147/20260525T223000/metrics.yaml"
DEFAULT_LADDER_M = [0.0, 0.0001, 0.00025, 0.0005, 0.001, 0.0015, 0.002]
DEFAULT_FORCE_TOLERANCE_N = 1.0e-9
DEFAULT_DISTANCE_TOLERANCE_M = 1.0e-9


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


def validate_ladder(ladder_m: list[float]) -> list[float]:
    values = [float(value) for value in ladder_m]
    if not values:
        raise ValueError("ladder must not be empty")
    if values[0] < 0.0:
        raise ValueError("ladder values must be nonnegative")
    if any(value < 0.0 for value in values):
        raise ValueError("ladder values must be nonnegative")
    if values != sorted(values):
        raise ValueError("ladder values must be sorted ascending")
    if len(set(values)) != len(values):
        raise ValueError("ladder values must be unique")
    return values


def measure_row(
    *,
    model_path: pathlib.Path,
    q: np.ndarray,
    normal_world: np.ndarray,
    penetration_m: float,
    plane_geom_name: str,
    tip_geom_name: str,
) -> dict[str, Any]:
    model = load_model(model_path)
    data = make_data(model)
    plane_idx = geom_id(model, plane_geom_name)
    tip_idx = geom_id(model, tip_geom_name)
    model.geom_pos[plane_idx] += float(penetration_m) * normal_world
    set_qpos(model, data, q)
    target_count, non_target_count = contact_pair_counts(data, plane_idx=plane_idx, tip_idx=tip_idx)
    force_N, counted_force_contacts = positive_contact_normal_force_between(
        model,
        data,
        geom_a_name=plane_geom_name,
        geom_b_name=tip_geom_name,
    )
    contact_distances = [
        float(data.contact[idx].dist)
        for idx in range(data.ncon)
        if {
            int(data.contact[idx].geom[0]),
            int(data.contact[idx].geom[1]),
        }
        == {int(plane_idx), int(tip_idx)}
    ]
    min_target_distance_m = min(contact_distances) if contact_distances else None
    return {
        "penetration_m": float(penetration_m),
        "model_ncon": int(data.ncon),
        "target_contact_pair_count": int(target_count),
        "non_target_contact_count": int(non_target_count),
        "counted_force_contacts": int(counted_force_contacts),
        "target_normal_force_N": float(force_N),
        "min_target_contact_distance_m": min_target_distance_m,
    }


def build_payload(
    *,
    config_path: pathlib.Path,
    previous_metrics_path: pathlib.Path,
    run_id: str,
    ladder_m: list[float],
    force_tolerance_N: float,
    distance_tolerance_m: float,
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
    ladder = validate_ladder(ladder_m)

    previous_summary = previous.get("summary", {})
    if previous_summary.get("simulation_can_start_from_diagnostic_overlay") is not True:
        violations.append("previous v149 overlay audit did not pass start-contact readiness")
    if previous_summary.get("diagnostic_overlay_acceptance_status") != "not_accepted":
        violations.append("previous v149 overlay audit drifted into accepted contact status")
    if previous_summary.get("completion_claim_allowed") is not False:
        violations.append("previous v149 overlay audit drifted into completion claim")

    rows = [
        measure_row(
            model_path=model_path,
            q=q,
            normal_world=normal,
            penetration_m=value,
            plane_geom_name=str(contact["plane_geom_name"]),
            tip_geom_name=str(contact["tip_geom_name"]),
        )
        for value in ladder
    ]
    forces = [float(row["target_normal_force_N"]) for row in rows]
    positive_rows = [row for row in rows if row["penetration_m"] > 0.0]
    clean_all_rows = all(
        row["target_contact_pair_count"] == 1
        and row["non_target_contact_count"] == 0
        and row["counted_force_contacts"] == 1
        for row in rows
    )
    zero_force_ok = forces[0] <= float(force_tolerance_N) if rows[0]["penetration_m"] == 0.0 else True
    positive_force_rows = all(row["target_normal_force_N"] > float(force_tolerance_N) for row in positive_rows)
    monotonic_force = all(
        float(next_force) + float(force_tolerance_N) >= float(force)
        for force, next_force in zip(forces, forces[1:])
    )
    strictly_increasing_positive_force = all(
        float(next_row["target_normal_force_N"]) > float(row["target_normal_force_N"])
        for row, next_row in zip(positive_rows, positive_rows[1:])
    )
    distances_match_penetration = all(
        row["min_target_contact_distance_m"] is not None
        and abs(float(row["min_target_contact_distance_m"]) + float(row["penetration_m"]))
        <= float(distance_tolerance_m)
        for row in rows
    )
    force_response_ladder_passed = all(
        [
            clean_all_rows,
            zero_force_ok,
            positive_force_rows,
            monotonic_force,
            strictly_increasing_positive_force,
            distances_match_penetration,
        ]
    )
    if not force_response_ladder_passed:
        violations.append("diagnostic overlay force-response ladder failed")

    return {
        "run_source": "calibrated overlay force response audit after v149",
        "audit_run_id": run_id,
        "source_files": {
            "config": rel(config_path),
            "previous_overlay_collision_mask": rel(previous_metrics_path),
            "mjcf": rel(model_path),
            "seed": rel(seed_path),
        },
        "summary": {
            "audit_passed": not violations,
            "violations": violations,
            "force_response_ladder_passed": force_response_ladder_passed,
            "row_count": len(rows),
            "penetration_ladder_m": [float(value) for value in ladder],
            "clean_target_contact_all_rows": clean_all_rows,
            "zero_penetration_force_ok": zero_force_ok,
            "positive_penetration_force_positive": positive_force_rows,
            "target_force_monotonic_nondecreasing": monotonic_force,
            "positive_target_force_strictly_increasing": strictly_increasing_positive_force,
            "contact_distance_matches_penetration": distances_match_penetration,
            "min_positive_force_N": float(min(row["target_normal_force_N"] for row in positive_rows)),
            "max_force_N": float(max(forces)),
            "force_at_1mm_N": next(
                float(row["target_normal_force_N"]) for row in rows if abs(row["penetration_m"] - 0.001) < 1.0e-12
            ),
            "plane_geom_name": str(contact["plane_geom_name"]),
            "tip_geom_name": str(contact["tip_geom_name"]),
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
            "offline_diagnostic_force_response_only": True,
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
            "Use the ladder only as offline diagnostic force-response evidence for simulation debugging.",
            "Do not fit accepted contact stiffness or force control from this unaccepted overlay.",
            "Run contact/setup-target acceptance review before any claim-closing use.",
        ],
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Calibrated Overlay Force Response Summary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Force-response ladder passed: `{summary['force_response_ladder_passed']}`",
        f"- Rows: `{summary['row_count']}`",
        f"- Clean target contact in all rows: `{summary['clean_target_contact_all_rows']}`",
        f"- Force at 1 mm: `{summary['force_at_1mm_N']}` N",
        f"- Max force: `{summary['max_force_N']}` N",
        f"- Completion claim allowed: `{summary['completion_claim_allowed']}`",
        "",
        "| penetration m | target force N | target contacts | non-target contacts | min distance m |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            "| "
            f"`{row['penetration_m']}` | "
            f"`{row['target_normal_force_N']}` | "
            f"`{row['target_contact_pair_count']}` | "
            f"`{row['non_target_contact_count']}` | "
            f"`{row['min_target_contact_distance_m']}` |"
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The collision-masked overlay has a clean target-only contact response over the diagnostic penetration ladder.",
            "- This is an offline diagnostic force-response probe only, not accepted contact calibration or hardware evidence.",
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
    parser.add_argument("--ladder-m", type=float, nargs="+", default=DEFAULT_LADDER_M)
    parser.add_argument("--force-tolerance-N", type=float, default=DEFAULT_FORCE_TOLERANCE_N)
    parser.add_argument("--distance-tolerance-m", type=float, default=DEFAULT_DISTANCE_TOLERANCE_M)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "calibrated_overlay_force_response_after_v149" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    command = ["python3", "scripts/audit_calibrated_overlay_force_response_after_v149.py", "--run-id", run_id]
    payload = build_payload(
        config_path=resolve(args.config),
        previous_metrics_path=resolve(args.previous_metrics),
        run_id=run_id,
        ladder_m=[float(v) for v in args.ladder_m],
        force_tolerance_N=float(args.force_tolerance_N),
        distance_tolerance_m=float(args.distance_tolerance_m),
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
