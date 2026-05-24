from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import math
import re
from typing import Any

import numpy as np
import yaml


@dataclass(frozen=True)
class LegacyVerificationMetrics:
    acceptance_mode: str
    overall_pass: bool
    q7_sample_time_s: float
    q7_at_22_s_rad: float
    startup_reaches_velocity_limit: bool
    tail_force_error_mean_N: float
    tail_force_error_pass: bool
    tail_position_error_mean_m: float
    tail_position_error_pass: bool
    tail_orientation_error_mean_rad: float
    tail_orientation_error_pass: bool
    max_joint_limit_violation_rad: float
    max_velocity_limit_violation_rad_s: float
    constraints_pass: bool
    required_method_coverage_pass: bool


def parse_legacy_verification_markdown(text: str) -> LegacyVerificationMetrics:
    return LegacyVerificationMetrics(
        acceptance_mode=_extract_str(text, r"Acceptance mode:\s*`([^`]+)`", "acceptance mode"),
        overall_pass=_extract_bool(text, r"Overall pass:\s*`(true|false)`", "overall pass"),
        q7_sample_time_s=_extract_float(text, r"q7 sample time:\s*`([-+0-9.eE]+)\s*s`", "q7 sample time"),
        q7_at_22_s_rad=_extract_float(text, r"q7 at 22 s:\s*`([-+0-9.eE]+)\s*rad`", "q7 at 22 s"),
        startup_reaches_velocity_limit=_extract_bool(
            text,
            r"Startup reaches velocity limit:\s*`(true|false)`",
            "startup reaches velocity limit",
        ),
        tail_force_error_mean_N=_extract_float(
            text,
            r"Tail mean `\|e_f\|`:\s*`([-+0-9.eE]+)\s*N`; pass:\s*`(?:true|false)`",
            "tail force error",
        ),
        tail_force_error_pass=_extract_bool(
            text,
            r"Tail mean `\|e_f\|`:\s*`[-+0-9.eE]+\s*N`; pass:\s*`(true|false)`",
            "tail force error pass",
        ),
        tail_position_error_mean_m=_extract_float(
            text,
            r"Tail mean `\|\|e_p\|\|`:\s*`([-+0-9.eE]+)\s*m`; pass:\s*`(?:true|false)`",
            "tail position error",
        ),
        tail_position_error_pass=_extract_bool(
            text,
            r"Tail mean `\|\|e_p\|\|`:\s*`[-+0-9.eE]+\s*m`; pass:\s*`(true|false)`",
            "tail position error pass",
        ),
        tail_orientation_error_mean_rad=_extract_float(
            text,
            r"Tail mean `\|\|e_o\|\|`:\s*`([-+0-9.eE]+)`; pass:\s*`(?:true|false)`",
            "tail orientation error",
        ),
        tail_orientation_error_pass=_extract_bool(
            text,
            r"Tail mean `\|\|e_o\|\|`:\s*`[-+0-9.eE]+`; pass:\s*`(true|false)`",
            "tail orientation error pass",
        ),
        max_joint_limit_violation_rad=_extract_float(
            text,
            r"Max joint-limit violation:\s*`([-+0-9.eE]+)\s*rad`",
            "max joint-limit violation",
        ),
        max_velocity_limit_violation_rad_s=_extract_float(
            text,
            r"Max velocity-limit violation:\s*`([-+0-9.eE]+)\s*rad/s`",
            "max velocity-limit violation",
        ),
        constraints_pass=_extract_bool(text, r"Constraints pass:\s*`(true|false)`", "constraints pass"),
        required_method_coverage_pass=_extract_bool(
            text,
            r"Required method coverage pass:\s*`(true|false)`",
            "required method coverage pass",
        ),
    )


