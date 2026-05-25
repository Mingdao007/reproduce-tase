from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_phase1_packet_freshness_after_v143 import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "configs" / "read_only_sop_step_registry.yaml"
PHASE1_FREEZE = (
    ROOT
    / "runs"
    / "read_only_phase1_approval_request_freeze"
    / "20260525T112000"
    / "metrics.yaml"
)
POST_V143_GATE = ROOT / "runs" / "post_v142_completion_gate" / "20260525T170000" / "metrics.yaml"
NEXT_STEP_SELECTION = (
    ROOT / "runs" / "read_only_next_step_selection" / "20260525T111000" / "metrics.yaml"
)
PACKET_METRICS = ROOT / "runs" / "read_only_step_approval_packet" / "20260525T095500" / "metrics.yaml"
PACKET_AUDIT = (
    ROOT / "runs" / "read_only_step_approval_packet_audit" / "20260525T095501" / "metrics.yaml"
)
PACKET_MARKDOWN = (
    ROOT / "runs" / "read_only_step_approval_packet" / "20260525T095500" / "approval_packet.md"
)


def build_current_payload(**overrides):
    kwargs = {
        "registry_path": REGISTRY,
        "phase1_freeze_path": PHASE1_FREEZE,
        "post_v143_gate_path": POST_V143_GATE,
        "next_step_selection_path": NEXT_STEP_SELECTION,
        "packet_metrics_path": PACKET_METRICS,
        "packet_audit_path": PACKET_AUDIT,
        "packet_markdown_path": PACKET_MARKDOWN,
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_phase1_packet_freshness_current_packet_is_still_not_approved() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["phase1_packet_fresh"] is True
    assert summary["registry_matches_frozen_packet"] is True
    assert summary["packet_hash_unchanged"] is True
    assert summary["frozen_step_id"] == "phase1_mounted_stack_tcp_contact_measurement"
    assert summary["frozen_worksheet"] == "tcp_contact_measurements.csv"
    assert summary["approval_phrase_required"] == "I approve this read-only measurement step"
    assert summary["exact_step_id_required"] is True
    assert summary["phase1_packet_still_not_approved"] is True
    assert summary["post_v143_completion_gate_binding"] is True
    assert summary["approved_read_only_run_count"] == 0
    assert summary["approved_read_only_audit_passed_count"] == 0
    assert summary["readiness_completion_evidence_ids"] == []
    assert summary["approval_record_created"] is False
    assert summary["live_access_authorized_now"] is False
    assert summary["execution_authorized_now"] is False
    assert summary["approved_read_only_evidence_created"] is False
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True

    checks = payload["freshness_checks"]
    assert checks["registry_phase1_step"]["allowed_worksheets"] == [
        "tcp_contact_measurements.csv"
    ]
    assert checks["current_phase1_freeze_summary"]["packet_approval_status"] == "not_approved"
    assert checks["post_v143_gate_summary"]["completion_claim_allowed"] is False

    boundary = payload["claim_boundary"]
    assert boundary["freshness_audit_only"] is True
    assert boundary["approval_record_created"] is False
    assert boundary["approved_read_only_evidence"] is False
    assert boundary["execution_authorized"] is False
    assert boundary["hardware_readiness"] is False
    assert boundary["do_not_mark_goal_complete"] is True


def test_phase1_packet_freshness_rejects_registry_scope_drift(tmp_path) -> None:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    for step in registry["steps"]:
        if step["step_id"] == "phase1_mounted_stack_tcp_contact_measurement":
            step["allowed_worksheets"] = ["tcp_contact_measurements.csv", "force_source_comparison.csv"]
            step["minimum_required_rows"]["force_source_comparison.csv"] = 1
    drifted = tmp_path / "registry.yaml"
    drifted.write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(registry_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["phase1_packet_fresh"] is False
    assert payload["summary"]["registry_matches_frozen_packet"] is False
    assert any("registry phase1 allowed_worksheets" in v for v in payload["summary"]["violations"])
    assert "current packet selected step no longer matches registry phase1 step" in payload[
        "summary"
    ]["violations"]


def test_phase1_packet_freshness_rejects_packet_hash_drift(tmp_path) -> None:
    drifted = tmp_path / "approval_packet.md"
    drifted.write_text(
        PACKET_MARKDOWN.read_text(encoding="utf-8") + "\n<!-- drift -->\n",
        encoding="utf-8",
    )

    payload = build_current_payload(packet_markdown_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["phase1_packet_fresh"] is False
    assert payload["summary"]["packet_hash_unchanged"] is False
    assert "phase1 packet markdown hash changed since v129 freeze" in payload["summary"][
        "violations"
    ]


def test_phase1_packet_freshness_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "phase1_packet_freshness"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_phase1_packet_freshness_after_v143.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_FRESHNESS",
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
    assert metrics["summary"]["phase1_packet_fresh"] is True
    assert metrics["summary"]["packet_hash_unchanged"] is True
    assert metrics["summary"]["completion_claim_allowed"] is False
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
