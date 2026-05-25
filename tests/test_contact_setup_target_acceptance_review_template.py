from __future__ import annotations

import json
import subprocess
import sys

import yaml


def test_create_contact_setup_target_acceptance_review_keeps_definition_not_accepted(tmp_path) -> None:
    out_dir = tmp_path / "contact_setup_review"
    command = [
        sys.executable,
        "scripts/create_contact_setup_target_acceptance_review.py",
        "--output-dir",
        str(out_dir),
        "--review-id",
        "TEST_REVIEW",
    ]

    completed = subprocess.run(command, cwd="/home/andy/reproduce-tase", text=True, capture_output=True, check=True)

    assert completed.stdout.strip() == str(out_dir)
    expected_files = {
        "README.md",
        "review_plan.md",
        "contact_setup_target_acceptance_review.md",
        "metrics.yaml",
        "metrics.json",
        "summary.md",
        "git_state.md",
    }
    assert expected_files.issubset({path.name for path in out_dir.iterdir()})

    metrics = yaml.safe_load((out_dir / "metrics.yaml").read_text(encoding="utf-8"))
    metrics_json = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))
    assert metrics_json == metrics
    assert metrics["review_id"] == "TEST_REVIEW"
    assert metrics["status"] == "review_scaffold_not_executed"
    assert metrics["template_source"] == "templates/contact_setup_target_acceptance_review"
    assert metrics["source_evidence"]["source_read_only_run"] is None
    assert metrics["source_evidence"]["approved_read_only_audit_passed"] is False
    assert metrics["source_evidence"]["latest_terminal_optimization"].endswith(
        "runs/strict_terminal_constrained_optimization/20260525T085000/metrics.yaml"
    )
    assert metrics["source_evidence"]["terminal_optimization_reviewed"] is False
    assert metrics["review_execution"]["user_approved_contact_setup_target_review"] is False
    assert metrics["review_execution"]["live_hardware_accessed"] is False
    assert metrics["review_execution"]["robot_motion_commanded"] is False
    assert metrics["review_execution"]["configuration_written"] is False
    assert metrics["review_execution"]["zeroing_or_biasing_performed"] is False
    assert metrics["review_execution"]["force_control_run"] is False
    assert metrics["terminal_compatibility_context"]["strict_terminal_pass_count"] == 0
    assert metrics["contact_setup_target_acceptance"]["decision"] == "not_accepted"
    assert metrics["contact_setup_target_acceptance"]["review_only"] is True
    assert metrics["contact_setup_target_acceptance"]["accepted_contact_model"] is None
    assert metrics["contact_setup_target_acceptance"]["accepted_setup_target_label"] is None
    assert metrics["verdict"]["supports_contact_model_update"] is False
    assert metrics["verdict"]["supports_setup_target_update"] is False
    assert metrics["verdict"]["supports_hardware_claim"] is False
    assert metrics["claim_boundary"]["hardware_readiness"] is False
    assert metrics["claim_boundary"]["do_not_mark_goal_complete"] is True


def test_audit_contact_setup_target_acceptance_review_accepts_scaffold(tmp_path) -> None:
    review_dir = tmp_path / "contact_setup_review"
    audit_dir = tmp_path / "audit"
    subprocess.run(
        [
            sys.executable,
            "scripts/create_contact_setup_target_acceptance_review.py",
            "--output-dir",
            str(review_dir),
            "--review-id",
            "TEST_REVIEW",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_contact_setup_target_acceptance_review.py",
            str(review_dir),
            "--output-dir",
            str(audit_dir),
            "--run-id",
            "TEST_AUDIT",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.strip() == str(audit_dir)
    audit = yaml.safe_load((audit_dir / "metrics.yaml").read_text(encoding="utf-8"))
    audit_json = json.loads((audit_dir / "metrics.json").read_text(encoding="utf-8"))
    assert audit_json == audit
    assert audit["audit_passed"] is True
    assert audit["violations"] == []
    assert audit["review_status"] == "review_scaffold_not_executed"
    assert audit["contact_setup_target_acceptance"]["decision"] == "not_accepted"
    assert audit["verdict"]["supports_contact_model_update"] is False
    assert audit["claim_boundary"]["hardware_readiness"] is False
    assert audit["claim_boundary"]["do_not_mark_goal_complete"] is True


def test_audit_contact_setup_target_acceptance_review_rejects_acceptance_drift(tmp_path) -> None:
    review_dir = tmp_path / "contact_setup_review"
    audit_dir = tmp_path / "audit"
    subprocess.run(
        [
            sys.executable,
            "scripts/create_contact_setup_target_acceptance_review.py",
            "--output-dir",
            str(review_dir),
            "--review-id",
            "TEST_REVIEW",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )
    metrics = yaml.safe_load((review_dir / "metrics.yaml").read_text(encoding="utf-8"))
    metrics["contact_setup_target_acceptance"]["decision"] = "accepted"
    metrics["contact_setup_target_acceptance"]["accepted_contact_model"] = "new_model"
    metrics["verdict"]["supports_contact_model_update"] = True
    metrics["claim_boundary"]["contact_calibration_claim"] = True
    (review_dir / "metrics.yaml").write_text(yaml.safe_dump(metrics, sort_keys=False), encoding="utf-8")
    (review_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_contact_setup_target_acceptance_review.py",
            str(review_dir),
            "--output-dir",
            str(audit_dir),
            "--run-id",
            "TEST_AUDIT",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    audit = yaml.safe_load((audit_dir / "metrics.yaml").read_text(encoding="utf-8"))
    assert audit["audit_passed"] is False
    assert "contact_setup_target_acceptance.decision is not not_accepted" in audit["violations"]
    assert "expected null field is not null: contact_setup_target_acceptance.accepted_contact_model" in audit[
        "violations"
    ]
    assert "expected false field is not false: verdict.supports_contact_model_update" in audit["violations"]
    assert "expected false field is not false: claim_boundary.contact_calibration_claim" in audit[
        "violations"
    ]
