from __future__ import annotations

import json
import subprocess
import sys

import yaml


ROOT = "/home/andy/reproduce-tase"
FINALIZER_STEPS = [
    "phase1_mounted_stack_tcp_contact_measurement",
    "phase2_ksm_contact_patch_convention",
    "phase3_plane_normal_external_measurement",
    "phase4_force_source_read_only_comparison",
    "phase5_orientation_gate_semantics_evidence",
]


def create_packet_and_audit(tmp_path, step_id: str) -> tuple[object, object]:
    packet_dir = tmp_path / "packets" / step_id
    audit_dir = tmp_path / "audits" / step_id
    subprocess.run(
        [
            sys.executable,
            "scripts/create_read_only_step_approval_packet.py",
            "--step-id",
            step_id,
            "--output-dir",
            str(packet_dir),
            "--packet-id",
            f"TEST_{step_id}",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_step_approval_packet.py",
            str(packet_dir),
            "--output-dir",
            str(audit_dir),
            "--run-id",
            f"TEST_AUDIT_{step_id}",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return packet_dir, audit_dir


def run_coverage(tmp_path, *, check: bool) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_step_approval_packet_coverage.py",
            "--packet-root",
            str(tmp_path / "packets"),
            "--audit-root",
            str(tmp_path / "audits"),
            "--output-dir",
            str(tmp_path / "coverage"),
            "--run-id",
            "TEST_COVERAGE",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def test_coverage_audit_accepts_all_finalizer_steps(tmp_path) -> None:
    for step_id in FINALIZER_STEPS:
        create_packet_and_audit(tmp_path, step_id)

    completed = run_coverage(tmp_path, check=True)

    assert completed.stdout.strip() == str(tmp_path / "coverage")
    metrics = yaml.safe_load((tmp_path / "coverage" / "metrics.yaml").read_text(encoding="utf-8"))
    metrics_json = json.loads((tmp_path / "coverage" / "metrics.json").read_text(encoding="utf-8"))
    assert metrics_json == metrics
    assert metrics["summary"]["audit_passed"] is True
    assert metrics["summary"]["coverage_complete"] is True
    assert metrics["summary"]["covered_step_count"] == 5
    assert metrics["summary"]["required_finalizer_step_count"] == 5
    assert metrics["summary"]["missing_step_ids"] == []
    assert metrics["summary"]["approved_packet_count"] == 0
    assert metrics["summary"]["execution_authorizing_packet_count"] == 0
    assert metrics["summary"]["live_access_authorizing_packet_count"] == 0
    assert metrics["summary"]["do_not_mark_goal_complete"] is True
    assert metrics["claim_boundary"]["approved_read_only_evidence"] is False
    assert metrics["claim_boundary"]["hardware_readiness"] is False
    assert metrics["claim_boundary"]["do_not_mark_goal_complete"] is True
    assert {row["step_id"] for row in metrics["coverage_rows"]} == set(FINALIZER_STEPS)
    assert all(row["coverage_passed"] is True for row in metrics["coverage_rows"])


def test_coverage_audit_rejects_missing_finalizer_steps(tmp_path) -> None:
    create_packet_and_audit(tmp_path, FINALIZER_STEPS[0])

    completed = run_coverage(tmp_path, check=False)

    assert completed.returncode == 1
    metrics = yaml.safe_load((tmp_path / "coverage" / "metrics.yaml").read_text(encoding="utf-8"))
    assert metrics["summary"]["audit_passed"] is False
    assert metrics["summary"]["coverage_complete"] is False
    assert metrics["summary"]["covered_step_count"] == 1
    assert metrics["summary"]["missing_step_count"] == 4
    assert metrics["summary"]["missing_step_ids"] == FINALIZER_STEPS[1:]
    assert "missing audited not-approved packet coverage" in metrics["summary"]["violations"][0]


def test_coverage_audit_rejects_live_access_authorizing_packet(tmp_path) -> None:
    packet_dirs = {}
    for step_id in FINALIZER_STEPS:
        packet_dir, _audit_dir = create_packet_and_audit(tmp_path, step_id)
        packet_dirs[step_id] = packet_dir
    drifted_packet = packet_dirs[FINALIZER_STEPS[2]]
    metrics = yaml.safe_load((drifted_packet / "metrics.yaml").read_text(encoding="utf-8"))
    metrics["approval_request"]["packet_authorizes_live_access"] = True
    (drifted_packet / "metrics.yaml").write_text(
        yaml.safe_dump(metrics, sort_keys=False),
        encoding="utf-8",
    )
    (drifted_packet / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    completed = run_coverage(tmp_path, check=False)

    assert completed.returncode == 1
    coverage = yaml.safe_load((tmp_path / "coverage" / "metrics.yaml").read_text(encoding="utf-8"))
    assert coverage["summary"]["audit_passed"] is False
    assert coverage["summary"]["covered_step_count"] == 4
    assert coverage["summary"]["missing_step_ids"] == [FINALIZER_STEPS[2]]
    assert coverage["summary"]["live_access_authorizing_packet_count"] == 1
    assert "live-access-authorizing approval packets found: 1" in coverage["summary"]["violations"]