def evaluate_paper_platform_parity(config_path: Path, repo_root: Path | None = None) -> dict[str, Any]:
    config_path = Path(config_path)
    repo_root = Path(repo_root) if repo_root is not None else config_path.resolve().parents[1]
    gate = yaml.safe_load(config_path.read_text(encoding="utf-8"))["paper_platform_parity"]
    candidate_info = gate["candidate"]
    candidate_metrics_path = _resolve_path(repo_root, candidate_info["metrics_path"])
    candidate_payload = yaml.safe_load(candidate_metrics_path.read_text(encoding="utf-8"))
    candidate_metrics = candidate_payload.get("metrics", candidate_payload)
    candidate_config = candidate_payload.get("config", {})

    legacy: dict[str, LegacyVerificationMetrics] = {}
    for name, info in gate["legacy_references"].items():
        verification_path = _resolve_path(repo_root, info["verification_path"])
        legacy[name] = parse_legacy_verification_markdown(verification_path.read_text(encoding="utf-8"))

    primary_name = gate["primary_convergence_reference"]
    fig6_name = gate["fig6_landmark_reference"]
    primary = legacy[primary_name]
    fig6_reference = legacy[fig6_name]
    thresholds = gate["thresholds"]
    required = gate["required_coverage"]

    checks: dict[str, dict[str, Any]] = {}
    checks["candidate_execution_contact_bounds"] = _check(
        bool(candidate_metrics.get("execution_success", False))
        and bool(candidate_metrics.get("contact_force_tail_success", False))
        and int(candidate_metrics.get("q_bound_violation_count", -1)) == 0
        and int(candidate_metrics.get("qdot_bound_violation_count", -1)) == 0,
        execution_success=bool(candidate_metrics.get("execution_success", False)),
        contact_force_tail_success=bool(candidate_metrics.get("contact_force_tail_success", False)),
        q_bound_violation_count=int(candidate_metrics.get("q_bound_violation_count", -1)),
        qdot_bound_violation_count=int(candidate_metrics.get("qdot_bound_violation_count", -1)),
    )
    for name, metrics in legacy.items():
        checks[f"legacy_{name}_overall"] = _check(
            metrics.overall_pass and metrics.constraints_pass and metrics.required_method_coverage_pass,
            overall_pass=metrics.overall_pass,
            constraints_pass=metrics.constraints_pass,
            required_method_coverage_pass=metrics.required_method_coverage_pass,
        )

    checks["tail_force_error_against_formula"] = _compare_candidate_to_reference(
        candidate_metrics,
        "tail_force_error_mean_N",
        primary.tail_force_error_mean_N,
        thresholds["tail_force_error_abs_N"],
        thresholds["tail_force_error_delta_N_vs_formula"],
    )
    checks["tail_position_error_against_formula"] = _compare_candidate_to_reference(
        candidate_metrics,
        "tail_position_error_mean_m",
        primary.tail_position_error_mean_m,
        thresholds["tail_position_error_abs_m"],
        thresholds["tail_position_error_delta_m_vs_formula"],
    )
    checks["tail_orientation_error_against_formula"] = _compare_candidate_to_reference(
        candidate_metrics,
        "tail_orientation_error_mean_rad",
        primary.tail_orientation_error_mean_rad,
        thresholds["tail_orientation_error_abs_rad"],
        thresholds["tail_orientation_error_delta_rad_vs_formula"],
    )

    duration_s = float(candidate_metrics.get("duration_s", 0.0))
    required_duration_s = float(required["duration_s"])
    checks["duration_coverage"] = _check(
        duration_s + 1.0e-12 >= required_duration_s,
        candidate_duration_s=duration_s,
        required_duration_s=required_duration_s,
    )

    q7_candidate, q7_source, q7_reason = _candidate_q7_landmark(
        candidate_metrics,
        _resolve_path(repo_root, candidate_info.get("raw_npz_path", "")) if candidate_info.get("raw_npz_path") else None,
        float(required["fig6_q7_sample_time_s"]),
    )
    q7_delta = None if q7_candidate is None else abs(q7_candidate - fig6_reference.q7_at_22_s_rad)
    q7_tolerance = float(thresholds["q7_at_22_abs_error_rad_vs_figure_match"])
    checks["fig6_q7_22s_landmark"] = _check(
        q7_candidate is not None and q7_delta is not None and q7_delta <= q7_tolerance,
        candidate_q7_rad=q7_candidate,
        candidate_source=q7_source,
        reference_q7_rad=fig6_reference.q7_at_22_s_rad,
        abs_delta_rad=q7_delta,
        tolerance_rad=q7_tolerance,
        reason=q7_reason,
    )

    checks["fig5_r_sweep_coverage"] = _fig5_r_sweep_check(gate.get("candidate_fig5_r_sweep", {}), repo_root)
    checks["paper_assumption_compatibility"] = _paper_assumption_check(candidate_config, required)

    formula_convergence_required_checks = [
        "candidate_execution_contact_bounds",
        f"legacy_{primary_name}_overall",
        "tail_force_error_against_formula",
        "tail_position_error_against_formula",
        "tail_orientation_error_against_formula",
        "duration_coverage",
        "fig5_r_sweep_coverage",
        "paper_assumption_compatibility",
    ]
    figure_match_landmark_required_checks = [
        f"legacy_{fig6_name}_overall",
        "fig6_q7_22s_landmark",
    ]
    legacy_strict_required_checks = [
        *formula_convergence_required_checks,
        *figure_match_landmark_required_checks,
    ]
    formula_convergence_pass = _all_checks_pass(checks, formula_convergence_required_checks)
    figure_match_landmark_pass = _all_checks_pass(checks, figure_match_landmark_required_checks)
    parity_pass = _all_checks_pass(checks, legacy_strict_required_checks)
    claim_results = {
        "formula_convergence": {
            "pass": formula_convergence_pass,
            "required_checks": formula_convergence_required_checks,
            "claim": "paper_platform_7dof_formula_convergence",
            "boundary": (
                "passes execution/contact/bounds, duration, Fig.5 coverage, "
                "paper-assumption compatibility, and tail convergence against "
                "the formula-faithful legacy reference; does not claim full "
                "q-trajectory or Fig.6 landmark parity"
            ),
        },
        "figure_match_landmark": {
            "pass": figure_match_landmark_pass,
            "required_checks": figure_match_landmark_required_checks,
            "claim": "paper_platform_7dof_figure_match_landmark",
            "boundary": (
                "tracks the tuned legacy figure-match q7 landmark separately "
                "from formula-faithful parity because v49-v50 provenance shows "
                "that landmark uses explicit figure-match tuning"
            ),
        },
        "legacy_strict_all_checks": {
            "pass": parity_pass,
            "required_checks": legacy_strict_required_checks,
            "claim": gate["claim"],
            "boundary": (
                "backward-compatible aggregate requiring both formula convergence "
                "and the tuned figure-match q7 landmark"
            ),
        },
    }
    return {
        "claim": gate["claim"],
        "paper_platform_parity_pass": parity_pass,
        "paper_platform_formula_convergence_pass": formula_convergence_pass,
        "paper_platform_figure_match_landmark_pass": figure_match_landmark_pass,
        "strict_required_checks": legacy_strict_required_checks,
        "formula_convergence_required_checks": formula_convergence_required_checks,
        "figure_match_landmark_required_checks": figure_match_landmark_required_checks,
        "claim_results": claim_results,
        "candidate": {
            "label": candidate_info.get("label", ""),
            "metrics_path": _display_path(candidate_metrics_path, repo_root),
            "raw_npz_path": candidate_info.get("raw_npz_path", ""),
            "metrics": candidate_metrics,
            "config": candidate_config,
        },
        "legacy_references": {name: asdict(metrics) for name, metrics in legacy.items()},
        "primary_convergence_reference": primary_name,
        "fig6_landmark_reference": fig6_name,
        "checks": checks,
        "interpretation": _interpretation(claim_results, checks),
    }


