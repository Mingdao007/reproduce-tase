from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_read_only_next_step_selection import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]


DEPENDENCY_MAP = (
    ROOT
    / "runs"
    / "read_only_evidence_dependency_map"
    / "20260525T110000"
    / "metrics.yaml"
)


def build_current_payload(**overrides):
    kwargs = {
        "dependency_map_path": DEPENDENCY_MAP,
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_current_next_step_selection_is_non_authorizing() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["selection_plan_complete"] is True
    assert summary["candidate_step_count"] == 5
    assert summary["recommended_sequence_step_ids"] == [
        "phase1_mounted_stack_tcp_contact_measurement",
        "phase2_ksm_contact_patch_convention",
        "phase3_plane_normal_external_measurement",
        "phase4_force_source_read_only_comparison",
        "phase5_orientation_gate_semantics_evidence",
    ]
    assert summary["first_candidate_step_id"] == "phase1_mounted_stack_tcp_contact_measurement"
    assert summary["first_candidate_worksheet"] == "tcp_contact_measurements.csv"
    assert summary["approval_phrase_required"] == "I approve this read-only measurement step"
    assert summary["exact_step_id_required"] is True
    assert summary["approved_packet_count"] == 0
    assert summary["execution_authorizing_packet_count"] == 0
    assert summary["live_access_authorizing_packet_count"] == 0
    assert summary["approved_read_only_evidence_created"] is False
    assert summary["explicit_user_approval_required"] is True
    assert summary["selection_authorizes_live_access"] is False
    assert summary["selection_authorizes_execution"] is False
    assert summary["selection_creates_approved_evidence"] is False
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["do_not_mark_goal_complete"] is True

    first = payload["first_candidate"]
    assert first["step_id"] == "phase1_mounted_stack_tcp_contact_measurement"
    assert first["supported_blocker_count"] == 6
    assert first["packet_coverage_passed"] is True
    assert first["preflight_ready"] is True
    assert first["approval_record_exists_now"] is False
    assert first["selection_authorizes_execution"] is False

    phase4_frontier = payload["dependency_frontier_rows"][3]
    assert phase4_frontier["after_step_id"] == "phase4_force_source_read_only_comparison"
    assert phase4_frontier["dependency_only_newly_coverable_blockers"] == [
        "calibrated_contact_geometry"
    ]
    phase5_frontier = payload["dependency_frontier_rows"][4]
    assert phase5_frontier["after_step_id"] == "phase5_orientation_gate_semantics_evidence"
    assert set(phase5_frontier["dependency_only_newly_coverable_blockers"]) == {
        "approved_read_only_calibration_evidence",
        "orientation_gate_acceptance",
        "strict_paper_equivalent_full_staged_feasibility",
        "robustness_to_contact_model_perturbations",
        "hardware_readiness",
    }

    boundary = payload["claim_boundary"]
    assert boundary["selection_audit_only"] is True
    assert boundary["approved_read_only_evidence"] is False
    assert boundary["execution_authorized"] is False
    assert boundary["hardware_readiness"] is False
    assert boundary["do_not_mark_goal_complete"] is True


def test_next_step_selection_rejects_approved_packet_drift(tmp_path) -> None:
    dependency_map = yaml.safe_load(DEPENDENCY_MAP.read_text(encoding="utf-8"))
    dependency_map["summary"]["approved_packet_count"] = 1
    drifted = tmp_path / "dependency_map.yaml"
    drifted.write_text(yaml.safe_dump(dependency_map, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(dependency_map_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert payload["summary"]["selection_plan_complete"] is False
    assert payload["summary"]["approved_packet_count"] == 1
    assert "v127 dependency-map source contains approved packets" in payload["summary"][
        "violations"
    ]


def test_next_step_selection_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "read_only_next_step_selection"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_next_step_selection.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_NEXT_STEP_SELECTION",
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
    assert metrics["summary"]["first_candidate_step_id"] == (
        "phase1_mounted_stack_tcp_contact_measurement"
    )
    assert metrics["summary"]["selection_authorizes_execution"] is False
    assert metrics["claim_boundary"]["selection_audit_only"] is True
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
