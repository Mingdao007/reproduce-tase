from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_user_completion_criterion_after_v144 import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]
POST_V143_GATE = ROOT / "runs" / "post_v142_completion_gate" / "20260525T170000" / "metrics.yaml"
PHASE1_FRESHNESS = (
    ROOT / "runs" / "phase1_packet_freshness_after_v143" / "20260525T180000" / "metrics.yaml"
)


def build_current_payload(**overrides):
    kwargs = {
        "post_v143_gate_path": POST_V143_GATE,
        "phase1_freshness_path": PHASE1_FRESHNESS,
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_user_completion_criterion_fails_when_offline_blockers_remain() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["answer"] == "not_complete_not_only_real_data_missing"
    assert summary["user_completion_criterion_met"] is False
    assert summary["only_real_or_explicit_approval_data_missing"] is False
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True
    assert summary["incomplete_requirement_count"] == 6
    assert summary["approval_or_live_data_blocked_count"] == 4
    assert summary["offline_nonfinal_unresolved_count"] == 2
    assert summary["offline_nonfinal_unresolved_ids"] == [
        "strict_terminal_or_full_staged_feasibility",
        "robustness_to_contact_model_perturbations",
    ]
    assert summary["approval_or_live_data_blocked_ids"] == [
        "approved_read_only_calibration_evidence",
        "contact_setup_target_acceptance",
        "orientation_gate_acceptance",
        "hardware_readiness",
    ]
    assert summary["phase1_packet_fresh"] is True
    assert summary["phase1_packet_still_not_approved"] is True
    assert summary["live_access_authorized_now"] is False
    assert summary["execution_authorized_now"] is False

    boundary = payload["claim_boundary"]
    assert boundary["post_hoc_audit_only"] is True
    assert boundary["live_hardware_access_authorized"] is False
    assert boundary["strict_paper_equivalent_feasibility"] is False
    assert boundary["robustness_claim"] is False
    assert boundary["do_not_mark_goal_complete"] is True


def test_user_completion_criterion_would_pass_only_when_all_incomplete_are_live_blocked(
    tmp_path,
) -> None:
    metrics = yaml.safe_load(POST_V143_GATE.read_text(encoding="utf-8"))
    checklist = metrics["completion_checklist"]
    metrics["completion_checklist"] = [
        row for row in checklist if row["requires_explicit_approval"] is True
    ]
    metrics["summary"]["incomplete_requirement_count"] = len(metrics["completion_checklist"])
    metrics["summary"]["incomplete_requirement_ids"] = [
        row["requirement_id"] for row in metrics["completion_checklist"]
    ]
    live_only = tmp_path / "post_gate_live_only.yaml"
    live_only.write_text(yaml.safe_dump(metrics, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(post_v143_gate_path=live_only)
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["user_completion_criterion_met"] is True
    assert summary["only_real_or_explicit_approval_data_missing"] is True
    assert summary["offline_nonfinal_unresolved_count"] == 0
    assert summary["answer"] == "complete_by_user_real_data_only_criterion"


def test_user_completion_criterion_rejects_phase1_approval_drift(tmp_path) -> None:
    metrics = yaml.safe_load(PHASE1_FRESHNESS.read_text(encoding="utf-8"))
    metrics["summary"]["phase1_packet_still_not_approved"] = False
    metrics["summary"]["execution_authorized_now"] = True
    drifted = tmp_path / "phase1_drift.yaml"
    drifted.write_text(yaml.safe_dump(metrics, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(phase1_freshness_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["user_completion_criterion_met"] is False
    assert any("phase1_packet_still_not_approved" in v for v in payload["summary"]["violations"])
    assert any("execution_authorized_now" in v for v in payload["summary"]["violations"])


def test_user_completion_criterion_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "user_completion_criterion"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_user_completion_criterion_after_v144.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_USER_CRITERION",
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
    assert metrics["summary"]["answer"] == "not_complete_not_only_real_data_missing"
    assert metrics["summary"]["user_completion_criterion_met"] is False
    assert metrics["summary"]["offline_nonfinal_unresolved_count"] == 2
    assert metrics["summary"]["completion_claim_allowed"] is False
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
