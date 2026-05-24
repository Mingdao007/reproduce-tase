from __future__ import annotations

from tase_repro.terminal_setup_gate import (
    TerminalSetupDiagnosticGate,
    evaluate_candidate,
    evaluate_terminal_setup_metrics,
)


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
