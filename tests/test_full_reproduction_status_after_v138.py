from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_full_reproduction_status_after_v138 import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]
POST_V138_GATE = ROOT / "runs" / "post_v137_completion_gate" / "20260525T125000" / "metrics.yaml"


def build_current_payload(**overrides):
    kwargs = {
        "post_v138_completion_gate_path": POST_V138_GATE,
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_full_reproduction_status_answers_not_complete() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["user_question_answer"] == "not_fully_reproduced"
    assert summary["full_reproduction_complete"] is False
    assert summary["continue_required"] is True
    assert summary["safe_continuation_mode"] == "explicit_read_only_approval_or_nonfinal_offline"
    assert summary["source_completion_gate_audit_passed"] is True
    assert summary["source_overall_goal_complete"] is False
    assert summary["source_completion_claim_allowed"] is False
    assert summary["source_do_not_mark_goal_complete"] is True
    assert summary["top_blocker"] == "approved_read_only_calibration_evidence"
    assert summary["incomplete_requirement_count"] == 6
    assert summary["required_incomplete_ids_present"] is True
    assert summary["missing_required_incomplete_ids"] == []
    assert summary["approved_read_only_run_count"] == 0
    assert summary["approved_read_only_audit_passed_count"] == 0
    assert summary["accepted_orientation_review_count"] == 0
    assert summary["accepted_contact_setup_target_review_count"] == 0
    assert summary["strict_terminal_pass_count"] == 0
    assert summary["closed_robustness_cell_count"] == 0
    assert summary["hardware_gate_report_exists"] is False
    assert summary["readiness_completion_evidence_ids"] == []
    assert summary["readiness_artifacts_are_non_evidence"] is True
    assert summary["margin_separation_is_non_evidence"] is True
    assert summary["do_not_mark_goal_complete"] is True
    assert payload["claim_boundary"]["full_reproduction_claim_allowed"] is False
    assert payload["claim_boundary"]["live_hardware_access"] is False


def test_status_audit_rejects_source_completion_drift(tmp_path) -> None:
    gate = yaml.safe_load(POST_V138_GATE.read_text(encoding="utf-8"))
    gate["summary"]["overall_goal_complete"] = True
    gate["summary"]["completion_claim_allowed"] = True
    gate["summary"]["do_not_mark_goal_complete"] = False
    drifted = tmp_path / "post_v138.yaml"
    drifted.write_text(yaml.safe_dump(gate, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(post_v138_completion_gate_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["full_reproduction_complete"] is False
    assert payload["summary"]["unexpected_complete_source"] is True
    assert payload["summary"]["unexpected_completion_claim_source"] is True
    assert (
        "post_v138_completion_gate.summary.overall_goal_complete is True, expected False"
        in payload["summary"]["violations"]
    )
    assert (
        "post_v138_completion_gate.summary.completion_claim_allowed is True, expected False"
        in payload["summary"]["violations"]
    )


def test_status_audit_rejects_missing_required_blocker(tmp_path) -> None:
    gate = yaml.safe_load(POST_V138_GATE.read_text(encoding="utf-8"))
    gate["summary"]["incomplete_requirement_ids"].remove("hardware_readiness")
    drifted = tmp_path / "post_v138.yaml"
    drifted.write_text(yaml.safe_dump(gate, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(post_v138_completion_gate_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["required_incomplete_ids_present"] is False
    assert payload["summary"]["missing_required_incomplete_ids"] == ["hardware_readiness"]
    assert "post_v138 completion gate missing incomplete IDs: ['hardware_readiness']" in payload[
        "summary"
    ]["violations"]


def test_status_audit_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "full_reproduction_status_after_v138"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_full_reproduction_status_after_v138.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_STATUS",
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
    assert metrics["summary"]["user_question_answer"] == "not_fully_reproduced"
    assert metrics["summary"]["full_reproduction_complete"] is False
    assert metrics["summary"]["continue_required"] is True
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
