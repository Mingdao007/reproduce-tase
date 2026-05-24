from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RelaxedSetupBudget:
    max_setup_tangential_drift_m: float
    max_final_orientation_error_rad: float
    max_tail_mean_abs_force_error_N: float
    contact_present_fraction_min: float
    max_qdot_violation_rad_s: float
    max_joint_limit_violation_rad: float
    qdot_saturation_policy: str = "record_only"

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "RelaxedSetupBudget":
        data = config["ur10e_adapted_relaxed_setup_budget"]
        return cls(
            max_setup_tangential_drift_m=float(data["max_setup_tangential_drift_m"]),
            max_final_orientation_error_rad=float(data["max_final_orientation_error_rad"]),
            max_tail_mean_abs_force_error_N=float(data["max_tail_mean_abs_force_error_N"]),
            contact_present_fraction_min=float(data["contact_present_fraction_min"]),
            max_qdot_violation_rad_s=float(data["max_qdot_violation_rad_s"]),
            max_joint_limit_violation_rad=float(data["max_joint_limit_violation_rad"]),
            qdot_saturation_policy=str(data.get("qdot_saturation_policy", "record_only")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_setup_tangential_drift_m": float(self.max_setup_tangential_drift_m),
            "max_final_orientation_error_rad": float(self.max_final_orientation_error_rad),
            "max_tail_mean_abs_force_error_N": float(self.max_tail_mean_abs_force_error_N),
            "contact_present_fraction_min": float(self.contact_present_fraction_min),
            "max_qdot_violation_rad_s": float(self.max_qdot_violation_rad_s),
            "max_joint_limit_violation_rad": float(self.max_joint_limit_violation_rad),
            "qdot_saturation_policy": self.qdot_saturation_policy,
        }


def load_acceptance_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _criterion(actual: float, operator: str, threshold: float) -> dict[str, Any]:
    if operator == "<=":
        passed = float(actual) <= float(threshold)
    elif operator == ">=":
        passed = float(actual) >= float(threshold)
    else:
        raise ValueError(f"unsupported operator: {operator}")
    return {
        "actual": float(actual),
        "operator": operator,
        "threshold": float(threshold),
        "passed": bool(passed),
    }


def evaluate_relaxed_setup_budget(approach_metrics: dict[str, Any], budget: RelaxedSetupBudget) -> dict[str, Any]:
    criteria = {
        "setup_tangential_drift_m": _criterion(
            approach_metrics["max_tangential_position_error_m"],
            "<=",
            budget.max_setup_tangential_drift_m,
        ),
        "final_orientation_error_rad": _criterion(
            approach_metrics["final_orientation_error_rad"],
            "<=",
            budget.max_final_orientation_error_rad,
        ),
        "tail_mean_abs_force_error_N": _criterion(
            approach_metrics["tail_mean_abs_force_error_N"],
            "<=",
            budget.max_tail_mean_abs_force_error_N,
        ),
        "contact_present_fraction": _criterion(
            approach_metrics["contact_present_fraction"],
            ">=",
            budget.contact_present_fraction_min,
        ),
        "max_qdot_violation_rad_s": _criterion(
            approach_metrics["max_qdot_violation_rad_s"],
            "<=",
            budget.max_qdot_violation_rad_s,
        ),
        "max_joint_limit_violation_rad": _criterion(
            approach_metrics["max_joint_limit_violation_rad"],
            "<=",
            budget.max_joint_limit_violation_rad,
        ),
    }
    failed = [name for name, criterion in criteria.items() if not criterion["passed"]]
    return {
        "passed": not failed,
        "failed_criteria": failed,
        "criteria": criteria,
        "recorded_qdot_saturation_fraction": float(approach_metrics["qdot_saturation_fraction"]),
        "recorded_tail_max_qdot_utilization": float(approach_metrics["tail_max_qdot_utilization"]),
        "qdot_saturation_policy": budget.qdot_saturation_policy,
    }


def evaluate_staged_run_root(run_root: str | Path, budget: RelaxedSetupBudget) -> dict[str, Any]:
    run_path = Path(run_root)
    with (run_path / "summary.yaml").open("r", encoding="utf-8") as f:
        summary = yaml.safe_load(f)
    rows = []
    for row in summary["rows"]:
        case_name = row["trajectory"]
        with (run_path / case_name / "metrics.yaml").open("r", encoding="utf-8") as f:
            metrics = yaml.safe_load(f)
        relaxed_setup_gate = evaluate_relaxed_setup_budget(metrics["approach"], budget)
        trajectory_pass = bool(row["trajectory_feasibility_pass"])
        adapted_pass = bool(relaxed_setup_gate["passed"] and trajectory_pass)
        rows.append(
            {
                "trajectory": case_name,
                "relaxed_setup_pass": bool(relaxed_setup_gate["passed"]),
                "relaxed_setup_failed_criteria": list(relaxed_setup_gate["failed_criteria"]),
                "trajectory_feasibility_pass": trajectory_pass,
                "ur10e_adapted_trajectory_after_relaxed_setup_pass": adapted_pass,
                "strict_full_staged_feasibility_pass": bool(row["full_staged_feasibility_pass"]),
                "setup_final_orientation_error_rad": float(row["approach_final_orientation_error_rad"]),
                "setup_tangential_drift_m": float(row["approach_max_tangential_position_error_m"]),
                "setup_tail_mean_abs_force_error_N": float(metrics["approach"]["tail_mean_abs_force_error_N"]),
                "setup_contact_present_fraction": float(metrics["approach"]["contact_present_fraction"]),
                "setup_qdot_saturation_fraction": float(metrics["approach"]["qdot_saturation_fraction"]),
                "trajectory_max_orientation_error_rad": float(row["trajectory_max_orientation_error_rad"]),
                "trajectory_qdot_saturation_fraction": float(row["trajectory_qdot_saturation_fraction"]),
                "relaxed_setup_gate": relaxed_setup_gate,
            }
        )
    return {
        "run_root": str(run_path),
        "budget": budget.to_dict(),
        "case_count": len(rows),
        "relaxed_setup_pass_count": sum(1 for row in rows if row["relaxed_setup_pass"]),
        "trajectory_feasibility_pass_count": sum(1 for row in rows if row["trajectory_feasibility_pass"]),
        "ur10e_adapted_trajectory_after_relaxed_setup_pass_count": sum(
            1 for row in rows if row["ur10e_adapted_trajectory_after_relaxed_setup_pass"]
        ),
        "strict_full_staged_feasibility_pass_count": sum(
            1 for row in rows if row["strict_full_staged_feasibility_pass"]
        ),
        "rows": rows,
    }
