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

DEFAULT_PARITY_METRICS = "runs/paper_platform_parity_eval/20260524T124200/metrics.yaml"
DEFAULT_TUNED_METRICS = "runs/paper_7dof_section_v/20260524T134441/metrics.yaml"
DEFAULT_RAW_PROVENANCE = "runs/paper_7dof_fig6_raw_provenance/20260524T134549/metrics.yaml"
DEFAULT_SPLIT_REPORT = "reports/paper_platform_split_evidence_report.md"
DEFAULT_Q7_TOLERANCE_RAD = 0.05


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


def float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def close_to(value: Any, expected: float, *, tolerance: float = 1.0e-9) -> bool:
    actual = float_or_none(value)
    return actual is not None and abs(actual - expected) <= tolerance


def finite_close_to(value: Any, expected: float, *, tolerance: float = 1.0e-9) -> bool:
    actual = float_or_none(value)
    return actual is not None and math.isfinite(actual) and abs(actual - expected) <= tolerance


def check_formula_line(parity_result: dict[str, Any]) -> dict[str, Any]:
    checks = parity_result.get("checks", {})
    claim_results = parity_result.get("claim_results", {})
    formula_claim = claim_results.get("formula_convergence", {})
    fig6_check = checks.get("fig6_q7_22s_landmark", {})
    required_checks = formula_claim.get("required_checks", [])
    required_check_status = {
        name: bool(checks.get(name, {}).get("pass")) for name in required_checks
    }
    required_checks_pass = bool(required_checks) and all(required_check_status.values())
    formula_pass = parity_result.get("paper_platform_formula_convergence_pass") is True
    formula_fig6_landmark_pass = (
        parity_result.get("paper_platform_figure_match_landmark_pass") is True
        or fig6_check.get("pass") is True
    )
    allowed = formula_pass and required_checks_pass and not formula_fig6_landmark_pass
    return {
        "claim_id": "paper_platform_7dof_formula_convergence",
        "claim_allowed": allowed,
        "source_claim": formula_claim.get("claim"),
        "source_pass": formula_pass,
        "required_checks_pass": required_checks_pass,
        "required_check_status": required_check_status,
        "formula_candidate_fig6_landmark_pass": formula_fig6_landmark_pass,
        "fig6_q7_abs_delta_rad": fig6_check.get("abs_delta_rad"),
        "boundary": (
            "Formula-faithful Python candidate passes formula-convergence checks "
            "but does not claim Fig.6 q-trajectory parity."
        ),
    }


def expected_tuning_checks(tuned_metrics: dict[str, Any], tuned_config: dict[str, Any]) -> dict[str, bool]:
    return {
        "force_loop_mode_is_admittance_proxy": tuned_metrics.get("force_loop_mode")
        == "admittance_proxy",
        "orientation_mode_is_normal_only": tuned_metrics.get("orientation_mode") == "normal_only",
        "solver_mode_is_pinv_bounded": tuned_metrics.get("solver_mode") == "pinv_bounded",
        "escape_velocity_alpha_is_20": close_to(tuned_metrics.get("escape_velocity_alpha"), 20.0),
        "kp_is_25": close_to(tuned_metrics.get("kp"), 25.0),
        "q7_nullspace_speed_is_0p35": close_to(
            tuned_metrics.get("q7_nullspace_speed_rad_s"), 0.35
        ),
        "force_integral_limit_is_finite_5": finite_close_to(
            tuned_metrics.get("force_integral_limit", tuned_config.get("force_integral_limit")), 5.0
        ),
    }


def tuned_candidate_formula_like(tuned_metrics: dict[str, Any]) -> bool:
    q7_speed = float_or_none(tuned_metrics.get("q7_nullspace_speed_rad_s", 0.0))
    force_integral_limit = float_or_none(tuned_metrics.get("force_integral_limit"))
    return (
        tuned_metrics.get("force_loop_mode") == "paper_literal"
        and tuned_metrics.get("orientation_mode") == "force_shortest_arc"
        and tuned_metrics.get("solver_mode") == "kkt_projection"
        and force_integral_limit is not None
        and math.isinf(force_integral_limit)
        and (q7_speed is None or abs(q7_speed) <= 1.0e-12)
    )


