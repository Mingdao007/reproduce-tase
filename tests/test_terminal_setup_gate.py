from __future__ import annotations

from pathlib import Path

import yaml

from tase_repro.terminal_setup_gate import (
    TerminalSetupDiagnosticGate,
    evaluate_candidate,
    evaluate_terminal_setup_metrics,
)

ROOT = Path(__file__).resolve().parents[1]


def test_terminal_setup_diagnostic_gate_evaluates_candidate() -> None:
    gate = TerminalSetupDiagnosticGate(
        max_terminal_tangential_error_m=0.004,
        max_terminal_orientation_error_rad=0.08,
        max_terminal_force_error_N=0.25,
        min_target_contact_count=1,
        claim_scope="test",
    )
    candidate = {
        "seed_label": "candidate",
        "q": [0.0] * 6,
        "tcp_m": [0.0, 0.0, 0.0],
        "force_error_N": 0.01,
        "tangential_error_m": 0.003,
        "orientation_error_rad": 0.07,
        "target_contact_count": 1,
    }
    result = evaluate_candidate(candidate, gate)

    assert result["passed"]
    assert result["failed_criteria"] == []
    assert result["max_gate_ratio"] < 1.0


def test_terminal_setup_diagnostic_gate_counts_passes() -> None:
    gate = TerminalSetupDiagnosticGate(
        max_terminal_tangential_error_m=0.004,
        max_terminal_orientation_error_rad=0.08,
        max_terminal_force_error_N=0.25,
        min_target_contact_count=1,
        claim_scope="test",
    )
    metrics = {
        "run_id": "run",
        "config": "config.yaml",
        "model": "model.xml",
        "candidate_count": 2,
        "candidates": [
            {
                "seed_label": "pass",
                "q": [0.0] * 6,
                "tcp_m": [0.0, 0.0, 0.0],
                "force_error_N": 0.01,
                "tangential_error_m": 0.003,
                "orientation_error_rad": 0.07,
                "target_contact_count": 1,
            },
            {
                "seed_label": "fail",
                "q": [0.0] * 6,
                "tcp_m": [0.0, 0.0, 0.0],
                "force_error_N": 0.0,
                "tangential_error_m": 0.0,
                "orientation_error_rad": 0.0,
                "target_contact_count": 0,
            },
        ],
    }
    evaluation = evaluate_terminal_setup_metrics(metrics, gate)

    assert evaluation["pass_count"] == 1
    assert evaluation["passed_seed_labels"] == ["pass"]
    assert evaluation["best_candidate"]["seed_label"] == "pass"


def test_stage_a_target_config_matches_v57_diagnostic_evidence() -> None:
    target = yaml.safe_load((ROOT / "configs/ur10e_adapted_stage_a_target.yaml").read_text(encoding="utf-8"))
    selected = target["selected_stage_a_target"]
    source = yaml.safe_load((ROOT / selected["source_metrics"]).read_text(encoding="utf-8"))
    best = source["best_candidate"]

    assert target["v58_scope"]["paper_equivalent_claim"] is False
    assert selected["label"] == "ur10e_adapted_terminal_setup_diagnostic"
    assert selected["claim_scope"] == "terminal_target_for_simulation_controller_prototype_only"
    assert source["pass_count"] == 1
    assert source["passed_seed_labels"] == [best["seed_label"]]
    assert selected["q_rad"] == best["q"]
    assert selected["tcp_m"] == best["tcp_m"]
    assert selected["source_errors"] == {
        "force_error_N": best["source_force_error_N"],
        "tangential_error_m": best["source_tangential_error_m"],
        "orientation_error_rad": best["source_orientation_error_rad"],
        "target_contact_count": best["source_target_contact_count"],
    }
    assert selected["diagnostic_gate"] == {
        "max_terminal_tangential_error_m": source["gate"]["max_terminal_tangential_error_m"],
        "max_terminal_orientation_error_rad": source["gate"]["max_terminal_orientation_error_rad"],
        "max_terminal_force_error_N": source["gate"]["max_terminal_force_error_N"],
        "min_target_contact_count": source["gate"]["min_target_contact_count"],
    }
