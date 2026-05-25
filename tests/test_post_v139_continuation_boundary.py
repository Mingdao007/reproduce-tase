from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_post_v139_continuation_boundary import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]
V139_STATUS = ROOT / "runs" / "full_reproduction_status_after_v138" / "20260525T130000" / "metrics.yaml"
REGISTRY = ROOT / "configs" / "read_only_sop_step_registry.yaml"
NEXT_SELECTION = ROOT / "runs" / "read_only_next_step_selection" / "20260525T111000" / "metrics.yaml"
EXECUTION_PREFLIGHT = ROOT / "runs" / "read_only_step_execution_preflight" / "20260525T101000" / "metrics.yaml"


def build_current_payload(**overrides):
    kwargs = {
        "v139_status_path": V139_STATUS,
        "registry_path": REGISTRY,
        "next_selection_path": NEXT_SELECTION,
        "execution_preflight_path": EXECUTION_PREFLIGHT,
        "observed_user_request": "019e5d70-5cf8-7553-aa82-1b3cf93759f9 continue",
        "claimed_approved_step_id": "",
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_continuation_boundary_rejects_freeform_continue_as_approval() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["exact_approval_phrase_observed"] is False
    assert summary["exact_registered_step_observed"] is False
    assert summary["approval_is_exact_and_registered"] is False
    assert summary["freeform_continue_is_approval"] is False
    assert summary["selected_safe_continuation_mode"] == "await_exact_phase1_approval_or_nonfinal_offline"
    assert summary["first_read_only_candidate_step_id"] == "phase1_mounted_stack_tcp_contact_measurement"
    assert summary["first_read_only_candidate_worksheet"] == "tcp_contact_measurements.csv"
    assert summary["read_only_sop_can_execute_now"] is False
    assert summary["live_access_authorized_now"] is False
    assert summary["execution_authorized_now"] is False
    assert summary["nonfinal_offline_work_allowed"] is True
    assert summary["strict_policy_terminal_family_exhausted"] is True
    assert summary["repeat_strict_family_recommended"] is False
    assert summary["v139_full_reproduction_complete"] is False
    assert summary["v139_continue_required"] is True
    assert summary["v139_top_blocker"] == "approved_read_only_calibration_evidence"
    assert summary["required_incomplete_ids_present"] is True
    assert summary["approved_read_only_run_count"] == 0
    assert summary["approved_read_only_audit_passed_count"] == 0
    assert summary["do_not_mark_goal_complete"] is True
    assert payload["claim_boundary"]["live_hardware_access"] is False
    assert payload["claim_boundary"]["approval_record_created"] is False
    assert payload["claim_boundary"]["completion_claim_allowed"] is False


def test_continuation_boundary_detects_exact_phrase_but_still_does_not_execute() -> None:
    payload = build_current_payload(
        observed_user_request="I approve this read-only measurement step",
        claimed_approved_step_id="phase1_mounted_stack_tcp_contact_measurement",
    )
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["exact_approval_phrase_observed"] is True
    assert summary["exact_registered_step_observed"] is True
    assert summary["approval_is_exact_and_registered"] is True
    assert summary["selected_safe_continuation_mode"] == "exact_approval_detected_but_audit_does_not_execute"
    assert summary["read_only_sop_can_execute_now"] is True
    assert summary["live_access_authorized_now"] is False
    assert summary["execution_authorized_now"] is False
    assert summary["nonfinal_offline_work_allowed"] is False
    assert payload["claim_boundary"]["live_hardware_access_authorized"] is False
    assert payload["claim_boundary"]["execution_authorized"] is False


def test_continuation_boundary_rejects_completion_drift(tmp_path) -> None:
    status = yaml.safe_load(V139_STATUS.read_text(encoding="utf-8"))
    status["summary"]["full_reproduction_complete"] = True
    status["summary"]["continue_required"] = False
    drifted = tmp_path / "v139_status.yaml"
    drifted.write_text(yaml.safe_dump(status, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(v139_status_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert "v139 summary full_reproduction_complete is True, expected False" in payload[
        "summary"
    ]["violations"]
    assert "v139 summary continue_required is False, expected True" in payload["summary"][
        "violations"
    ]


def test_continuation_boundary_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "post_v139_continuation_boundary"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_post_v139_continuation_boundary.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_BOUNDARY",
            "--observed-user-request",
            "continue",
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
    assert metrics["summary"]["freeform_continue_is_approval"] is False
    assert metrics["summary"]["read_only_sop_can_execute_now"] is False
    assert metrics["claim_boundary"]["live_hardware_access"] is False
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
