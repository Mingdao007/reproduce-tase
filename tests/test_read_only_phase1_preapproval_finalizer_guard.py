from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_read_only_phase1_preapproval_finalizer_guard import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]

FREEZE = (
    ROOT
    / "runs"
    / "read_only_phase1_approval_request_freeze"
    / "20260525T112000"
    / "metrics.yaml"
)


def build_current_payload(**overrides):
    kwargs = {
        "freeze_path": FREEZE,
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_current_phase1_preapproval_finalizer_guard_rejects_all_cases() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["preapproval_finalizer_guard_complete"] is True
    assert summary["source_freeze_audit_passed"] is True
    assert summary["case_count"] == 5
    assert summary["rejected_case_count"] == 5
    assert summary["scaffold_preserved_case_count"] == 5
    assert summary["approved_read_only_evidence_created_count"] == 0
    assert summary["successful_finalization_count"] == 0
    assert summary["repository_evidence_run_created"] is False
    assert summary["temp_only_dry_run"] is True
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
        "wrong_confirmation_phrase",
        "unknown_step_id",
        "operator_tbd",
        "disallowed_worksheet_rows",
        "missing_required_rows",
    }
    for row in rows.values():
        assert row["returncode"] != 0
        assert row["rejected_as_expected"] is True
        assert row["scaffold_preserved"] is True
        assert row["status_after_attempt"] == "scaffold_created_not_executed"
        assert row["approved_read_only_evidence_created"] is False
        assert row["read_only_evidence_finalization_present"] is False

    assert "approval phrase mismatch" in rows["wrong_confirmation_phrase"]["stderr_excerpt"]
    assert "is not in" in rows["unknown_step_id"]["stderr_excerpt"]
    assert "operator must be non-empty" in rows["operator_tbd"]["stderr_excerpt"]
    assert "does not allow rows in" in rows["disallowed_worksheet_rows"]["stderr_excerpt"]
    assert "at least one worksheet CSV row is required" in rows["missing_required_rows"][
        "stderr_excerpt"
    ]

    boundary = payload["claim_boundary"]
    assert boundary["preapproval_finalizer_guard_only"] is True
    assert boundary["temp_only_dry_run"] is True
    assert boundary["approval_record_created"] is False
    assert boundary["approved_read_only_evidence"] is False
    assert boundary["execution_authorized"] is False
    assert boundary["do_not_mark_goal_complete"] is True


def test_phase1_preapproval_finalizer_guard_rejects_freeze_drift(tmp_path) -> None:
    freeze = yaml.safe_load(FREEZE.read_text(encoding="utf-8"))
    freeze["summary"]["packet_approval_status"] = "approved"
    freeze["summary"]["freeze_authorizes_execution"] = True
    drifted = tmp_path / "freeze.yaml"
    drifted.write_text(yaml.safe_dump(freeze, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(freeze_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["preapproval_finalizer_guard_complete"] is False
    assert "v129 packet approval status is not not_approved" in payload["summary"][
        "violations"
    ]
    assert "v129 summary freeze_authorizes_execution is not false" in payload["summary"][
        "violations"
    ]


def test_phase1_preapproval_finalizer_guard_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "read_only_phase1_preapproval_finalizer_guard"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_phase1_preapproval_finalizer_guard.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_PHASE1_GUARD",
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
    assert metrics["claim_boundary"]["preapproval_finalizer_guard_only"] is True
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
