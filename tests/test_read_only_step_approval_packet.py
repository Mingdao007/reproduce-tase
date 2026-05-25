from __future__ import annotations

import json
import subprocess
import sys

import yaml


def test_create_read_only_step_approval_packet_keeps_packet_not_approved(tmp_path) -> None:
    out_dir = tmp_path / "approval_packet"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/create_read_only_step_approval_packet.py",
            "--step-id",
            "phase1_mounted_stack_tcp_contact_measurement",
            "--output-dir",
            str(out_dir),
            "--packet-id",
            "TEST_PACKET",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.strip() == str(out_dir)
    assert {"approval_packet.md", "metrics.yaml", "metrics.json", "summary.md", "git_state.md"}.issubset(
        {path.name for path in out_dir.iterdir()}
    )
    metrics = yaml.safe_load((out_dir / "metrics.yaml").read_text(encoding="utf-8"))
    metrics_json = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))
    assert metrics_json == metrics
    assert metrics["status"] == "approval_packet_created_not_approved"
    assert metrics["packet_id"] == "TEST_PACKET"
    assert metrics["registry_path"] == "configs/read_only_sop_step_registry.yaml"
    assert metrics["selected_step"]["step_id"] == "phase1_mounted_stack_tcp_contact_measurement"
    assert metrics["selected_step"]["finalizer_eligible"] is True
    assert metrics["selected_step"]["allowed_worksheets"] == ["tcp_contact_measurements.csv"]
    assert metrics["approval_request"]["approval_status"] == "not_approved"
    assert metrics["approval_request"]["required_approved_step_id"] == (
        "phase1_mounted_stack_tcp_contact_measurement"
    )
    assert metrics["approval_request"]["packet_authorizes_execution"] is False
    assert metrics["approval_request"]["packet_authorizes_live_access"] is False
    assert metrics["execution"]["live_hardware_accessed"] is False
    assert metrics["execution"]["robot_motion_commanded"] is False
    assert metrics["claim_boundary"]["approved_read_only_evidence"] is False
    assert metrics["claim_boundary"]["hardware_readiness"] is False
    assert metrics["claim_boundary"]["do_not_mark_goal_complete"] is True
    packet_text = (out_dir / "approval_packet.md").read_text(encoding="utf-8")
    assert "Approval status: `not_approved`" in packet_text
    assert "This packet is not an approval record." in packet_text


def test_audit_read_only_step_approval_packet_accepts_packet(tmp_path) -> None:
    packet_dir = tmp_path / "approval_packet"
    audit_dir = tmp_path / "audit"
    subprocess.run(
        [
            sys.executable,
            "scripts/create_read_only_step_approval_packet.py",
            "--step-id",
            "phase1_mounted_stack_tcp_contact_measurement",
            "--output-dir",
            str(packet_dir),
            "--packet-id",
            "TEST_PACKET",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_step_approval_packet.py",
            str(packet_dir),
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
    assert audit["packet_status"] == "approval_packet_created_not_approved"
    assert audit["selected_step"]["step_id"] == "phase1_mounted_stack_tcp_contact_measurement"
    assert audit["approval_request"]["approval_status"] == "not_approved"
    assert audit["claim_boundary"]["hardware_readiness"] is False
    assert audit["claim_boundary"]["do_not_mark_goal_complete"] is True


def test_audit_read_only_step_approval_packet_rejects_approval_drift(tmp_path) -> None:
    packet_dir = tmp_path / "approval_packet"
    audit_dir = tmp_path / "audit"
    subprocess.run(
        [
            sys.executable,
            "scripts/create_read_only_step_approval_packet.py",
            "--step-id",
            "phase1_mounted_stack_tcp_contact_measurement",
            "--output-dir",
            str(packet_dir),
            "--packet-id",
            "TEST_PACKET",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=True,
    )
    metrics = yaml.safe_load((packet_dir / "metrics.yaml").read_text(encoding="utf-8"))
    metrics["approval_request"]["approval_status"] = "approved"
    metrics["approval_request"]["operator"] = "pytest"
    metrics["approval_request"]["packet_authorizes_execution"] = True
    metrics["execution"]["live_hardware_accessed"] = True
    metrics["claim_boundary"]["hardware_readiness"] = True
    (packet_dir / "metrics.yaml").write_text(yaml.safe_dump(metrics, sort_keys=False), encoding="utf-8")
    (packet_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_step_approval_packet.py",
            str(packet_dir),
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
    assert "approval_request.approval_status is not not_approved" in audit["violations"]
    assert "approval_request.operator is not null" in audit["violations"]
    assert "approval_request.packet_authorizes_execution is not false" in audit["violations"]
    assert "expected false field is not false: execution.live_hardware_accessed" in audit[
        "violations"
    ]
    assert "expected false field is not false: claim_boundary.hardware_readiness" in audit[
        "violations"
    ]


def test_create_read_only_step_approval_packet_rejects_nonfinalizer_step(tmp_path) -> None:
    out_dir = tmp_path / "approval_packet"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/create_read_only_step_approval_packet.py",
            "--step-id",
            "phase0_static_bench_preflight",
            "--output-dir",
            str(out_dir),
            "--packet-id",
            "TEST_PACKET",
        ],
        cwd="/home/andy/reproduce-tase",
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "not finalizer-eligible" in completed.stderr or "not finalizer-eligible" in completed.stdout
    assert not out_dir.exists()
