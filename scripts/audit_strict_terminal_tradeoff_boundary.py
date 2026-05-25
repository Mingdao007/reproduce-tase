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
DEFAULT_REMAINING_BLOCKERS = "runs/remaining_blocker_prioritization/20260525T072557/metrics.yaml"
DEFAULT_CLAIM_BOUNDARY = "runs/paper_platform_claim_boundary/20260525T103000/metrics.yaml"

CRITERIA = ["force_error_N", "tangential_error_m", "orientation_error_rad"]


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


def criterion_ratio(row: dict[str, Any], criterion: str) -> float:
    value = row.get("terminal_ratios", {}).get(criterion)
    if value is None:
        return math.inf
    return float(value)


def ratio_vector(row: dict[str, Any]) -> list[float]:
    return [criterion_ratio(row, criterion) for criterion in CRITERIA]


def row_contact_passed(row: dict[str, Any]) -> bool:
    criteria = row.get("strict_terminal_gate", {}).get("criteria", {})
    return bool(criteria.get("target_contact_count", {}).get("passed"))


def row_joint_limit_passed(row: dict[str, Any]) -> bool:
    criteria = row.get("strict_terminal_gate", {}).get("criteria", {})
    return bool(criteria.get("joint_limit_violation_rad", {}).get("passed"))


def row_passes(row: dict[str, Any], criterion: str) -> bool:
    criteria = row.get("strict_terminal_gate", {}).get("criteria", {})
    return bool(criteria.get(criterion, {}).get("passed"))


def finite_max_gate_ratio(row: dict[str, Any]) -> float:
    value = row.get("strict_terminal_gate", {}).get("max_gate_ratio")
    if value is None:
        return math.inf
    return float(value)


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    metrics = row.get("terminal_metrics", {})
    gate = row.get("strict_terminal_gate", {})
    return {
        "case_id": row.get("case_id"),
        "optimizer_success": row.get("optimizer", {}).get("success"),
        "target_contact_passed": row_contact_passed(row),
        "joint_limit_passed": row_joint_limit_passed(row),
        "passed": gate.get("passed"),
        "failed_criteria": gate.get("failed_criteria", []),
        "max_gate_ratio": gate.get("max_gate_ratio"),
        "ratios": {criterion: criterion_ratio(row, criterion) for criterion in CRITERIA},
        "metrics": {
            "force_error_N": metrics.get("force_error_N"),
            "tangential_error_m": metrics.get("tangential_error_m"),
            "orientation_error_rad": metrics.get("orientation_error_rad"),
            "target_contact_count": metrics.get("target_contact_count"),
        },
    }


def dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_vec = ratio_vector(left)
    right_vec = ratio_vector(right)
    return all(a <= b for a, b in zip(left_vec, right_vec)) and any(
        a < b for a, b in zip(left_vec, right_vec)
    )


