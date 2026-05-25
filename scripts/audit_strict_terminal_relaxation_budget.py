#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import pathlib
import subprocess
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

DEFAULT_STRICT_TERMINAL = "runs/strict_terminal_constrained_optimization/20260525T085000/metrics.yaml"
DEFAULT_TRADEOFF_BOUNDARY = "runs/strict_terminal_tradeoff_boundary/20260525T104000/metrics.yaml"
DEFAULT_CALIBRATION_MARGIN = "runs/contact_orientation_calibration_margin/20260524T235723/metrics.yaml"
DEFAULT_REMAINING_BLOCKERS = "runs/remaining_blocker_prioritization/20260525T072557/metrics.yaml"

SCALAR_CRITERIA = ["force_error_N", "tangential_error_m", "orientation_error_rad"]


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


def scalar_ratios(row: dict[str, Any]) -> dict[str, float]:
    return {name: float(row.get("terminal_ratios", {}).get(name, math.inf)) for name in SCALAR_CRITERIA}


def scalar_actuals(row: dict[str, Any]) -> dict[str, float]:
    metrics = row.get("terminal_metrics", {})
    return {name: float(metrics.get(name, math.inf)) for name in SCALAR_CRITERIA}


def scalar_thresholds(row: dict[str, Any]) -> dict[str, float]:
    criteria = row.get("strict_terminal_gate", {}).get("criteria", {})
    return {
        name: float(criteria.get(name, {}).get("threshold", math.nan))
        for name in SCALAR_CRITERIA
    }


def contact_passed(row: dict[str, Any]) -> bool:
    criteria = row.get("strict_terminal_gate", {}).get("criteria", {})
    return bool(criteria.get("target_contact_count", {}).get("passed"))


def joint_limit_passed(row: dict[str, Any]) -> bool:
    criteria = row.get("strict_terminal_gate", {}).get("criteria", {})
    return bool(criteria.get("joint_limit_violation_rad", {}).get("passed"))


def eligible_for_scalar_relaxation(row: dict[str, Any]) -> bool:
    return contact_passed(row) and joint_limit_passed(row)


def required_multipliers(row: dict[str, Any]) -> dict[str, float]:
    return {name: max(1.0, ratio) for name, ratio in scalar_ratios(row).items()}


def required_increases(row: dict[str, Any]) -> dict[str, float]:
    actuals = scalar_actuals(row)
    thresholds = scalar_thresholds(row)
    increases: dict[str, float] = {}
    for name in SCALAR_CRITERIA:
        threshold = thresholds[name]
        actual = actuals[name]
        increases[name] = max(0.0, actual - threshold)
    return increases


def failed_scalar_criteria(row: dict[str, Any]) -> list[str]:
    return [name for name, ratio in scalar_ratios(row).items() if ratio > 1.0]


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    multipliers = required_multipliers(row)
    return {
        "case_id": row.get("case_id"),
        "eligible_for_scalar_relaxation": eligible_for_scalar_relaxation(row),
        "target_contact_passed": contact_passed(row),
        "joint_limit_passed": joint_limit_passed(row),
        "strict_passed": row.get("strict_terminal_gate", {}).get("passed"),
        "failed_scalar_criteria": failed_scalar_criteria(row),
        "required_uniform_multiplier": max(multipliers.values()),
        "required_multipliers": multipliers,
        "required_increases": required_increases(row),
        "actuals": scalar_actuals(row),
        "thresholds": scalar_thresholds(row),
    }


def best_by(rows: list[dict[str, Any]], key: Any) -> dict[str, Any] | None:
    if not rows:
        return None
    return min(rows, key=key)


