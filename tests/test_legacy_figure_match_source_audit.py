from __future__ import annotations

from scripts.audit_legacy_figure_match_source import (
    classify_source,
    extract_assignments,
)


def test_extract_figure_match_assignments_and_classification() -> None:
    source = """
cfg.paper_method.formula_faithful.orientation_mode = 'force_shortest_arc';
cfg.paper_method.formula_faithful.solver_mode = 'kkt_projection';
cfg.paper_method.formula_faithful.acceptance_mode = 'diagnostic';
cfg.paper_method.formula_faithful.force_loop_mode = 'paper_literal';
cfg.paper_method.figure_match.orientation_mode = 'normal_only';
cfg.paper_method.figure_match.solver_mode = 'pinv_bounded';
cfg.paper_method.figure_match.acceptance_mode = 'landmark';
cfg.paper_method.figure_match.force_loop_mode = 'admittance_proxy';
cfg.paper_method.figure_match.alpha = 20.0;
cfg.paper_method.figure_match.maxAngularSpeed = 1.5;
cfg.paper_method.figure_match.kp = 25.0;
cfg.paper_method.figure_match.q7NullspaceSpeed = 0.35;
"""
    formula = extract_assignments(source, "cfg.paper_method.formula_faithful")
    figure = extract_assignments(source, "cfg.paper_method.figure_match")
    assert figure["force_loop_mode"]["value"] == "admittance_proxy"
    assert figure["q7NullspaceSpeed"]["value"] == 0.35

    summary = classify_source(formula=formula, figure=figure, raw_figure=None)
    assert not summary["figure_match_is_formula_faithful"]
    assert summary["uses_explicit_q7_nullspace_bias"]
    assert summary["nonpaper_tuning_knob_count"] >= 8
