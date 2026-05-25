from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_read_only_evidence_dependency_map import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]


def build_current_payload(**overrides):
    kwargs = {
        "registry_path": ROOT / "configs" / "read_only_sop_step_registry.yaml",
        "measured_geometry_path": ROOT
        / "runs"
        / "measured_geometry_readiness"
        / "20260525T000739"
        / "metrics.yaml",
        "remaining_blockers_path": ROOT
        / "runs"
        / "remaining_blocker_prioritization"
        / "20260525T072557"
        / "metrics.yaml",
        "relaxation_budget_path": ROOT
        / "runs"
        / "strict_terminal_relaxation_budget"
        / "20260525T105000"
        / "metrics.yaml",
        "packet_coverage_path": ROOT
        / "runs"
        / "read_only_step_approval_packet_coverage"
        / "20260525T100500"
        / "metrics.yaml",
        "preflight_path": ROOT
        / "runs"
        / "read_only_step_execution_preflight"
        / "20260525T101000"
        / "metrics.yaml",
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_current_dependency_map_is_complete_but_non_evidence() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["dependency_map_complete"] is True
    assert summary["mapped_readiness_check_count"] == 5
    assert summary["finalizer_step_count"] == 5
    assert summary["mapped_step_count"] == 5
    assert summary["packet_covered_step_count"] == 5
    assert summary["preflight_ready_step_count"] == 5
    assert summary["approved_packet_count"] == 0
    assert summary["execution_authorizing_packet_count"] == 0
    assert summary["live_access_authorizing_packet_count"] == 0
    assert summary["approved_read_only_evidence_created"] is False
    assert summary["explicit_user_approval_required"] is True
    assert summary["live_access_authorized"] is False
    assert summary["execution_authorized"] is False
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True

    rows = {row["step_id"]: row for row in payload["step_dependency_rows"]}
    assert set(rows) == {
        "phase1_mounted_stack_tcp_contact_measurement",
        "phase2_ksm_contact_patch_convention",
        "phase3_plane_normal_external_measurement",
        "phase4_force_source_read_only_comparison",
        "phase5_orientation_gate_semantics_evidence",
    }
    phase1 = rows["phase1_mounted_stack_tcp_contact_measurement"]
    assert phase1["readiness_check"] == "mounted_stack_tcp_contact_point"
    assert phase1["worksheet"] == "tcp_contact_measurements.csv"
    assert phase1["packet_coverage_passed"] is True
    assert phase1["preflight_ready"] is True
    assert phase1["approval_required"] is True
    assert phase1["creates_completion_evidence"] is False

    blockers = {row["blocker_id"]: row for row in payload["blocker_dependency_rows"]}
    strict = blockers["strict_paper_equivalent_full_staged_feasibility"]
    assert strict["required_step_ids"] == list(rows)
    assert strict["all_packets_covered"] is True
    assert strict["all_preflight_ready"] is True
    assert strict["completion_claim_allowed"] is False
    assert strict["status"] == "packet_preflight_ready_but_approval_missing"

    boundary = payload["claim_boundary"]
    assert boundary["dependency_map_only"] is True
    assert boundary["approved_read_only_evidence"] is False
    assert boundary["strict_paper_equivalent_feasibility"] is False
    assert boundary["hardware_readiness"] is False
    assert boundary["robot_motion_authorized"] is False
    assert boundary["hardware_writes_authorized"] is False
    assert boundary["force_control_authorized"] is False
    assert boundary["do_not_mark_goal_complete"] is True


def test_dependency_map_rejects_missing_preflight_ready_step(tmp_path) -> None:
    preflight = yaml.safe_load(
        (
            ROOT
            / "runs"
            / "read_only_step_execution_preflight"
            / "20260525T101000"
            / "metrics.yaml"
        ).read_text(encoding="utf-8")
    )
    for row in preflight["preflight_rows"]:
        if row["step_id"] == "phase3_plane_normal_external_measurement":
            row["preflight_ready"] = False
            row["violations"] = ["synthetic missing preflight readiness"]
            break
    preflight["summary"]["preflight_ready_step_count"] = 4
    preflight["summary"]["missing_ready_step_ids"] = [
        "phase3_plane_normal_external_measurement"
    ]
    drifted = tmp_path / "preflight.yaml"
    drifted.write_text(yaml.safe_dump(preflight, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(preflight_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["dependency_map_complete"] is False
    assert payload["summary"]["preflight_ready_step_count"] == 4
    assert any(
        "phase3_plane_normal_external_measurement" in violation
        for violation in payload["summary"]["violations"]
    )


def test_dependency_map_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "read_only_evidence_dependency_map"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_evidence_dependency_map.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_DEPENDENCY_MAP",
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
    assert metrics["summary"]["dependency_map_complete"] is True
    assert metrics["summary"]["approved_read_only_evidence_created"] is False
    assert metrics["claim_boundary"]["dependency_map_only"] is True
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
