from __future__ import annotations

import json
import shutil
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


def run_preflight(tmp_path, *, check: bool, extra_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "scripts/audit_read_only_step_execution_preflight.py",
            "--output-dir",
            str(tmp_path / "preflight"),
            "--run-id",
            "TEST_PREFLIGHT",
            *(extra_args or []),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


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


def test_execution_preflight_accepts_current_packet_coverage(tmp_path) -> None:
    completed = run_preflight(tmp_path, check=True)

    assert completed.stdout.strip() == str(tmp_path / "preflight")
    metrics = yaml.safe_load((tmp_path / "preflight" / "metrics.yaml").read_text(encoding="utf-8"))
    metrics_json = json.loads((tmp_path / "preflight" / "metrics.json").read_text(encoding="utf-8"))
    assert metrics_json == metrics
    assert metrics["summary"]["audit_passed"] is True
    assert metrics["summary"]["finalizer_eligible_step_count"] == 5
    assert metrics["summary"]["preflight_ready_step_count"] == 5
    assert metrics["summary"]["missing_ready_step_ids"] == []
    assert metrics["summary"]["explicit_user_approval_required"] is True
    assert metrics["summary"]["preflight_authorizes_live_access"] is False
    assert metrics["summary"]["preflight_authorizes_execution"] is False
    assert metrics["summary"]["approved_read_only_evidence_created"] is False
    assert metrics["summary"]["do_not_mark_goal_complete"] is True
    assert metrics["claim_boundary"]["approved_read_only_evidence"] is False
    assert metrics["claim_boundary"]["hardware_readiness"] is False
    assert metrics["claim_boundary"]["do_not_mark_goal_complete"] is True
    assert {row["step_id"] for row in metrics["preflight_rows"]} == set(FINALIZER_STEPS)
    assert all(row["preflight_ready"] is True for row in metrics["preflight_rows"])
    assert all("finalize_read_only_calibration_measurement_evidence.py" in " ".join(row["post_approval_command_plan"]) for row in metrics["preflight_rows"])


def test_execution_preflight_rejects_missing_template_worksheet(tmp_path) -> None:
    template_dir = tmp_path / "template"
    shutil.copytree(f"{ROOT}/templates/read_only_calibration_measurement", template_dir)
    (template_dir / "force_source_comparison.csv").unlink()

    completed = run_preflight(
        tmp_path,
        check=False,
        extra_args=["--template-dir", str(template_dir)],
    )

    assert completed.returncode == 1
    metrics = yaml.safe_load((tmp_path / "preflight" / "metrics.yaml").read_text(encoding="utf-8"))
    assert metrics["summary"]["audit_passed"] is False
    assert "template missing required files: force_source_comparison.csv" in metrics["summary"]["violations"]
    phase4 = [
        row
        for row in metrics["preflight_rows"]
        if row["step_id"] == "phase4_force_source_read_only_comparison"
    ][0]
    assert phase4["preflight_ready"] is False
    assert "missing template worksheet/header: force_source_comparison.csv" in phase4["violations"]


def test_execution_preflight_rejects_live_access_authorizing_packet(tmp_path) -> None:
    packet_dirs = {}
    for step_id in FINALIZER_STEPS:
        packet_dir, _audit_dir = create_packet_and_audit(tmp_path, step_id)
        packet_dirs[step_id] = packet_dir
    drifted_packet = packet_dirs["phase3_plane_normal_external_measurement"]
    metrics = yaml.safe_load((drifted_packet / "metrics.yaml").read_text(encoding="utf-8"))
    metrics["approval_request"]["packet_authorizes_live_access"] = True
    (drifted_packet / "metrics.yaml").write_text(
        yaml.safe_dump(metrics, sort_keys=False),
        encoding="utf-8",
    )
    (drifted_packet / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    completed = run_preflight(
        tmp_path,
        check=False,
        extra_args=[
            "--packet-root",
            str(tmp_path / "packets"),
            "--packet-audit-root",
            str(tmp_path / "audits"),
        ],
    )

    assert completed.returncode == 1
    preflight = yaml.safe_load((tmp_path / "preflight" / "metrics.yaml").read_text(encoding="utf-8"))
    assert preflight["summary"]["audit_passed"] is False
    assert preflight["summary"]["preflight_ready_step_count"] == 4
    assert preflight["summary"]["missing_ready_step_ids"] == [
        "phase3_plane_normal_external_measurement"
    ]
    assert preflight["summary"]["live_access_authorizing_packet_count"] == 1
    assert "live-access-authorizing approval packets found: 1" in preflight["summary"]["violations"]