def check_tuned_line(
    tuned_payload: dict[str, Any],
    raw_payload: dict[str, Any],
    *,
    q7_tolerance_rad: float,
) -> dict[str, Any]:
    tuned_metrics = tuned_payload.get("metrics", {})
    tuned_config = tuned_payload.get("config", {})
    raw_summary = raw_payload.get("summary", {})
    tuning_checks = expected_tuning_checks(tuned_metrics, tuned_config)

    q7_error = float_or_none(tuned_metrics.get("fig6_q7_abs_error_to_2p5_rad"))
    raw_delta_to_figure = float_or_none(raw_summary.get("python_abs_delta_to_figure_q7_at_22_s_rad"))
    raw_delta_to_formula = float_or_none(raw_summary.get("python_abs_delta_to_formula_q7_at_22_s_rad"))
    q7_landmark_pass = (
        q7_error is not None
        and q7_error <= q7_tolerance_rad
        and raw_delta_to_figure is not None
        and raw_delta_to_figure <= q7_tolerance_rad
    )
    raw_provenance_pass = (
        raw_summary.get("python_fk_matches_sampled_legacy_raw") is True
        and raw_summary.get("legacy_figure_force_loop_mode") == "admittance_proxy"
        and raw_summary.get("python_force_loop_mode") == "admittance_proxy"
    )
    execution_pass = (
        tuned_metrics.get("execution_success") is True
        and tuned_metrics.get("contact_force_tail_success") is True
        and int(tuned_metrics.get("q_bound_violation_count", -1)) == 0
        and int(tuned_metrics.get("qdot_bound_violation_count", -1)) == 0
        and float(tuned_metrics.get("duration_s", 0.0)) >= 30.0
    )
    non_paper_faithful = (
        all(tuning_checks.values())
        and raw_delta_to_formula is not None
        and raw_delta_to_formula > q7_tolerance_rad
    )
    allowed = execution_pass and q7_landmark_pass and raw_provenance_pass and non_paper_faithful
    return {
        "claim_id": "paper_platform_7dof_tuned_figure_match_candidate",
        "claim_allowed": allowed,
        "source_claim": tuned_metrics.get("claim_level"),
        "execution_pass": execution_pass,
        "q7_landmark_pass": q7_landmark_pass,
        "raw_provenance_pass": raw_provenance_pass,
        "non_paper_faithful_tuning_present": non_paper_faithful,
        "expected_tuning_checks": tuning_checks,
        "python_abs_delta_to_figure_q7_at_22_s_rad": raw_delta_to_figure,
        "python_abs_delta_to_formula_q7_at_22_s_rad": raw_delta_to_formula,
        "fig6_q7_abs_error_to_2p5_rad": q7_error,
        "formula_like": tuned_candidate_formula_like(tuned_metrics),
        "boundary": (
            "Separate tuned Python candidate matches the legacy Fig.6 q7 "
            "landmark with documented non-paper-faithful tuning."
        ),
    }


def check_strict_line(parity_result: dict[str, Any]) -> dict[str, Any]:
    strict_claim = parity_result.get("claim_results", {}).get("legacy_strict_all_checks", {})
    strict_pass = parity_result.get("paper_platform_parity_pass") is True
    required_checks = strict_claim.get("required_checks", parity_result.get("strict_required_checks", []))
    check_status = {
        name: bool(parity_result.get("checks", {}).get(name, {}).get("pass"))
        for name in required_checks
    }
    failed_checks = [name for name, passed in check_status.items() if not passed]
    return {
        "claim_id": "paper_platform_7dof_legacy_strict_all_checks",
        "claim_allowed": strict_pass,
        "source_claim": strict_claim.get("claim", parity_result.get("claim")),
        "source_pass": strict_pass,
        "failed_required_checks": failed_checks,
        "required_check_status": check_status,
        "boundary": (
            "Full paper-equivalent numerical parity remains unclaimed unless "
            "the strict aggregate is independently updated and accepted."
        ),
    }


