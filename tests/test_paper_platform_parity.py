from __future__ import annotations

from pathlib import Path

import yaml

from tase_repro.paper_platform_parity import (
    evaluate_paper_platform_parity,
    parse_legacy_verification_markdown,
)


ROOT = Path(__file__).resolve().parents[1]


def test_parse_formula_faithful_legacy_verification() -> None:
    path = (
        ROOT
        / "runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/"
        / "paper_method_formula_faithful/paper_method_formula_faithful_verification.md"
    )
    metrics = parse_legacy_verification_markdown(path.read_text(encoding="utf-8"))
    assert metrics.acceptance_mode == "diagnostic"
    assert metrics.overall_pass
    assert metrics.constraints_pass
    assert metrics.required_method_coverage_pass
    assert metrics.q7_at_22_s_rad == 1.124179
    assert metrics.tail_force_error_mean_N == 0.0476436


def test_current_v47_candidate_splits_formula_convergence_from_q7_landmark() -> None:
    result = evaluate_paper_platform_parity(ROOT / "configs/paper_platform_parity.yaml", ROOT)
    assert not result["paper_platform_parity_pass"]
    assert result["paper_platform_formula_convergence_pass"]
    assert not result["paper_platform_figure_match_landmark_pass"]
    assert result["checks"]["candidate_execution_contact_bounds"]["pass"]
    assert result["checks"]["tail_force_error_against_formula"]["pass"]
    assert result["checks"]["duration_coverage"]["pass"]
    assert not result["checks"]["fig6_q7_22s_landmark"]["pass"]
    assert result["checks"]["fig5_r_sweep_coverage"]["pass"]
    assert result["checks"]["paper_assumption_compatibility"]["pass"]
    assert "fig6_q7_22s_landmark" not in result["formula_convergence_required_checks"]
    assert "fig6_q7_22s_landmark" in result["figure_match_landmark_required_checks"]


