from __future__ import annotations

import json
import subprocess
import sys

import yaml


def test_create_orientation_gate_acceptance_review_keeps_gate_not_accepted(tmp_path) -> None:
    out_dir = tmp_path / "gate_review"
    command = [
        sys.executable,
        "scripts/create_orientation_gate_acceptance_review.py",
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
        "gate_acceptance_review.md",
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
    assert metrics["template_source"] == "templates/orientation_gate_acceptance_review"
    assert metrics["source_evidence"]["source_read_only_run"] is None
    assert metrics["source_evidence"]["approved_read_only_audit_passed"] is False
    assert metrics["review_execution"]["user_approved_gate_acceptance_review"] is False
    assert metrics["review_execution"]["live_hardware_accessed"] is False
    assert metrics["review_execution"]["robot_motion_commanded"] is False
    assert metrics["review_execution"]["configuration_written"] is False
    assert metrics["review_execution"]["zeroing_or_biasing_performed"] is False
    assert metrics["review_execution"]["force_control_run"] is False
    assert metrics["orientation_gate_acceptance"]["decision"] == "not_accepted"
    assert metrics["orientation_gate_acceptance"]["review_only"] is True
    assert metrics["orientation_gate_acceptance"]["accepted_gate_value_rad"] is None
    assert metrics["orientation_gate_acceptance"]["reviewer"] is None
    assert metrics["verdict"]["supports_gate_relaxation"] is False
    assert metrics["verdict"]["supports_hardware_claim"] is False
    assert metrics["claim_boundary"]["hardware_readiness"] is False


def test_audit_orientation_gate_acceptance_review_accepts_scaffold(tmp_path) -> None:
    review_dir = tmp_path / "gate_review"
    audit_dir = tmp_path / "audit"
    subprocess.run(
        [
            sys.executable,
            "scripts/create_orientation_gate_acceptance_review.py",
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
            "scripts/audit_orientation_gate_acceptance_review.py",
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
    assert audit["orientation_gate_acceptance"]["decision"] == "not_accepted"
    assert audit["verdict"]["supports_gate_relaxation"] is False
    assert audit["claim_boundary"]["hardware_readiness"] is False


def test_audit_orientation_gate_acceptance_review_rejects_acceptance_drift(tmp_path) -> None:
    review_dir = tmp_path / "gate_review"
    audit_dir = tmp_path / "audit"
    subprocess.run(
        [
            sys.executable,
            "scripts/create_orientation_gate_acceptance_review.py",
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
    metrics["orientation_gate_acceptance"]["decision"] = "accepted"
    metrics["orientation_gate_acceptance"]["accepted_gate_value_rad"] = 0.119
    metrics["verdict"]["supports_gate_relaxation"] = True
    (review_dir / "metrics.yaml").write_text(yaml.safe_dump(metrics, sort_keys=False), encoding="utf-8")
    (review_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_orientation_gate_acceptance_review.py",
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
    assert "orientation_gate_acceptance.decision is not not_accepted" in audit["violations"]
    assert "expected null field is not null: orientation_gate_acceptance.accepted_gate_value_rad" in audit[
        "violations"
    ]
    assert "expected false field is not false: verdict.supports_gate_relaxation" in audit["violations"]
