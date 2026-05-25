from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_paper_platform_claim_boundary import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]


def build_current_payload(**overrides):
    kwargs = {
        "parity_metrics_path": ROOT
        / "runs"
        / "paper_platform_parity_eval"
        / "20260524T124200"
        / "metrics.yaml",
        "tuned_metrics_path": ROOT
        / "runs"
        / "paper_7dof_section_v"
        / "20260524T134441"
        / "metrics.yaml",
        "raw_provenance_path": ROOT
        / "runs"
        / "paper_7dof_fig6_raw_provenance"
        / "20260524T134549"
        / "metrics.yaml",
        "split_report_path": ROOT / "reports" / "paper_platform_split_evidence_report.md",
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_current_paper_platform_claim_boundary_is_preserved() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["formula_convergence_claim_allowed"] is True
    assert summary["tuned_figure_match_claim_allowed"] is True
    assert summary["strict_paper_equivalent_claim_allowed"] is False
    assert summary["claim_lines_collapsed"] is False
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True

    rows = {row["claim_id"]: row for row in payload["claim_rows"]}
    assert rows["paper_platform_7dof_formula_convergence"]["claim_allowed"] is True
    assert (
        rows["paper_platform_7dof_formula_convergence"][
            "formula_candidate_fig6_landmark_pass"
        ]
        is False
    )
    tuned = rows["paper_platform_7dof_tuned_figure_match_candidate"]
    assert tuned["claim_allowed"] is True
    assert tuned["non_paper_faithful_tuning_present"] is True
    assert tuned["python_abs_delta_to_formula_q7_at_22_s_rad"] > 1.0
    assert rows["paper_platform_7dof_legacy_strict_all_checks"]["claim_allowed"] is False

    boundary = payload["claim_boundary"]
    assert boundary["full_paper_equivalent_parity"] is False
    assert boundary["hardware_access_authorized"] is False
    assert boundary["approved_read_only_evidence"] is False


def test_claim_boundary_rejects_strict_parity_drift(tmp_path) -> None:
    parity = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "paper_platform_parity_eval"
            / "20260524T124200"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    parity["result"]["paper_platform_parity_pass"] = True
    parity["result"]["paper_platform_figure_match_landmark_pass"] = True
    parity["result"]["checks"]["fig6_q7_22s_landmark"]["pass"] = True
    drifted = tmp_path / "parity.yaml"
    drifted.write_text(yaml.safe_dump(parity, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(parity_metrics_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["strict_paper_equivalent_claim_allowed"] is True
    assert payload["summary"]["claim_lines_collapsed"] is True
    assert "strict paper-equivalent parity is now claimed by the source metrics" in payload[
        "summary"
    ]["violations"]
    assert "paper-platform claim lines collapsed into a full-parity implication" in payload[
        "summary"
    ]["violations"]


def test_claim_boundary_rejects_tuned_formula_like_drift(tmp_path) -> None:
    tuned = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "paper_7dof_section_v"
            / "20260524T134441"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    tuned["metrics"]["force_loop_mode"] = "paper_literal"
    tuned["metrics"]["orientation_mode"] = "force_shortest_arc"
    tuned["metrics"]["solver_mode"] = "kkt_projection"
    tuned["metrics"]["force_integral_limit"] = float("inf")
    tuned["metrics"]["q7_nullspace_speed_rad_s"] = 0.0
    drifted = tmp_path / "tuned.yaml"
    drifted.write_text(yaml.safe_dump(tuned, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(tuned_metrics_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["tuned_figure_match_claim_allowed"] is False
    assert payload["summary"]["claim_lines_collapsed"] is True
    assert "tuned figure-match line is missing documented non-paper-faithful tuning" in payload[
        "summary"
    ]["violations"]


def test_claim_boundary_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "paper_platform_claim_boundary"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_paper_platform_claim_boundary.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_CLAIM_BOUNDARY",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.strip() == str(out_dir)
    metrics_yaml_text = (out_dir / "metrics.yaml").read_text(encoding="utf-8")
    metrics = yaml.safe_load(metrics_yaml_text)
    metrics_json = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))

    assert metrics_json == metrics
    assert "&id" not in metrics_yaml_text
    assert "*id" not in metrics_yaml_text
    assert metrics["summary"]["audit_passed"] is True
    assert metrics["summary"]["claim_lines_collapsed"] is False
    assert metrics["claim_boundary"]["full_paper_equivalent_parity"] is False
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