def test_synthetic_complete_candidate_can_pass_gate(tmp_path: Path) -> None:
    candidate_path = tmp_path / "candidate.yaml"
    candidate_path.write_text(
        yaml.safe_dump(
            {
                "metrics": {
                    "execution_success": True,
                    "contact_force_tail_success": True,
                    "duration_s": 30.0,
                    "q_bound_violation_count": 0,
                    "qdot_bound_violation_count": 0,
                    "tail_force_error_mean_N": 0.05,
                    "tail_position_error_mean_m": 0.0006,
                    "tail_orientation_error_mean_rad": 0.00006,
                    "fig6_q7_at_22s_rad": 2.49,
                },
                "config": {"force_integral_limit": float("inf")},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    fig5_paths = {}
    for value in ["0.2", "0.4", "0.6", "0.8", "1"]:
        path = tmp_path / f"fig5_r{value.replace('.', 'p')}.yaml"
        path.write_text(
            yaml.safe_dump(
                {
                    "metrics": {
                        "fig5_r_value": float(value),
                        "duration_s": 2.0,
                        "execution_success": True,
                    }
                }
            ),
            encoding="utf-8",
        )
        fig5_paths[value] = str(path)
    config_path = tmp_path / "parity.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "paper_platform_parity": {
                    "claim": "synthetic",
                    "candidate": {"label": "synthetic", "metrics_path": str(candidate_path)},
                    "legacy_references": {
                        "formula_faithful": {
                            "verification_path": str(
                                ROOT
                                / "runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/"
                                / "paper_method_formula_faithful/paper_method_formula_faithful_verification.md"
                            )
                        },
                        "figure_match": {
                            "verification_path": str(
                                ROOT
                                / "runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/"
                                / "paper_method_figure_match/paper_method_figure_match_verification.md"
                            )
                        },
                    },
                    "primary_convergence_reference": "formula_faithful",
                    "fig6_landmark_reference": "figure_match",
                    "required_coverage": {
                        "duration_s": 30.0,
                        "fig6_q7_sample_time_s": 22.0,
                        "fig5_r_sweep": True,
                        "uncapped_force_integral": True,
                    },
                    "candidate_fig5_r_sweep": {
                        "required_duration_s": 2.0,
                        "required_r_values": [0.2, 0.4, 0.6, 0.8, 1.0],
                        "metrics_paths": fig5_paths,
                    },
                    "thresholds": {
                        "tail_force_error_abs_N": 1.0,
                        "tail_position_error_abs_m": 0.002,
                        "tail_orientation_error_abs_rad": 0.001,
                        "tail_force_error_delta_N_vs_formula": 0.05,
                        "tail_position_error_delta_m_vs_formula": 0.001,
                        "tail_orientation_error_delta_rad_vs_formula": 0.0001,
                        "q7_at_22_abs_error_rad_vs_figure_match": 0.05,
                    },
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    result = evaluate_paper_platform_parity(config_path, ROOT)
    assert result["paper_platform_parity_pass"]
    assert result["paper_platform_formula_convergence_pass"]
    assert result["paper_platform_figure_match_landmark_pass"]


def test_synthetic_formula_candidate_can_pass_without_figure_match_landmark(tmp_path: Path) -> None:
    candidate_path = tmp_path / "candidate.yaml"
    candidate_path.write_text(
        yaml.safe_dump(
            {
                "metrics": {
                    "execution_success": True,
                    "contact_force_tail_success": True,
                    "duration_s": 30.0,
                    "q_bound_violation_count": 0,
                    "qdot_bound_violation_count": 0,
                    "tail_force_error_mean_N": 0.05,
                    "tail_position_error_mean_m": 0.0006,
                    "tail_orientation_error_mean_rad": 0.00006,
                    "fig6_q7_at_22s_rad": 1.66,
                },
                "config": {"force_integral_limit": float("inf")},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    fig5_paths = {}
    for value in ["0.2", "0.4", "0.6", "0.8", "1"]:
        path = tmp_path / f"fig5_r{value.replace('.', 'p')}.yaml"
        path.write_text(
            yaml.safe_dump(
                {
                    "metrics": {
                        "fig5_r_value": float(value),
                        "duration_s": 2.0,
                        "execution_success": True,
                    }
                }
            ),
            encoding="utf-8",
        )
        fig5_paths[value] = str(path)
    config_path = tmp_path / "parity.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "paper_platform_parity": {
                    "claim": "synthetic",
                    "candidate": {"label": "synthetic", "metrics_path": str(candidate_path)},
                    "legacy_references": {
                        "formula_faithful": {
                            "verification_path": str(
                                ROOT
                                / "runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/"
                                / "paper_method_formula_faithful/paper_method_formula_faithful_verification.md"
                            )
                        },
                        "figure_match": {
                            "verification_path": str(
                                ROOT
                                / "runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/"
                                / "paper_method_figure_match/paper_method_figure_match_verification.md"
                            )
                        },
                    },
                    "primary_convergence_reference": "formula_faithful",
                    "fig6_landmark_reference": "figure_match",
                    "required_coverage": {
                        "duration_s": 30.0,
                        "fig6_q7_sample_time_s": 22.0,
                        "fig5_r_sweep": True,
                        "uncapped_force_integral": True,
                    },
                    "candidate_fig5_r_sweep": {
                        "required_duration_s": 2.0,
                        "required_r_values": [0.2, 0.4, 0.6, 0.8, 1.0],
                        "metrics_paths": fig5_paths,
                    },
                    "thresholds": {
                        "tail_force_error_abs_N": 1.0,
                        "tail_position_error_abs_m": 0.002,
                        "tail_orientation_error_abs_rad": 0.001,
                        "tail_force_error_delta_N_vs_formula": 0.05,
                        "tail_position_error_delta_m_vs_formula": 0.001,
                        "tail_orientation_error_delta_rad_vs_formula": 0.0001,
                        "q7_at_22_abs_error_rad_vs_figure_match": 0.05,
                    },
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    result = evaluate_paper_platform_parity(config_path, ROOT)
    assert result["paper_platform_formula_convergence_pass"]
    assert not result["paper_platform_figure_match_landmark_pass"]
    assert not result["paper_platform_parity_pass"]