def build_payload(
    *,
    parity_metrics_path: pathlib.Path,
    tuned_metrics_path: pathlib.Path,
    raw_provenance_path: pathlib.Path,
    split_report_path: pathlib.Path,
    run_id: str,
    q7_tolerance_rad: float = DEFAULT_Q7_TOLERANCE_RAD,
) -> dict[str, Any]:
    violations: list[str] = []
    for path in [parity_metrics_path, tuned_metrics_path, raw_provenance_path, split_report_path]:
        if not path.exists():
            violations.append(f"missing required source file: {rel(path)}")

    parity_payload = load_yaml(parity_metrics_path) if parity_metrics_path.exists() else {}
    tuned_payload = load_yaml(tuned_metrics_path) if tuned_metrics_path.exists() else {}
    raw_payload = load_yaml(raw_provenance_path) if raw_provenance_path.exists() else {}
    split_report_text = split_report_path.read_text(encoding="utf-8") if split_report_path.exists() else ""

    parity_result = parity_payload.get("result", {})
    formula_row = check_formula_line(parity_result)
    tuned_row = check_tuned_line(
        tuned_payload,
        raw_payload,
        q7_tolerance_rad=q7_tolerance_rad,
    )
    strict_row = check_strict_line(parity_result)

    if not formula_row["claim_allowed"]:
        violations.append("formula convergence claim is not valid under the split boundary")
    if formula_row["formula_candidate_fig6_landmark_pass"]:
        violations.append("formula convergence line drifted into Fig.6 q-trajectory parity")
    if not tuned_row["claim_allowed"]:
        violations.append("tuned figure-match claim is not valid under the split boundary")
    if not tuned_row["non_paper_faithful_tuning_present"]:
        violations.append("tuned figure-match line is missing documented non-paper-faithful tuning")
    if strict_row["claim_allowed"]:
        violations.append("strict paper-equivalent parity is now claimed by the source metrics")
    if "Full\npaper-equivalent numerical parity remains unclaimed" not in split_report_text:
        violations.append("split evidence report no longer states full parity remains unclaimed")

    raw_delta_to_formula = tuned_row["python_abs_delta_to_formula_q7_at_22_s_rad"]
    claim_lines_collapsed = bool(
        strict_row["claim_allowed"]
        or formula_row["formula_candidate_fig6_landmark_pass"]
        or tuned_row["formula_like"]
        or (raw_delta_to_formula is not None and raw_delta_to_formula <= q7_tolerance_rad)
    )
    if claim_lines_collapsed:
        violations.append("paper-platform claim lines collapsed into a full-parity implication")

    claim_rows = [formula_row, tuned_row, strict_row]
    audit_passed = not violations
    summary = {
        "audit_passed": audit_passed,
        "violations": violations,
        "formula_convergence_claim_allowed": formula_row["claim_allowed"],
        "tuned_figure_match_claim_allowed": tuned_row["claim_allowed"],
        "strict_paper_equivalent_claim_allowed": strict_row["claim_allowed"],
        "claim_lines_collapsed": claim_lines_collapsed,
        "claim_boundary_preserved": audit_passed and not claim_lines_collapsed,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
        "q7_tolerance_rad": q7_tolerance_rad,
    }
    return {
        "run_source": "paper-platform claim-boundary regression audit",
        "audit_run_id": run_id,
        "source_files": {
            "paper_platform_parity_metrics": rel(parity_metrics_path),
            "tuned_figure_match_metrics": rel(tuned_metrics_path),
            "raw_provenance_metrics": rel(raw_provenance_path),
            "split_evidence_report": rel(split_report_path),
        },
        "summary": summary,
        "claim_rows": claim_rows,
        "claim_boundary": {
            "offline_audit_only": True,
            "formula_convergence_claim": formula_row["claim_allowed"],
            "tuned_figure_match_claim": tuned_row["claim_allowed"],
            "full_paper_equivalent_parity": strict_row["claim_allowed"],
            "formula_controller_fig6_q_trajectory_parity": formula_row[
                "formula_candidate_fig6_landmark_pass"
            ],
            "tuned_figure_match_proves_paper_equations": False,
            "ur10e_hardware_readiness": False,
            "hardware_access_authorized": False,
            "approved_read_only_evidence": False,
            "do_not_mark_goal_complete": True,
        },
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Paper Platform Claim Boundary Audit",
        "",
        f"Run id: `{payload['audit_run_id']}`",
        "",
        f"Audit passed: `{summary['audit_passed']}`",
        f"Formula convergence claim allowed: `{summary['formula_convergence_claim_allowed']}`",
        f"Tuned figure-match claim allowed: `{summary['tuned_figure_match_claim_allowed']}`",
        f"Strict paper-equivalent claim allowed: `{summary['strict_paper_equivalent_claim_allowed']}`",
        f"Claim lines collapsed: `{summary['claim_lines_collapsed']}`",
        f"Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "Claim rows:",
        "",
        "| Claim | Allowed | Boundary |",
        "| --- | ---: | --- |",
    ]
    for row in payload["claim_rows"]:
        lines.append(f"| `{row['claim_id']}` | `{row['claim_allowed']}` | {row['boundary']} |")
    lines.extend(["", "Violations:", ""])
    if summary["violations"]:
        for violation in summary["violations"]:
            lines.append(f"- {violation}")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            (
                "The formula-convergence and tuned Fig.6 evidence lines remain "
                "separate. Full paper-equivalent numerical parity and UR10e "
                "hardware readiness remain unclaimed."
            ),
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--parity-metrics-path", default=DEFAULT_PARITY_METRICS)
    parser.add_argument("--tuned-metrics-path", default=DEFAULT_TUNED_METRICS)
    parser.add_argument("--raw-provenance-path", default=DEFAULT_RAW_PROVENANCE)
    parser.add_argument("--split-report-path", default=DEFAULT_SPLIT_REPORT)
    parser.add_argument("--q7-tolerance-rad", type=float, default=DEFAULT_Q7_TOLERANCE_RAD)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "paper_platform_claim_boundary" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(
        parity_metrics_path=resolve(args.parity_metrics_path),
        tuned_metrics_path=resolve(args.tuned_metrics_path),
        raw_provenance_path=resolve(args.raw_provenance_path),
        split_report_path=resolve(args.split_report_path),
        run_id=run_id,
        q7_tolerance_rad=args.q7_tolerance_rad,
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