def build_payload(
    *,
    strict_terminal_path: pathlib.Path,
    tradeoff_boundary_path: pathlib.Path,
    calibration_margin_path: pathlib.Path,
    remaining_blockers_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    for path in [
        strict_terminal_path,
        tradeoff_boundary_path,
        calibration_margin_path,
        remaining_blockers_path,
    ]:
        if not path.exists():
            violations.append(f"missing required source file: {rel(path)}")

    strict = load_yaml(strict_terminal_path) if strict_terminal_path.exists() else {}
    tradeoff = load_yaml(tradeoff_boundary_path) if tradeoff_boundary_path.exists() else {}
    calibration = load_yaml(calibration_margin_path) if calibration_margin_path.exists() else {}
    remaining = load_yaml(remaining_blockers_path) if remaining_blockers_path.exists() else {}
    rows = strict.get("optimization_rows", [])
    eligible_rows = [row for row in rows if eligible_for_scalar_relaxation(row)]
    strict_pass_rows = [row for row in rows if row.get("strict_terminal_gate", {}).get("passed")]

    if not rows:
        violations.append("strict terminal source rows are missing")
    if not eligible_rows:
        violations.append("no contact/joint-limit eligible rows exist for scalar relaxation budgeting")

    best_uniform = best_by(
        eligible_rows,
        lambda row: compact_row(row)["required_uniform_multiplier"],
    )
    single_relaxation_rows = [
        row for row in eligible_rows if len(failed_scalar_criteria(row)) == 1
    ]
    best_single_relaxation = best_by(
        single_relaxation_rows,
        lambda row: compact_row(row)["required_uniform_multiplier"],
    )
    best_orientation_only = best_by(
        [row for row in single_relaxation_rows if failed_scalar_criteria(row) == ["orientation_error_rad"]],
        lambda row: compact_row(row)["required_uniform_multiplier"],
    )
    contactless_xy_orientation = [
        row
        for row in rows
        if not contact_passed(row)
        and scalar_ratios(row)["tangential_error_m"] <= 1.0
        and scalar_ratios(row)["orientation_error_rad"] <= 1.0
    ]

    best_uniform_row = compact_row(best_uniform) if best_uniform else None
    best_single_row = compact_row(best_single_relaxation) if best_single_relaxation else None
    best_orientation_only_row = compact_row(best_orientation_only) if best_orientation_only else None
    strict_orientation_increase = (
        best_uniform_row["required_increases"]["orientation_error_rad"]
        if best_uniform_row
        else None
    )
    diagnostic_required_rotation = calibration.get("equivalent_corrections", {}).get(
        "required_normal_rotation_rad"
    )
    strict_to_diagnostic_orientation_margin_ratio = (
        float(strict_orientation_increase) / float(diagnostic_required_rotation)
        if strict_orientation_increase is not None and diagnostic_required_rotation
        else None
    )

    if strict_pass_rows:
        violations.append("strict terminal pass rows are present")
    if not best_uniform_row or best_uniform_row["required_uniform_multiplier"] <= 1.0:
        violations.append("minimum scalar relaxation budget does not preserve strict failure")
    if best_uniform_row and set(best_uniform_row["failed_scalar_criteria"]) != set(SCALAR_CRITERIA):
        violations.append("best uniform relaxation row no longer requires all three scalar gates")
    if not best_orientation_only_row:
        violations.append("no orientation-only scalar relaxation row exists")
    if not contactless_xy_orientation:
        violations.append("no contactless xy+orientation counterexample exists")
    if tradeoff.get("summary", {}).get("tradeoff_boundary_preserved") is not True:
        violations.append("v125 tradeoff boundary source is not preserved")
    if calibration.get("calibration_scale_interpretation", {}).get(
        "accepted_measurement_noise_budget_exists"
    ) is not False:
        violations.append("calibration margin source now reports an accepted measurement budget")
    if remaining.get("summary", {}).get("overall_goal_complete") is not False:
        violations.append("remaining blocker source no longer reports incomplete goal")

    relaxation_budget_acceptance_allowed = False
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "optimization_case_count": len(rows),
        "eligible_scalar_relaxation_row_count": len(eligible_rows),
        "strict_terminal_pass_count": len(strict_pass_rows),
        "minimum_uniform_multiplier": (
            best_uniform_row["required_uniform_multiplier"] if best_uniform_row else None
        ),
        "minimum_uniform_case_id": best_uniform_row["case_id"] if best_uniform_row else None,
        "minimum_uniform_requires_all_three_scalar_gates": (
            set(best_uniform_row["failed_scalar_criteria"]) == set(SCALAR_CRITERIA)
            if best_uniform_row
            else False
        ),
        "single_scalar_relaxation_row_count": len(single_relaxation_rows),
        "best_single_scalar_relaxation_case_id": (
            best_single_row["case_id"] if best_single_row else None
        ),
        "best_single_scalar_relaxation_multiplier": (
            best_single_row["required_uniform_multiplier"] if best_single_row else None
        ),
        "orientation_only_relaxation_case_id": (
            best_orientation_only_row["case_id"] if best_orientation_only_row else None
        ),
        "orientation_only_multiplier": (
            best_orientation_only_row["required_uniform_multiplier"]
            if best_orientation_only_row
            else None
        ),
        "contactless_xy_orientation_row_count": len(contactless_xy_orientation),
        "strict_orientation_increase_rad": strict_orientation_increase,
        "diagnostic_required_normal_rotation_rad": diagnostic_required_rotation,
        "strict_to_diagnostic_orientation_margin_ratio": strict_to_diagnostic_orientation_margin_ratio,
        "relaxation_budget_acceptance_allowed": relaxation_budget_acceptance_allowed,
        "new_optimization_run": False,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    return {
        "run_source": "strict terminal relaxation budget audit",
        "audit_run_id": run_id,
        "source_files": {
            "strict_terminal_constrained_optimization": rel(strict_terminal_path),
            "strict_terminal_tradeoff_boundary": rel(tradeoff_boundary_path),
            "contact_orientation_calibration_margin": rel(calibration_margin_path),
            "remaining_blocker_prioritization": rel(remaining_blockers_path),
        },
        "summary": summary,
        "best_uniform_relaxation_row": best_uniform_row,
        "best_single_scalar_relaxation_row": best_single_row,
        "orientation_only_relaxation_row": best_orientation_only_row,
        "contactless_xy_orientation_rows": [compact_row(row) for row in contactless_xy_orientation],
        "strict_terminal_thresholds": strict.get("strict_terminal_thresholds", {}),
        "v125_tradeoff_context": {
            "tradeoff_boundary_preserved": tradeoff.get("summary", {}).get(
                "tradeoff_boundary_preserved"
            ),
            "best_combined_failed_all_three_scalar_gates": tradeoff.get("summary", {}).get(
                "best_combined_failed_all_three_scalar_gates"
            ),
        },
        "v85_calibration_context": {
            "accepted_measurement_noise_budget_exists": calibration.get(
                "calibration_scale_interpretation", {}
            ).get("accepted_measurement_noise_budget_exists"),
            "required_normal_rotation_rad": diagnostic_required_rotation,
            "continuous_required_gate_rad": calibration.get("equivalent_corrections", {}).get(
                "continuous_required_gate_rad"
            ),
        },
        "claim_boundary": {
            "post_hoc_existing_rows_only": True,
            "new_optimization_run": False,
            "relaxation_budget_acceptance_allowed": relaxation_budget_acceptance_allowed,
            "strict_terminal_relaxation_accepted": False,
            "strict_paper_equivalent_feasibility": False,
            "canonical_controller_change": False,
            "canonical_orientation_gate_change": False,
            "failed_cell_closed": False,
            "robustness_claim": False,
            "contact_calibration_claim": False,
            "hardware_readiness": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "do_not_mark_goal_complete": True,
        },
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    uniform = payload["best_uniform_relaxation_row"] or {}
    orientation_only = payload["orientation_only_relaxation_row"] or {}
    lines = [
        "# Strict Terminal Relaxation Budget Audit",
        "",
        f"Run id: `{payload['audit_run_id']}`",
        "",
        f"Audit passed: `{summary['audit_passed']}`",
        f"Strict terminal pass count: `{summary['strict_terminal_pass_count']}`",
        f"Minimum uniform multiplier: `{summary['minimum_uniform_multiplier']}`",
        f"Minimum uniform case: `{summary['minimum_uniform_case_id']}`",
        f"Minimum uniform requires all three scalar gates: `{summary['minimum_uniform_requires_all_three_scalar_gates']}`",
        f"Best single-scalar multiplier: `{summary['best_single_scalar_relaxation_multiplier']}`",
        f"Orientation-only case: `{summary['orientation_only_relaxation_case_id']}`",
        f"Contactless xy+orientation rows: `{summary['contactless_xy_orientation_row_count']}`",
        f"Relaxation acceptance allowed: `{summary['relaxation_budget_acceptance_allowed']}`",
        f"Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "Minimum uniform relaxation row:",
        "",
        "| Criterion | Multiplier | Increase |",
        "| --- | ---: | ---: |",
    ]
    for criterion in SCALAR_CRITERIA:
        multipliers = uniform.get("required_multipliers", {})
        increases = uniform.get("required_increases", {})
        lines.append(f"| `{criterion}` | `{multipliers.get(criterion)}` | `{increases.get(criterion)}` |")
    lines.extend(
        [
            "",
            "Best single-scalar relaxation row:",
            "",
            f"- Case: `{orientation_only.get('case_id')}`",
            f"- Failed scalar criteria: `{orientation_only.get('failed_scalar_criteria')}`",
            f"- Required multipliers: `{orientation_only.get('required_multipliers')}`",
            "",
            "Scale comparison:",
            "",
            f"- Strict orientation increase: `{summary['strict_orientation_increase_rad']}`",
            f"- V85 diagnostic required normal rotation: `{summary['diagnostic_required_normal_rotation_rad']}`",
            f"- Ratio: `{summary['strict_to_diagnostic_orientation_margin_ratio']}`",
            "",
            "Violations:",
            "",
        ]
    )
    if summary["violations"]:
        lines.extend(f"- {violation}" for violation in summary["violations"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            (
                "The existing strict-terminal rows would require substantial "
                "non-accepted scalar gate relaxation. The smallest uniform budget "
                "still scales force, x/y, and orientation together, while the "
                "single-scalar recovery path needs a much larger orientation "
                "relaxation. This audit accepts no relaxation and creates no "
                "strict feasibility evidence."
            ),
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--strict-terminal-path", default=DEFAULT_STRICT_TERMINAL)
    parser.add_argument("--tradeoff-boundary-path", default=DEFAULT_TRADEOFF_BOUNDARY)
    parser.add_argument("--calibration-margin-path", default=DEFAULT_CALIBRATION_MARGIN)
    parser.add_argument("--remaining-blockers-path", default=DEFAULT_REMAINING_BLOCKERS)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "strict_terminal_relaxation_budget" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(
        strict_terminal_path=resolve(args.strict_terminal_path),
        tradeoff_boundary_path=resolve(args.tradeoff_boundary_path),
        calibration_margin_path=resolve(args.calibration_margin_path),
        remaining_blockers_path=resolve(args.remaining_blockers_path),
        run_id=run_id,
    )
    payload["audit_root"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0 if payload["summary"]["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
