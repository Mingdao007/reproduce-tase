from __future__ import annotations

import json
import subprocess
import sys

import yaml


def test_audit_offline_completion_blockers_reports_incomplete_goal(tmp_path) -> None:
    out_dir = tmp_path / "offline_blockers"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_offline_completion_blockers.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_AUDIT",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.strip() == str(out_dir)
    metrics = yaml.safe_load((out_dir / "metrics.yaml").read_text(encoding="utf-8"))
    metrics_json = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))
    assert metrics_json == metrics
    assert metrics["overall_goal_complete"] is False
    assert metrics["completion_blocked"] is True
    assert metrics["claim_boundary"]["do_not_mark_goal_complete"] is True
    assert metrics["claim_boundary"]["robot_motion_authorized"] is False
    assert metrics["claim_boundary"]["hardware_writes_authorized"] is False
    assert metrics["claim_boundary"]["force_control_authorized"] is False
    assert metrics["claim_boundary"]["hardware_readiness_claim"] is False

    requirements = {item["id"]: item for item in metrics["requirements"]}
    assert requirements["ur10e_adapted_relaxed_simulation"]["achieved"] is True
    assert requirements["strict_paper_equivalent_full_staged_feasibility"]["achieved"] is False
    assert requirements["approved_read_only_calibration_evidence"]["achieved"] is False
    assert requirements["calibrated_contact_geometry"]["achieved"] is False
    assert requirements["orientation_gate_acceptance"]["achieved"] is False
    assert requirements["robustness_to_contact_model_perturbations"]["achieved"] is False
    assert requirements["hardware_readiness"]["achieved"] is False

    assert "strict_paper_equivalent_full_staged_feasibility" in metrics[
        "offline_actionable_nonfinal_requirement_ids"
    ]
    assert "robustness_to_contact_model_perturbations" in metrics[
        "offline_actionable_nonfinal_requirement_ids"
    ]
    assert "approved_read_only_calibration_evidence" in metrics[
        "live_or_explicit_approval_blocked_requirement_ids"
    ]
    assert "hardware_readiness" in metrics["live_or_explicit_approval_blocked_requirement_ids"]


def test_audit_offline_completion_blockers_uses_real_read_only_and_gate_review_state(tmp_path) -> None:
    out_dir = tmp_path / "offline_blockers"
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_offline_completion_blockers.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_AUDIT",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )

    metrics = yaml.safe_load((out_dir / "metrics.yaml").read_text(encoding="utf-8"))
    requirements = {item["id"]: item for item in metrics["requirements"]}
    read_only_evidence = requirements["approved_read_only_calibration_evidence"]["evidence"][0]
    gate_review_evidence = requirements["orientation_gate_acceptance"]["evidence"][0]

    assert read_only_evidence["run_count"] >= 1
    assert read_only_evidence["approved_read_only_run_count"] == 0
    assert all(run["status"] != "approved_read_only_evidence" for run in read_only_evidence["runs"])
    assert gate_review_evidence["review_count"] >= 1
    assert gate_review_evidence["accepted_review_count"] == 0
    assert all(review["decision"] != "accepted" for review in gate_review_evidence["reviews"])
