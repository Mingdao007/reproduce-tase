from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_read_only_evidence_sequence_boundary import (
    EXPECTED_SEQUENCE,
    FIRST_STEP_ID,
    FIRST_WORKSHEET,
    build_payload,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]


def build_current_payload(**overrides):
    kwargs = {
        "dependency_map_path": ROOT
        / "runs"
        / "read_only_evidence_dependency_map"
        / "20260525T110000"
        / "metrics.yaml",
        "next_step_selection_path": ROOT
        / "runs"
        / "read_only_next_step_selection"
        / "20260525T111000"
        / "metrics.yaml",
        "acceptance_boundary_path": ROOT
        / "runs"
        / "phase1_approved_evidence_acceptance_boundary"
        / "20260525T114000"
        / "metrics.yaml",
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_current_read_only_sequence_boundary_keeps_phase1_first_and_nonfinal() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["sequence_boundary_complete"] is True
    assert summary["ordered_step_count"] == 5
    assert summary["expected_step_count"] == 5
    assert summary["first_step_id"] == FIRST_STEP_ID
    assert summary["first_worksheet"] == FIRST_WORKSHEET
    assert summary["remaining_step_count_after_phase1"] == 4
    assert summary["remaining_step_ids_after_phase1"] == EXPECTED_SEQUENCE[1:]
    assert summary["all_steps_packet_covered"] is True
    assert summary["all_steps_preflight_ready"] is True
    assert summary["all_steps_separate_approval_required"] is True
    assert summary["phase1_alone_completes_measured_geometry_chain"] is False
    assert summary["phase1_alone_completes_overall_goal"] is False
    assert summary["current_approved_read_only_run_count"] == 0
    assert summary["current_phase1_approved_read_only_run_count"] == 0
    assert summary["current_finalization_record_count"] == 0
    assert summary["current_approved_read_only_audit_passed_count"] == 0
    assert summary["approved_packet_count"] == 0
    assert summary["execution_authorizing_packet_count"] == 0
    assert summary["live_access_authorizing_packet_count"] == 0
    assert summary["bundle_approval_authorized"] is False
    assert summary["approved_read_only_evidence_created"] is False
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True

    rows = payload["sequence_rows"]
    assert [row["step_id"] for row in rows] == EXPECTED_SEQUENCE
    assert rows[0]["chain_role"] == "first_selected_phase1"
    assert rows[0]["would_remain_after_phase1_only"] is False
    assert all(row["separate_exact_user_approval_required"] is True for row in rows)
    assert all(row["bundle_authorized"] is False for row in rows)
    assert [row["step_id"] for row in rows if row["would_remain_after_phase1_only"]] == (
        EXPECTED_SEQUENCE[1:]
    )

    boundary = payload["claim_boundary"]
    assert boundary["sequence_boundary_only"] is True
    assert boundary["approved_read_only_evidence"] is False
    assert boundary["phase1_alone_completes_overall_goal"] is False
    assert boundary["bundle_approval_authorized"] is False
    assert boundary["execution_authorized"] is False


def test_sequence_boundary_rejects_missing_downstream_step(tmp_path) -> None:
    dependency = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "read_only_evidence_dependency_map"
            / "20260525T110000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    dependency["summary"]["mapped_step_count"] = 4
    dependency["step_dependency_rows"] = [
        row
        for row in dependency["step_dependency_rows"]
        if row["step_id"] != "phase5_orientation_gate_semantics_evidence"
    ]
    drifted = tmp_path / "dependency.yaml"
    drifted.write_text(yaml.safe_dump(dependency, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(dependency_map_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["sequence_boundary_complete"] is False
    assert "v127.summary.mapped_step_count is 4, expected 5" in payload["summary"][
        "violations"
    ]
    assert (
        "v127.step_dependency_rows missing expected step: phase5_orientation_gate_semantics_evidence"
        in payload["summary"]["violations"]
    )


def test_sequence_boundary_rejects_approval_or_authorization_drift(tmp_path) -> None:
    acceptance = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "phase1_approved_evidence_acceptance_boundary"
            / "20260525T114000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    acceptance["summary"]["approved_read_only_run_count"] = 1
    acceptance["summary"]["execution_authorized"] = True
    drifted = tmp_path / "acceptance.yaml"
    drifted.write_text(yaml.safe_dump(acceptance, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(acceptance_boundary_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["current_approved_read_only_run_count"] == 1
    assert "v131.summary.approved_read_only_run_count is 1, expected 0" in payload[
        "summary"
    ]["violations"]
    assert "v131.summary.execution_authorized is not false" in payload["summary"][
        "violations"
    ]


def test_read_only_sequence_boundary_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "read_only_evidence_sequence_boundary"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_evidence_sequence_boundary.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_SEQUENCE_BOUNDARY",
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
    assert metrics["summary"]["remaining_step_count_after_phase1"] == 4
    assert metrics["summary"]["phase1_alone_completes_overall_goal"] is False
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
