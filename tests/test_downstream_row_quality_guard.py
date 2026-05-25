from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest
import yaml

from scripts.audit_downstream_row_quality_guard import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]
PHASE1_GUARD = ROOT / "runs" / "phase1_row_quality_guard" / "20260525T120000" / "metrics.yaml"


def build_current_payload(**overrides):
    kwargs = {
        "phase1_guard_path": PHASE1_GUARD,
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_current_downstream_row_quality_guard_rejects_all_invalid_rows() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["downstream_row_quality_guard_complete"] is True
    assert summary["source_phase1_guard_audit_passed"] is True
    assert summary["case_count"] == 4
    assert summary["rejected_case_count"] == 4
    assert summary["scaffold_preserved_case_count"] == 4
    assert summary["approved_read_only_evidence_created_count"] == 0
    assert summary["repository_evidence_run_created"] is False
    assert summary["temp_only_dry_run"] is True
    assert summary["guarded_downstream_step_count"] == 4
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
        "phase2_placeholder_contact_patch_description",
        "phase3_nonunit_plane_normal",
        "phase4_negative_timestamp",
        "phase5_accepted_decision_row",
    }
    for row in rows.values():
        assert row["returncode"] != 0
        assert row["rejected_as_expected"] is True
        assert row["scaffold_preserved"] is True
        assert row["status_after_attempt"] == "scaffold_created_not_executed"
        assert row["approved_read_only_evidence_created"] is False
        assert row["read_only_evidence_finalization_present"] is False

    assert "contact_patch_description must be non-empty" in rows[
        "phase2_placeholder_contact_patch_description"
    ]["stderr_excerpt"]
    assert "normal_vector must have unit length" in rows["phase3_nonunit_plane_normal"][
        "stderr_excerpt"
    ]
    assert "timestamp_s must be nonnegative" in rows["phase4_negative_timestamp"][
        "stderr_excerpt"
    ]
    assert "decision must be one of" in rows["phase5_accepted_decision_row"]["stderr_excerpt"]

    boundary = payload["claim_boundary"]
    assert boundary["downstream_row_quality_guard_only"] is True
    assert boundary["approved_read_only_evidence"] is False
    assert boundary["live_hardware_access_authorized"] is False
    assert boundary["execution_authorized"] is False
    assert boundary["do_not_mark_goal_complete"] is True


def test_downstream_row_quality_guard_rejects_source_phase1_guard_drift(tmp_path) -> None:
    source = yaml.safe_load(PHASE1_GUARD.read_text(encoding="utf-8"))
    source["summary"]["phase1_row_quality_guard_complete"] = False
    source["summary"]["approved_read_only_evidence_created"] = True
    drifted = tmp_path / "phase1_guard.yaml"
    drifted.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(phase1_guard_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["downstream_row_quality_guard_complete"] is False
    assert "v133 source summary phase1_row_quality_guard_complete is False, expected True" in payload[
        "summary"
    ]["violations"]
    assert "v133 source summary approved_read_only_evidence_created is True, expected False" in payload[
        "summary"
    ]["violations"]


def test_downstream_row_quality_guard_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "downstream_row_quality_guard"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_downstream_row_quality_guard.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_DOWNSTREAM_ROW_QUALITY",
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
    assert metrics["summary"]["rejected_case_count"] == 4
    assert metrics["summary"]["approved_read_only_evidence_created"] is False
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()


@pytest.mark.parametrize(
    ("step_id", "worksheet", "row", "evidence_key"),
    [
        (
            "phase2_ksm_contact_patch_convention",
            "ksm_contact_patch_convention.csv",
            "sample_001,ksm_fixture,flat leading face,fully seated against witness marks,visual_inspection,pytest,synthetic test row\n",
            "ksm_contact_patch_convention",
        ),
        (
            "phase3_plane_normal_external_measurement",
            "plane_normal_measurements.csv",
            "sample_001,external_metrology_fixture,0.0,0.0,1.0,0.03,synthetic test row\n",
            "plane_normal_robot_base_frame",
        ),
        (
            "phase4_force_source_read_only_comparison",
            "force_source_comparison.csv",
            "0.0,ur_rtde,0.0,0.0,32.0,0.0,0.0,0.0,bias_unchanged,base,synthetic test row\n",
            "force_source_frame_reconciliation",
        ),
        (
            "phase5_orientation_gate_semantics_evidence",
            "orientation_gate_semantics.csv",
            "sample_001,normal_alignment,0.119,plane_normal_fixture,contact_fixture,0.03,14.0,unresolved,pytest,synthetic test row\n",
            "orientation_gate_semantics",
        ),
    ],
)
def test_finalize_accepts_valid_downstream_rows(
    tmp_path,
    step_id: str,
    worksheet: str,
    row: str,
    evidence_key: str,
) -> None:
    run_dir = tmp_path / "readonly_measurement"
    audit_dir = tmp_path / "audit"
    subprocess.run(
        [
            sys.executable,
            "scripts/create_read_only_calibration_measurement_run.py",
            "--output-dir",
            str(run_dir),
            "--run-id",
            "TEST_RUN",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    worksheet_path = run_dir / worksheet
    worksheet_path.write_text(worksheet_path.read_text(encoding="utf-8") + row, encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/finalize_read_only_calibration_measurement_evidence.py",
            str(run_dir),
            "--confirmation-phrase",
            "I approve this read-only measurement step",
            "--approved-step-id",
            step_id,
            "--operator",
            "pytest",
            "--live-hardware-accessed",
            "false",
            "--finalized-at-utc",
            "2026-05-25T00:00:00Z",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.strip() == str(run_dir.resolve())
    metrics = yaml.safe_load((run_dir / "metrics.yaml").read_text(encoding="utf-8"))
    assert metrics["status"] == "approved_read_only_evidence"
    assert metrics["evidence_status"][evidence_key] == "collected_read_only"
    assert metrics["read_only_evidence_finalization"]["approved_step_id"] == step_id
    assert metrics["read_only_evidence_finalization"]["allowed_worksheets"] == [worksheet]
    assert metrics["read_only_evidence_finalization"]["worksheet_row_counts"][worksheet] == 1
    assert metrics["execution"]["robot_motion_commanded"] is False
    assert metrics["claim_boundary"]["hardware_readiness"] is False

    subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_calibration_measurement_run.py",
            str(run_dir),
            "--audit-mode",
            "approved-read-only",
            "--output-dir",
            str(audit_dir),
            "--run-id",
            "TEST_AUDIT",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    audit = yaml.safe_load((audit_dir / "metrics.yaml").read_text(encoding="utf-8"))
    assert audit["audit_mode"] == "approved-read-only"
    assert audit["audit_passed"] is True
    assert audit["violations"] == []
