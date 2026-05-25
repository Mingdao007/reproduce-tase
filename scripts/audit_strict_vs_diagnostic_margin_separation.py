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

DEFAULT_CALIBRATION_MARGIN = (
    "runs/contact_orientation_calibration_margin/20260524T235723/metrics.yaml"
)
DEFAULT_RELAXATION_BUDGET = (
    "runs/strict_terminal_relaxation_budget/20260525T105000/metrics.yaml"
)
DEFAULT_COMPLETION_GATE = "runs/post_v135_completion_gate/20260525T123000/metrics.yaml"
MIN_EXPECTED_SCALE_SEPARATION = 10.0


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


def nested_get(payload: dict[str, Any], path: list[str], default: Any = None) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


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


def finite_positive(value: Any, *, label: str, violations: list[str]) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        violations.append(f"{label} is not numeric")
        return math.nan
    if not math.isfinite(number) or number <= 0.0:
        violations.append(f"{label} must be finite and positive")
    return number


def validate_calibration_margin(metrics: dict[str, Any], violations: list[str]) -> None:
    if metrics.get("run_source") != "v85 contact orientation calibration margin":
        violations.append("v85 calibration margin source changed")
    if nested_get(metrics, ["calibration_scale_interpretation", "accepted_measurement_noise_budget_exists"]) is not False:
        violations.append("v85 accepted_measurement_noise_budget_exists is not false")
    for gate_id, option in metrics.get("gate_options", {}).items():
        if option.get("accepted_as_replacement_gate") is not False:
            violations.append(f"v85 gate option {gate_id} is accepted as replacement")
        if option.get("replacement_gate_justified_by_existing_metrics") is not False:
            violations.append(f"v85 gate option {gate_id} is justified by existing metrics")


