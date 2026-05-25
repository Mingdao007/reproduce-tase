from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_read_only_phase1_approval_request_freeze import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]

NEXT_STEP_SELECTION = (
    ROOT
    / "runs"
    / "read_only_next_step_selection"
    / "20260525T111000"
    / "metrics.yaml"
)
PACKET_METRICS = (
    ROOT
    / "runs"
    / "read_only_step_approval_packet"
    / "20260525T095500"
    / "metrics.yaml"
)
PACKET_AUDIT = (
    ROOT
    / "runs"
    / "read_only_step_approval_packet_audit"
    / "20260525T095501"
    / "metrics.yaml"
)
PACKET_MARKDOWN = (
    ROOT
    / "runs"
    / "read_only_step_approval_packet"
    / "20260525T095500"
    / "approval_packet.md"
)


def build_current_payload(**overrides):
    kwargs = {
        "next_step_selection_path": NEXT_STEP_SELECTION,
        "packet_metrics_path": PACKET_METRICS,
        "packet_audit_path": PACKET_AUDIT,
        "packet_markdown_path": PACKET_MARKDOWN,
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_current_phase1_approval_request_freeze_is_non_authorizing() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["approval_request_freeze_complete"] is True
    assert summary["frozen_step_id"] == "phase1_mounted_stack_tcp_contact_measurement"
    assert summary["frozen_worksheet"] == "tcp_contact_measurements.csv"
    assert summary["approval_phrase_required"] == "I approve this read-only measurement step"
    assert summary["exact_step_id_required"] is True
    assert summary["packet_status"] == "approval_packet_created_not_approved"
    assert summary["packet_audit_passed"] is True
    assert summary["packet_approval_status"] == "not_approved"
    assert summary["approved_packet_count"] == 0
    assert summary["execution_authorizing_packet_count"] == 0
    assert summary["live_access_authorizing_packet_count"] == 0
    assert summary["approved_read_only_evidence_created"] is False
    assert summary["freeze_authorizes_live_access"] is False
    assert summary["freeze_authorizes_execution"] is False
    assert summary["freeze_creates_approved_evidence"] is False
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True

    frozen = payload["frozen_approval_request"]
    assert frozen["allowed_worksheets"] == ["tcp_contact_measurements.csv"]
    assert frozen["minimum_required_rows"] == {"tcp_contact_measurements.csv": 1}
    assert frozen["required_approved_step_id"] == "phase1_mounted_stack_tcp_contact_measurement"
    assert frozen["fresh_scaffold_required_after_approval"] is True
    assert frozen["approved_read_only_audit_required_after_finalization"] is True
    assert len(frozen["post_approval_command_plan"]) == 4

    packet_freeze = payload["packet_freeze"]
    assert packet_freeze["packet_markdown_sha256"]
    assert packet_freeze["packet_markdown_bytes"] > 500
    assert packet_freeze["approval_request"]["approval_status"] == "not_approved"

    boundary = payload["claim_boundary"]
    assert boundary["approval_request_freeze_only"] is True
    assert boundary["approval_record_created"] is False
    assert boundary["approved_read_only_evidence"] is False
    assert boundary["execution_authorized"] is False
    assert boundary["hardware_readiness"] is False
    assert boundary["do_not_mark_goal_complete"] is True


def test_phase1_approval_request_freeze_rejects_approved_packet_drift(tmp_path) -> None:
    packet = yaml.safe_load(PACKET_METRICS.read_text(encoding="utf-8"))
    packet["approval_request"]["approval_status"] = "approved"
    packet["approval_request"]["operator"] = "synthetic"
    packet["approval_request"]["packet_authorizes_execution"] = True
    drifted = tmp_path / "packet.yaml"
    drifted.write_text(yaml.safe_dump(packet, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(packet_metrics_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["approval_request_freeze_complete"] is False
    assert payload["summary"]["packet_approval_status"] == "approved"
    assert "packet approval status is not not_approved" in payload["summary"]["violations"]
    assert "packet approval_request.operator is not null" in payload["summary"]["violations"]
    assert "packet now authorizes execution" in payload["summary"]["violations"]


def test_phase1_approval_request_freeze_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "read_only_phase1_approval_request_freeze"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_phase1_approval_request_freeze.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_PHASE1_FREEZE",
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
    assert metrics["summary"]["frozen_step_id"] == "phase1_mounted_stack_tcp_contact_measurement"
    assert metrics["summary"]["freeze_authorizes_execution"] is False
    assert metrics["claim_boundary"]["approval_request_freeze_only"] is True
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
