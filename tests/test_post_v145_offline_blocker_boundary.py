from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_post_v145_offline_blocker_boundary import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]
V145 = ROOT / "runs" / "user_completion_criterion_after_v144" / "20260525T190000" / "metrics.yaml"
STRICT = (
    ROOT / "runs" / "strict_terminal_constrained_optimization" / "20260525T085000" / "metrics.yaml"
)
ROBUSTNESS = (
    ROOT
    / "runs"
    / "robustness_dependency_frontier_after_v141"
    / "20260525T160000"
    / "metrics.yaml"
)


def build_current_payload(**overrides):
    kwargs = {
        "v145_criterion_path": V145,
        "strict_terminal_path": STRICT,
        "robustness_frontier_path": ROBUSTNESS,
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_current_boundary_has_no_safe_nonrepeating_completion_shortcut() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["user_completion_criterion_met"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True
    assert summary["offline_nonfinal_unresolved_count"] == 2
    assert summary["offline_nonfinal_unresolved_ids"] == [
        "strict_terminal_or_full_staged_feasibility",
        "robustness_to_contact_model_perturbations",
    ]
    assert summary["completion_closing_offline_shortcut_count"] == 0
    assert summary["completion_closing_offline_shortcut_known"] is False
    assert summary["safe_nonrepeating_completion_action_available"] is False
    assert summary["live_or_approval_data_still_blocking"] is True
    assert summary["exact_phase1_approval_still_required"] is True

    rows = {row["blocker_id"]: row for row in payload["boundary_rows"]}
    strict = rows["strict_terminal_or_full_staged_feasibility"]
    assert strict["status"] == "offline_unresolved_nonfinal"
    assert strict["completion_closing_offline_shortcut_known"] is False
    assert strict["safe_nonrepeating_closure_action"] is None
    assert strict["evidence"]["strict_terminal_pass_count"] == 0
    assert strict["evidence"]["best_max_gate_ratio"] > 1.0

    robustness = rows["robustness_to_contact_model_perturbations"]
    assert robustness["status"] == "offline_unresolved_but_closure_dependency_blocked"
    assert robustness["completion_closing_offline_shortcut_known"] is False
    assert robustness["evidence"]["closed_cell_count"] == 0
    assert robustness["evidence"]["accepted_as_robustness_proof"] is False
    assert robustness["evidence"]["additional_failed_cell_execution_recommended"] is False


def test_boundary_rejects_hidden_strict_pass(tmp_path) -> None:
    strict_metrics = yaml.safe_load(STRICT.read_text(encoding="utf-8"))
    strict_metrics["summary"]["strict_terminal_pass_count"] = 1
    strict_metrics["summary"]["strict_paper_equivalent_feasibility"] = True
    drifted = tmp_path / "strict_hidden_pass.yaml"
    drifted.write_text(yaml.safe_dump(strict_metrics, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(strict_terminal_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert any("strict_terminal_pass_count" in v for v in payload["summary"]["violations"])
    assert any("strict_paper_equivalent_feasibility" in v for v in payload["summary"]["violations"])


def test_boundary_rejects_robustness_closure_drift(tmp_path) -> None:
    robustness_metrics = yaml.safe_load(ROBUSTNESS.read_text(encoding="utf-8"))
    robustness_metrics["summary"]["closed_cell_count"] = 4
    robustness_metrics["summary"]["accepted_as_robustness_proof"] = True
    drifted = tmp_path / "robustness_closed.yaml"
    drifted.write_text(yaml.safe_dump(robustness_metrics, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(robustness_frontier_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert any("closed_cell_count" in v for v in payload["summary"]["violations"])
    assert any("accepted_as_robustness_proof" in v for v in payload["summary"]["violations"])


def test_post_v145_offline_blocker_boundary_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "post_v145_offline_blocker_boundary"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_post_v145_offline_blocker_boundary.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_BOUNDARY",
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
    assert metrics["summary"]["completion_closing_offline_shortcut_count"] == 0
    assert metrics["summary"]["completion_claim_allowed"] is False
    assert metrics["summary"]["do_not_mark_goal_complete"] is True
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