def pareto_frontier(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frontier = []
    for row in rows:
        if not any(other is not row and dominates(other, row) for other in rows):
            frontier.append(row)
    return sorted(frontier, key=lambda row: (finite_max_gate_ratio(row), str(row.get("case_id"))))


def best_row(rows: list[dict[str, Any]], key: Any) -> dict[str, Any]:
    return min(rows, key=key)


def tradeoff_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    force_xy_without_orientation = [
        row
        for row in rows
        if row_contact_passed(row)
        and row_joint_limit_passed(row)
        and row_passes(row, "force_error_N")
        and row_passes(row, "tangential_error_m")
        and not row_passes(row, "orientation_error_rad")
    ]
    xy_orientation_without_force_or_contact = [
        row
        for row in rows
        if row_joint_limit_passed(row)
        and row_passes(row, "tangential_error_m")
        and row_passes(row, "orientation_error_rad")
        and (not row_passes(row, "force_error_N") or not row_contact_passed(row))
    ]
    return {
        "force_xy_without_orientation_count": len(force_xy_without_orientation),
        "force_xy_without_orientation_best": (
            compact_row(best_row(force_xy_without_orientation, lambda row: criterion_ratio(row, "orientation_error_rad")))
            if force_xy_without_orientation
            else None
        ),
        "xy_orientation_without_force_or_contact_count": len(xy_orientation_without_force_or_contact),
        "xy_orientation_without_force_or_contact_best": (
            compact_row(best_row(xy_orientation_without_force_or_contact, lambda row: criterion_ratio(row, "force_error_N")))
            if xy_orientation_without_force_or_contact
            else None
        ),
    }


def build_payload(
    *,
    strict_terminal_path: pathlib.Path,
    remaining_blockers_path: pathlib.Path,
    claim_boundary_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    for path in [strict_terminal_path, remaining_blockers_path, claim_boundary_path]:
        if not path.exists():
            violations.append(f"missing required source file: {rel(path)}")

    strict = load_yaml(strict_terminal_path) if strict_terminal_path.exists() else {}
    remaining = load_yaml(remaining_blockers_path) if remaining_blockers_path.exists() else {}
    claim_boundary = load_yaml(claim_boundary_path) if claim_boundary_path.exists() else {}
    rows = strict.get("optimization_rows", [])

    strict_pass_rows = [row for row in rows if row.get("strict_terminal_gate", {}).get("passed")]
    contact_rows = [row for row in rows if row_contact_passed(row)]
    finite_rows = [row for row in rows if math.isfinite(finite_max_gate_ratio(row))]
    rows_for_best = finite_rows or rows

    if not rows:
        violations.append("strict terminal optimization rows are missing")
        rows_for_best = []

    best_combined = best_row(rows_for_best, finite_max_gate_ratio) if rows_for_best else {}
    single_best_rows = {
        criterion: compact_row(best_row(rows, lambda row, name=criterion: criterion_ratio(row, name)))
        for criterion in CRITERIA
    } if rows else {}
    frontier = [compact_row(row) for row in pareto_frontier(rows)] if rows else []
    tradeoffs = tradeoff_rows(rows) if rows else {
        "force_xy_without_orientation_count": 0,
        "force_xy_without_orientation_best": None,
        "xy_orientation_without_force_or_contact_count": 0,
        "xy_orientation_without_force_or_contact_best": None,
    }
    best_combined_row = compact_row(best_combined) if best_combined else {}

    best_combined_failed_all_three = all(
        criterion in best_combined_row.get("failed_criteria", []) for criterion in CRITERIA
    )
    no_strict_pass = len(strict_pass_rows) == 0
    force_xy_tradeoff_present = tradeoffs["force_xy_without_orientation_count"] > 0
    xy_orientation_tradeoff_present = tradeoffs["xy_orientation_without_force_or_contact_count"] > 0
    v116_still_incomplete = strict.get("summary", {}).get(
        "strict_terminal_constrained_optimization_complete"
    ) is False
    completion_context_incomplete = remaining.get("summary", {}).get("overall_goal_complete") is False
    paper_boundary_incomplete = claim_boundary.get("summary", {}).get(
        "strict_paper_equivalent_claim_allowed"
    ) is False

    if not no_strict_pass:
        violations.append("strict terminal pass rows are present")
    if not best_combined_failed_all_three:
        violations.append("best combined row no longer fails all three scalar strict gates")
    if not force_xy_tradeoff_present:
        violations.append("no force+xy/contact row isolates orientation as the remaining failure")
    if not xy_orientation_tradeoff_present:
        violations.append("no xy+orientation row isolates force/contact as the remaining failure")
    if not v116_still_incomplete:
        violations.append("v116 strict terminal source no longer reports incomplete optimization")
    if not completion_context_incomplete:
        violations.append("remaining blocker context no longer reports incomplete goal")
    if not paper_boundary_incomplete:
        violations.append("paper-platform claim boundary no longer blocks strict parity")

    tradeoff_boundary_preserved = (
        no_strict_pass
        and best_combined_failed_all_three
        and force_xy_tradeoff_present
        and xy_orientation_tradeoff_present
        and v116_still_incomplete
        and completion_context_incomplete
        and paper_boundary_incomplete
    )
    audit_passed = not violations
    summary = {
        "audit_passed": audit_passed,
        "violations": violations,
        "strict_terminal_pass_count": len(strict_pass_rows),
        "optimization_case_count": len(rows),
        "contact_row_count": len(contact_rows),
        "finite_max_gate_ratio_row_count": len(finite_rows),
        "best_combined_case_id": best_combined_row.get("case_id"),
        "best_combined_max_gate_ratio": best_combined_row.get("max_gate_ratio"),
        "best_combined_failed_all_three_scalar_gates": best_combined_failed_all_three,
        "pareto_frontier_count": len(frontier),
        "force_xy_without_orientation_count": tradeoffs["force_xy_without_orientation_count"],
        "xy_orientation_without_force_or_contact_count": tradeoffs[
            "xy_orientation_without_force_or_contact_count"
        ],
        "tradeoff_boundary_preserved": tradeoff_boundary_preserved,
        "new_optimization_run": False,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    return {
        "run_source": "strict terminal tradeoff boundary audit",
        "audit_run_id": run_id,
        "source_files": {
            "strict_terminal_constrained_optimization": rel(strict_terminal_path),
            "remaining_blocker_prioritization": rel(remaining_blockers_path),
            "paper_platform_claim_boundary": rel(claim_boundary_path),
        },
        "summary": summary,
        "strict_terminal_thresholds": strict.get("strict_terminal_thresholds", {}),
        "v116_summary": strict.get("summary", {}),
        "v112_context": {
            "top_priority_blocker_id": remaining.get("summary", {}).get("top_priority_blocker_id"),
            "offline_actionable_blocker_ids": remaining.get("summary", {}).get(
                "offline_actionable_blocker_ids", []
            ),
        },
        "v124_paper_platform_context": {
            "formula_convergence_claim_allowed": claim_boundary.get("summary", {}).get(
                "formula_convergence_claim_allowed"
            ),
            "tuned_figure_match_claim_allowed": claim_boundary.get("summary", {}).get(
                "tuned_figure_match_claim_allowed"
            ),
            "strict_paper_equivalent_claim_allowed": claim_boundary.get("summary", {}).get(
                "strict_paper_equivalent_claim_allowed"
            ),
            "claim_lines_collapsed": claim_boundary.get("summary", {}).get("claim_lines_collapsed"),
        },
        "best_combined_row": best_combined_row,
        "single_criterion_best_rows": single_best_rows,
        "tradeoff_rows": tradeoffs,
        "pareto_frontier_rows": frontier,
        "claim_boundary": {
            "post_hoc_existing_v116_rows_only": True,
            "new_optimization_run": False,
            "strict_terminal_tradeoff_closed": False,
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
    best = payload["best_combined_row"]
    tradeoffs = payload["tradeoff_rows"]
    lines = [
        "# Strict Terminal Tradeoff Boundary Audit",
        "",
        f"Run id: `{payload['audit_run_id']}`",
        "",
        f"Audit passed: `{summary['audit_passed']}`",
        f"Strict terminal pass count: `{summary['strict_terminal_pass_count']}`",
        f"Best combined row: `{summary['best_combined_case_id']}`",
        f"Best combined max-gate ratio: `{summary['best_combined_max_gate_ratio']}`",
        f"Best combined fails all three scalar gates: `{summary['best_combined_failed_all_three_scalar_gates']}`",
        f"Force+xy/contact without orientation rows: `{summary['force_xy_without_orientation_count']}`",
        f"Xy+orientation without force/contact rows: `{summary['xy_orientation_without_force_or_contact_count']}`",
        f"Tradeoff boundary preserved: `{summary['tradeoff_boundary_preserved']}`",
        f"New optimization run: `{summary['new_optimization_run']}`",
        f"Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "Best combined row ratios:",
        "",
        "| Criterion | Ratio |",
        "| --- | ---: |",
    ]
    for criterion, ratio in best.get("ratios", {}).items():
        lines.append(f"| `{criterion}` | `{ratio}` |")
    lines.extend(
        [
            "",
            "Tradeoff examples:",
            "",
            f"- Force+xy/contact without orientation: `{_case_id(tradeoffs['force_xy_without_orientation_best'])}`",
            f"- Xy+orientation without force/contact: `{_case_id(tradeoffs['xy_orientation_without_force_or_contact_best'])}`",
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
                "The existing v116 optimization rows show a strict terminal "
                "tradeoff rather than a hidden pass: force/xy can be recovered "
                "at the cost of orientation, while xy/orientation can be recovered "
                "only without the required force/contact. This audit is post-hoc "
                "bookkeeping over existing rows and does not close strict feasibility."
            ),
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _case_id(row: dict[str, Any] | None) -> str | None:
    if not row:
        return None
    return row.get("case_id")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--strict-terminal-path", default=DEFAULT_STRICT_TERMINAL)
    parser.add_argument("--remaining-blockers-path", default=DEFAULT_REMAINING_BLOCKERS)
    parser.add_argument("--claim-boundary-path", default=DEFAULT_CLAIM_BOUNDARY)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "strict_terminal_tradeoff_boundary" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(
        strict_terminal_path=resolve(args.strict_terminal_path),
        remaining_blockers_path=resolve(args.remaining_blockers_path),
        claim_boundary_path=resolve(args.claim_boundary_path),
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
