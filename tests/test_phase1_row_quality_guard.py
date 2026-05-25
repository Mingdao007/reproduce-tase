from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_phase1_row_quality_guard import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]
SEQUENCE_BOUNDARY = (
    ROOT
    / "runs"
    / "read_only_evidence_sequence_boundary"
    / "20260525T115000"
    / "metrics.yaml"
)


def build_current_payload(**overrides):
    kwargs = {
        "sequence_boundary_path": SEQUENCE_BOUNDARY,
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_current_phase1_row_quality_guard_rejects_all_invalid_rows() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["phase1_row_quality_guard_complete"] is True
    assert summary["source_sequence_boundary_audit_passed"] is True
    assert summary["case_count"] == 5
    assert summary["rejected_case_count"] == 5
    assert summary["scaffold_preserved_case_count"] == 5
    assert summary["approved_read_only_evidence_created_count"] == 0
    assert summary["repository_evidence_run_created"] is False
    assert summary["temp_only_dry_run"] is True
    assert summary["guarded_step_id"] == "phase1_mounted_stack_tcp_contact_measurement"
    assert summary["guarded_worksheet"] == "tcp_contact_measurements.csv"
    assert summary["approved_packet_count"] == 0
    assert summary["execution_authorizing_packet_count"] == 0
    assert summary["live_access_authorizing_packet_count"] == 0
    assert summary["approved_read_only_evidence_created"] is False
    assert summary["guard_authorizes_live_access"] is False
    assert summary["guard_authorizes_execution"] is False
    assert summary["guard_creates_approved_evidence"] is False
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True

    rows = {row["case_id"]: row for row in payload["rejection_case_rows"]}
    assert set(rows) == {
        "placeholder_datum",
        "invalid_tool_axis_sign",
        "nonnumeric_distance",
        "nonpositive_resolution",
        "placeholder_row_operator",
    }
    for row in rows.values():
        assert row["returncode"] != 0
        assert row["rejected_as_expected"] is True
        assert row["scaffold_preserved"] is True
        assert row["status_after_attempt"] == "scaffold_created_not_executed"
        assert row["approved_read_only_evidence_created"] is False
        assert row["read_only_evidence_finalization_present"] is False

    assert "datum must be non-empty" in rows["placeholder_datum"]["stderr_excerpt"]
    assert "tool_axis_sign must be one of" in rows["invalid_tool_axis_sign"]["stderr_excerpt"]
    assert "distance_mm is not numeric" in rows["nonnumeric_distance"]["stderr_excerpt"]
    assert "resolution_mm must be finite and positive" in rows["nonpositive_resolution"][
        "stderr_excerpt"
    ]
    assert "operator must be non-empty" in rows["placeholder_row_operator"]["stderr_excerpt"]

    boundary = payload["claim_boundary"]
    assert boundary["phase1_row_quality_guard_only"] is True
    assert boundary["approved_read_only_evidence"] is False
    assert boundary["live_hardware_access_authorized"] is False
    assert boundary["execution_authorized"] is False
    assert boundary["do_not_mark_goal_complete"] is True


def test_phase1_row_quality_guard_rejects_sequence_boundary_drift(tmp_path) -> None:
    sequence = yaml.safe_load(SEQUENCE_BOUNDARY.read_text(encoding="utf-8"))
    sequence["summary"]["first_step_id"] = "phase2_ksm_contact_patch_convention"
    sequence["summary"]["completion_claim_allowed"] = True
    drifted = tmp_path / "sequence.yaml"
    drifted.write_text(yaml.safe_dump(sequence, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(sequence_boundary_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["phase1_row_quality_guard_complete"] is False
    assert (
        "v132 source summary first_step_id is 'phase2_ksm_contact_patch_convention', "
        "expected 'phase1_mounted_stack_tcp_contact_measurement'"
    ) in payload["summary"]["violations"]
    assert "v132 source summary completion_claim_allowed is True, expected False" in payload[
        "summary"
    ]["violations"]


def test_phase1_row_quality_guard_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "phase1_row_quality_guard"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_phase1_row_quality_guard.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_ROW_QUALITY",
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
    assert metrics["summary"]["rejected_case_count"] == 5
    assert metrics["summary"]["approved_read_only_evidence_created"] is False
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
