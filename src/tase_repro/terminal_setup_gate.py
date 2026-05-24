from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class TerminalSetupDiagnosticGate:
    max_terminal_tangential_error_m: float
    max_terminal_orientation_error_rad: float
    max_terminal_force_error_N: float
    min_target_contact_count: int
    claim_scope: str

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "TerminalSetupDiagnosticGate":
        section = config["ur10e_adapted_terminal_setup_diagnostic_gate"]
        return cls(
            max_terminal_tangential_error_m=float(section["max_terminal_tangential_error_m"]),
            max_terminal_orientation_error_rad=float(section["max_terminal_orientation_error_rad"]),
            max_terminal_force_error_N=float(section["max_terminal_force_error_N"]),
            min_target_contact_count=int(section["min_target_contact_count"]),
            claim_scope=str(section["claim_scope"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_terminal_tangential_error_m": float(self.max_terminal_tangential_error_m),
            "max_terminal_orientation_error_rad": float(self.max_terminal_orientation_error_rad),
            "max_terminal_force_error_N": float(self.max_terminal_force_error_N),
            "min_target_contact_count": int(self.min_target_contact_count),
            "claim_scope": self.claim_scope,
        }


def load_acceptance_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def evaluate_candidate(candidate: dict[str, Any], gate: TerminalSetupDiagnosticGate) -> dict[str, Any]:
    force_error = float(candidate["force_error_N"])
    tangential_error = float(candidate["tangential_error_m"])
    orientation_error = float(candidate["orientation_error_rad"])
    target_contact_count = int(candidate.get("target_contact_count", 1 if candidate.get("contact_present") else 0))
    criteria = {
        "force_error_N": {
            "actual": force_error,
            "operator": "<=",
            "threshold": gate.max_terminal_force_error_N,
            "passed": force_error <= gate.max_terminal_force_error_N,
        },
        "tangential_error_m": {
            "actual": tangential_error,
            "operator": "<=",
            "threshold": gate.max_terminal_tangential_error_m,
            "passed": tangential_error <= gate.max_terminal_tangential_error_m,
        },
        "orientation_error_rad": {
            "actual": orientation_error,
            "operator": "<=",
            "threshold": gate.max_terminal_orientation_error_rad,
            "passed": orientation_error <= gate.max_terminal_orientation_error_rad,
        },
        "target_contact_count": {
            "actual": target_contact_count,
            "operator": ">=",
            "threshold": gate.min_target_contact_count,
            "passed": target_contact_count >= gate.min_target_contact_count,
        },
    }
    failed = [name for name, criterion in criteria.items() if not criterion["passed"]]
    ratios = [
        force_error / gate.max_terminal_force_error_N,
        tangential_error / gate.max_terminal_tangential_error_m,
        orientation_error / gate.max_terminal_orientation_error_rad,
        0.0 if target_contact_count >= gate.min_target_contact_count else float("inf"),
    ]
    return {
        "seed_label": candidate["seed_label"],
        "q": candidate["q"],
        "tcp_m": candidate["tcp_m"],
        "criteria": criteria,
        "failed_criteria": failed,
        "passed": not failed,
        "max_gate_ratio": max(ratios),
        "source_force_error_N": force_error,
        "source_tangential_error_m": tangential_error,
        "source_orientation_error_rad": orientation_error,
        "source_target_contact_count": target_contact_count,
    }


def evaluate_terminal_setup_metrics(metrics: dict[str, Any], gate: TerminalSetupDiagnosticGate) -> dict[str, Any]:
    candidates = [evaluate_candidate(candidate, gate) for candidate in metrics["candidates"]]
    candidates.sort(key=lambda candidate: (candidate["max_gate_ratio"], candidate["seed_label"]))
    passed = [candidate for candidate in candidates if candidate["passed"]]
    return {
        "source_run_id": metrics.get("run_id"),
        "source_run_config": metrics.get("config"),
        "source_model": metrics.get("model"),
        "source_candidate_count": int(metrics["candidate_count"]),
        "gate": gate.to_dict(),
        "pass_count": len(passed),
        "passed_seed_labels": [candidate["seed_label"] for candidate in passed],
        "best_candidate": candidates[0],
        "passed_candidates": passed,
        "warnings": [
            "diagnostic terminal setup gate only",
            "not paper-equivalent full staged feasibility",
            "not a path or trajectory feasibility claim",
            "not hardware-ready",
        ],
    }