def validate_relaxation_budget(metrics: dict[str, Any], violations: list[str]) -> None:
    summary = metrics.get("summary", {})
    expected = {
        "audit_passed": True,
        "strict_terminal_pass_count": 0,
        "minimum_uniform_requires_all_three_scalar_gates": True,
        "relaxation_budget_acceptance_allowed": False,
        "new_optimization_run": False,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            violations.append(f"v126 summary {key} is {summary.get(key)!r}, expected {value!r}")
    boundary = metrics.get("claim_boundary", {})
    for key in [
        "strict_terminal_relaxation_accepted",
        "strict_paper_equivalent_feasibility",
        "canonical_orientation_gate_change",
        "contact_calibration_claim",
        "hardware_readiness",
    ]:
        if boundary.get(key) is not False:
            violations.append(f"v126 claim_boundary.{key} is not false")


def validate_completion_gate(metrics: dict[str, Any], violations: list[str]) -> None:
    summary = metrics.get("summary", {})
    expected = {
        "audit_passed": True,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
        "top_blocker": "approved_read_only_calibration_evidence",
        "approved_read_only_run_count": 0,
        "approved_read_only_audit_passed_count": 0,
        "strict_terminal_pass_count": 0,
        "readiness_artifacts_are_non_evidence": True,
        "finalization_rehearsal_is_non_evidence": True,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            violations.append(f"v136 summary {key} is {summary.get(key)!r}, expected {value!r}")


def build_payload(
    *,
    calibration_margin_path: pathlib.Path,
    relaxation_budget_path: pathlib.Path,
    completion_gate_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    if not calibration_margin_path.exists():
        violations.append(f"missing calibration margin metrics: {rel(calibration_margin_path)}")
        calibration: dict[str, Any] = {}
    else:
        calibration = load_yaml(calibration_margin_path)
        validate_calibration_margin(calibration, violations)
    if not relaxation_budget_path.exists():
        violations.append(f"missing relaxation budget metrics: {rel(relaxation_budget_path)}")
        relaxation: dict[str, Any] = {}
    else:
        relaxation = load_yaml(relaxation_budget_path)
        validate_relaxation_budget(relaxation, violations)
    if not completion_gate_path.exists():
        violations.append(f"missing completion gate metrics: {rel(completion_gate_path)}")
        completion_gate: dict[str, Any] = {}
    else:
        completion_gate = load_yaml(completion_gate_path)
        validate_completion_gate(completion_gate, violations)

    diagnostic_rotation = finite_positive(
        nested_get(calibration, ["equivalent_corrections", "required_normal_rotation_rad"]),
        label="v85 equivalent_corrections.required_normal_rotation_rad",
        violations=violations,
    )
    strict_orientation_increase = finite_positive(
        nested_get(relaxation, ["summary", "strict_orientation_increase_rad"]),
        label="v126 summary.strict_orientation_increase_rad",
        violations=violations,
    )
    strict_tangential_increase = finite_positive(
        nested_get(
            relaxation,
            ["best_uniform_relaxation_row", "required_increases", "tangential_error_m"],
        ),
        label="v126 best_uniform_relaxation_row.required_increases.tangential_error_m",
        violations=violations,
    )
    strict_force_increase = finite_positive(
        nested_get(relaxation, ["best_uniform_relaxation_row", "required_increases", "force_error_N"]),
        label="v126 best_uniform_relaxation_row.required_increases.force_error_N",
        violations=violations,
    )
    strict_to_diagnostic_ratio = (
        strict_orientation_increase / diagnostic_rotation
        if diagnostic_rotation and math.isfinite(diagnostic_rotation)
        else math.nan
    )
    v126_reported_ratio = nested_get(
        relaxation, ["summary", "strict_to_diagnostic_orientation_margin_ratio"]
    )
    if math.isfinite(strict_to_diagnostic_ratio) and v126_reported_ratio is not None:
        if abs(strict_to_diagnostic_ratio - float(v126_reported_ratio)) > 1.0e-9:
            violations.append("computed strict-to-diagnostic ratio does not match v126 summary")
    if not math.isfinite(strict_to_diagnostic_ratio) or strict_to_diagnostic_ratio < MIN_EXPECTED_SCALE_SEPARATION:
        violations.append(
            f"strict-to-diagnostic orientation ratio {strict_to_diagnostic_ratio!r} "
            f"is below {MIN_EXPECTED_SCALE_SEPARATION}"
        )

    v85_margin_can_close_strict_orientation = (
        math.isfinite(diagnostic_rotation)
        and math.isfinite(strict_orientation_increase)
        and diagnostic_rotation >= strict_orientation_increase
    )
    v85_margin_can_close_strict_uniform_relaxation = (
        v85_margin_can_close_strict_orientation
        and strict_force_increase <= 0.0
        and strict_tangential_increase <= 0.0
    )
    if v85_margin_can_close_strict_orientation:
        violations.append("v85 diagnostic margin is large enough to close strict orientation")
    if v85_margin_can_close_strict_uniform_relaxation:
        violations.append("v85 diagnostic margin is enough to close strict uniform relaxation")

    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "strict_vs_diagnostic_margin_separation_complete": not violations,
        "source_calibration_margin_present": bool(calibration),
        "source_relaxation_budget_audit_passed": nested_get(relaxation, ["summary", "audit_passed"]),
        "source_completion_gate_audit_passed": nested_get(completion_gate, ["summary", "audit_passed"]),
        "diagnostic_required_normal_rotation_rad": diagnostic_rotation,
        "diagnostic_required_normal_rotation_deg": nested_get(
            calibration, ["equivalent_corrections", "required_normal_rotation_deg"]
        ),
        "strict_orientation_increase_rad": strict_orientation_increase,
        "strict_tangential_increase_m": strict_tangential_increase,
        "strict_force_increase_N": strict_force_increase,
        "strict_to_diagnostic_orientation_margin_ratio": strict_to_diagnostic_ratio,
        "minimum_uniform_multiplier": nested_get(relaxation, ["summary", "minimum_uniform_multiplier"]),
        "minimum_uniform_case_id": nested_get(relaxation, ["summary", "minimum_uniform_case_id"]),
        "minimum_uniform_requires_all_three_scalar_gates": nested_get(
            relaxation, ["summary", "minimum_uniform_requires_all_three_scalar_gates"]
        ),
        "v85_margin_can_close_strict_orientation": v85_margin_can_close_strict_orientation,
        "v85_margin_can_close_strict_uniform_relaxation": v85_margin_can_close_strict_uniform_relaxation,
        "v85_margin_can_close_strict_paper_equivalent_goal": False,
        "diagnostic_margin_is_strictly_smaller_than_strict_orientation_gap": (
            not v85_margin_can_close_strict_orientation
        ),
        "accepted_measurement_noise_budget_exists": nested_get(
            calibration, ["calibration_scale_interpretation", "accepted_measurement_noise_budget_exists"]
        ),
        "replacement_gate_accepted": any(
            option.get("accepted_as_replacement_gate") is True
            for option in calibration.get("gate_options", {}).values()
        ),
        "read_only_evidence_required_for_calibration": True,
        "approved_read_only_run_count": nested_get(
            completion_gate, ["summary", "approved_read_only_run_count"]
        ),
        "approved_read_only_audit_passed_count": nested_get(
            completion_gate, ["summary", "approved_read_only_audit_passed_count"]
        ),
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    return {
        "run_source": "strict versus diagnostic margin separation audit",
        "audit_run_id": run_id,
        "source_files": {
            "contact_orientation_calibration_margin": rel(calibration_margin_path),
            "strict_terminal_relaxation_budget": rel(relaxation_budget_path),
            "post_v135_completion_gate": rel(completion_gate_path),
        },
        "summary": summary,
        "comparison": {
            "diagnostic_context": {
                "source": "v85 contact orientation calibration margin",
                "hardest_row": calibration.get("hardest_row"),
                "required_normal_rotation_rad": diagnostic_rotation,
                "required_gate_increase_rad": nested_get(
                    calibration, ["equivalent_corrections", "required_gate_increase_rad"]
                ),
                "equivalent_base_z_or_contact_point_um": nested_get(
                    calibration, ["equivalent_corrections", "equivalent_base_z_or_contact_point_um"]
                ),
                "accepted_measurement_noise_budget_exists": nested_get(
                    calibration,
                    ["calibration_scale_interpretation", "accepted_measurement_noise_budget_exists"],
                ),
            },
            "strict_context": {
                "source": "v126 strict terminal relaxation budget",
                "strict_terminal_pass_count": nested_get(
                    relaxation, ["summary", "strict_terminal_pass_count"]
                ),
                "minimum_uniform_case_id": nested_get(
                    relaxation, ["summary", "minimum_uniform_case_id"]
                ),
                "minimum_uniform_multiplier": nested_get(
                    relaxation, ["summary", "minimum_uniform_multiplier"]
                ),
                "failed_scalar_criteria": nested_get(
                    relaxation,
                    ["best_uniform_relaxation_row", "failed_scalar_criteria"],
                    [],
                ),
                "required_increases": nested_get(
                    relaxation, ["best_uniform_relaxation_row", "required_increases"], {}
                ),
            },
            "scale_separation": {
                "ratio": strict_to_diagnostic_ratio,
                "minimum_expected_ratio": MIN_EXPECTED_SCALE_SEPARATION,
                "strict_gap_exceeds_diagnostic_margin": (
                    not v85_margin_can_close_strict_orientation
                ),
                "strict_gap_also_requires_force_and_tangential_relaxation": (
                    strict_force_increase > 0.0 and strict_tangential_increase > 0.0
                ),
            },
        },
        "claim_boundary": {
            "post_hoc_existing_metrics_only": True,
            "new_optimization_run": False,
            "diagnostic_margin_only": True,
            "strict_terminal_relaxation_accepted": False,
            "strict_paper_equivalent_feasibility": False,
            "canonical_orientation_gate_change": False,
            "contact_calibration_claim": False,
            "robustness_claim": False,
            "hardware_readiness": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "do_not_mark_goal_complete": True,
        },
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Strict vs Diagnostic Margin Separation Audit",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Separation complete: `{summary['strict_vs_diagnostic_margin_separation_complete']}`",
        f"- Diagnostic required normal rotation rad: `{summary['diagnostic_required_normal_rotation_rad']}`",
        f"- Strict orientation increase rad: `{summary['strict_orientation_increase_rad']}`",
        f"- Strict/diagnostic orientation ratio: `{summary['strict_to_diagnostic_orientation_margin_ratio']}`",
        f"- Minimum uniform multiplier: `{summary['minimum_uniform_multiplier']}`",
        f"- Minimum uniform requires all three scalar gates: `{summary['minimum_uniform_requires_all_three_scalar_gates']}`",
        f"- V85 margin can close strict orientation: `{summary['v85_margin_can_close_strict_orientation']}`",
        f"- V85 margin can close strict paper-equivalent goal: `{summary['v85_margin_can_close_strict_paper_equivalent_goal']}`",
        f"- Completion claim allowed: `{summary['completion_claim_allowed']}`",
        f"- Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "## Violations",
        "",
    ]
    if summary["violations"]:
        lines.extend(f"- {violation}" for violation in summary["violations"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The v85 diagnostic margin is a small orientation/contact definition "
                "margin for the weighted diagnostic row. It is not large enough to "
                "close the v126 strict-terminal orientation gap, and the strict best "
                "uniform row also needs force and tangential relaxation. This audit "
                "therefore keeps the diagnostic calibration path separate from any "
                "strict paper-equivalent feasibility claim."
            ),
            "",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--calibration-margin-path", default=DEFAULT_CALIBRATION_MARGIN)
    parser.add_argument("--relaxation-budget-path", default=DEFAULT_RELAXATION_BUDGET)
    parser.add_argument("--completion-gate-path", default=DEFAULT_COMPLETION_GATE)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "strict_vs_diagnostic_margin_separation" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        calibration_margin_path=resolve(args.calibration_margin_path),
        relaxation_budget_path=resolve(args.relaxation_budget_path),
        completion_gate_path=resolve(args.completion_gate_path),
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