def _extract_str(text: str, pattern: str, label: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"could not parse {label}")
    return match.group(1)


def _extract_float(text: str, pattern: str, label: str) -> float:
    return float(_extract_str(text, pattern, label))


def _extract_bool(text: str, pattern: str, label: str) -> bool:
    value = _extract_str(text, pattern, label).lower()
    if value not in {"true", "false"}:
        raise ValueError(f"could not parse {label} as bool")
    return value == "true"


def _resolve_path(repo_root: Path, path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return repo_root / path


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _check(pass_value: bool, **values: Any) -> dict[str, Any]:
    return {"pass": bool(pass_value), **values}


def _all_checks_pass(checks: dict[str, dict[str, Any]], required_checks: list[str]) -> bool:
    return all(bool(checks[name]["pass"]) for name in required_checks)


def _compare_candidate_to_reference(
    candidate_metrics: dict[str, Any],
    key: str,
    reference_value: float,
    absolute_limit: float,
    delta_tolerance: float,
) -> dict[str, Any]:
    candidate_value = float(candidate_metrics.get(key, math.inf))
    delta = abs(candidate_value - float(reference_value))
    return _check(
        candidate_value <= float(absolute_limit) and delta <= float(delta_tolerance),
        candidate_value=candidate_value,
        reference_value=float(reference_value),
        absolute_limit=float(absolute_limit),
        abs_delta=delta,
        delta_tolerance=float(delta_tolerance),
    )


def _candidate_q7_landmark(
    candidate_metrics: dict[str, Any],
    raw_npz_path: Path | None,
    sample_time_s: float,
) -> tuple[float | None, str, str]:
    metric_keys = [
        f"fig6_q7_at_{int(sample_time_s)}s_rad" if sample_time_s.is_integer() else "",
        "fig6_q7_at_22_s_rad",
        "q7_at_22_s_rad",
    ]
    for key in metric_keys:
        if key and key in candidate_metrics:
            return float(candidate_metrics[key]), f"candidate metrics field {key}", "candidate metric present"
    if raw_npz_path is None:
        return None, "none", "candidate raw npz path is not configured"
    if not raw_npz_path.exists():
        return None, str(raw_npz_path), "candidate raw npz is absent; raw arrays are intentionally ignored by Git"
    with np.load(raw_npz_path) as raw:
        if "t_s" not in raw or "q_rad" not in raw:
            return None, str(raw_npz_path), "candidate raw npz lacks t_s or q_rad"
        t_s = np.asarray(raw["t_s"], dtype=float)
        q_rad = np.asarray(raw["q_rad"], dtype=float)
        if t_s.size == 0 or q_rad.ndim != 2 or q_rad.shape[1] < 7:
            return None, str(raw_npz_path), "candidate raw npz has invalid t_s or q_rad shape"
        if float(t_s[-1]) + 1.0e-12 < sample_time_s:
            return None, str(raw_npz_path), f"candidate raw arrays end at {float(t_s[-1]):.3f} s"
        index = int(np.argmin(np.abs(t_s - sample_time_s)))
        return float(q_rad[index, 6]), str(raw_npz_path), f"nearest raw sample at {float(t_s[index]):.3f} s"


def _fig5_r_sweep_check(fig5_config: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    required_values = [_numeric_key(value) for value in fig5_config.get("required_r_values", [])]
    required_duration_s = float(fig5_config.get("required_duration_s", 0.0))
    configured_paths = {
        _numeric_key(key): path for key, path in dict(fig5_config.get("metrics_paths", {})).items()
    }
    missing = []
    present = []
    invalid = []
    for value in required_values:
        path_value = configured_paths.get(value)
        if path_value is None:
            missing.append(value)
            continue
        path = _resolve_path(repo_root, str(path_value))
        if not path.exists():
            missing.append(value)
        else:
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
            metrics = payload.get("metrics", payload)
            actual_r = _numeric_key(metrics.get("fig5_r_value", math.nan))
            execution_success = bool(metrics.get("execution_success", False))
            duration_s = float(metrics.get("duration_s", 0.0))
            if actual_r != value or not execution_success or duration_s + 1.0e-12 < required_duration_s:
                invalid.append(
                    {
                        "r": value,
                        "path": str(path),
                        "actual_r": actual_r,
                        "execution_success": execution_success,
                        "duration_s": duration_s,
                    }
                )
            else:
                present.append(value)
    return _check(
        len(missing) == 0 and len(invalid) == 0 and len(required_values) > 0,
        required_r_values=required_values,
        required_duration_s=required_duration_s,
        present_r_values=present,
        missing_r_values=missing,
        invalid_r_values=invalid,
    )


def _paper_assumption_check(candidate_config: dict[str, Any], required: dict[str, Any]) -> dict[str, Any]:
    force_integral_limit = candidate_config.get("force_integral_limit", math.inf)
    try:
        force_integral_limit_float = float(force_integral_limit)
    except (TypeError, ValueError):
        force_integral_limit_float = math.inf
    uncapped = math.isinf(force_integral_limit_float)
    required_uncapped = bool(required.get("uncapped_force_integral", False))
    return _check(
        (not required_uncapped) or uncapped,
        force_integral_limit=force_integral_limit_float,
        required_uncapped_force_integral=required_uncapped,
        reason="finite force-integral cap is a diagnostic anti-windup assumption" if not uncapped else "uncapped",
    )


def _numeric_key(value: Any) -> str:
    return f"{float(value):.10g}"


def _interpretation(claim_results: dict[str, dict[str, Any]], checks: dict[str, dict[str, Any]]) -> str:
    formula_pass = bool(claim_results["formula_convergence"]["pass"])
    figure_pass = bool(claim_results["figure_match_landmark"]["pass"])
    strict_pass = bool(claim_results["legacy_strict_all_checks"]["pass"])
    if strict_pass:
        return "legacy strict aggregate passed: formula convergence and figure-match landmark both pass"
    failed = [name for name, payload in checks.items() if not payload["pass"]]
    if formula_pass and not figure_pass:
        return (
            "formula-convergence claim passed, but legacy strict aggregate remains failed "
            "because tuned figure-match landmark checks failed: " + ", ".join(failed)
        )
    return "paper-platform split gate failed: " + ", ".join(failed)
