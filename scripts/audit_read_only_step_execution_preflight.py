#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from audit_read_only_calibration_measurement_run import (  # noqa: E402
    EXPECTED_CSV_HEADERS,
    OPTIONAL_CSV_HEADERS,
    REQUIRED_FILES,
)
from audit_read_only_step_approval_packet_coverage import (  # noqa: E402
    audit_confirms_not_approved_packet,
    audit_rows_by_packet_path,
    load_yaml,
    packet_passes_not_approved,
    packet_rows_by_step,
    rel,
    scan_metrics,
    write_git_state,
    write_yaml,
)

DEFAULT_REGISTRY = ROOT / "configs" / "read_only_sop_step_registry.yaml"
DEFAULT_PACKET_ROOT = ROOT / "runs" / "read_only_step_approval_packet"
DEFAULT_PACKET_AUDIT_ROOT = ROOT / "runs" / "read_only_step_approval_packet_audit"
DEFAULT_TEMPLATE_DIR = ROOT / "templates" / "read_only_calibration_measurement"
APPROVAL_PHRASE = "I approve this read-only measurement step"
HEAVY_EXTENSIONS = {".npz", ".npy", ".mat", ".tar", ".gz", ".zip"}
REQUIRED_SCRIPT_PATHS = [
    ROOT / "scripts" / "create_read_only_calibration_measurement_run.py",
    ROOT / "scripts" / "finalize_read_only_calibration_measurement_evidence.py",
    ROOT / "scripts" / "audit_read_only_calibration_measurement_run.py",
    ROOT / "scripts" / "audit_read_only_step_approval_packet.py",
    ROOT / "scripts" / "audit_read_only_step_approval_packet_coverage.py",
]
TEMPLATE_REQUIRED_FILES = sorted(REQUIRED_FILES - {"metrics.json", "git_state.md"})


def path_from_row(row: dict[str, Any]) -> pathlib.Path:
    path = pathlib.Path(row["path"])
    if path.is_absolute():
        return path
    return ROOT / path


def artifact_audit(*roots: pathlib.Path) -> dict[str, Any]:
    files: list[pathlib.Path] = []
    for root in roots:
        if root.exists():
            files.extend(path for path in root.rglob("*") if path.is_file())
    return {
        "file_count": len(files),
        "total_bytes": sum(path.stat().st_size for path in files),
        "heavy_payloads": [
            rel(path) for path in files if path.suffix.lower() in HEAVY_EXTENSIONS
        ],
    }


def finalizer_steps(registry: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        step
        for step in registry.get("steps", [])
        if step.get("finalizer_eligible") is True
    ]


def validate_registry(registry: dict[str, Any], violations: list[str]) -> None:
    if registry.get("source_sop") != "reports/read_only_calibration_measurement_sop.md":
        violations.append("registry source_sop does not point to the v87 SOP")
    if registry.get("approval_phrase") != APPROVAL_PHRASE:
        violations.append("registry approval phrase mismatch")
    for key, value in registry.get("claim_boundary", {}).items():
        if value is not False:
            violations.append(f"registry claim_boundary.{key} is not false")


def template_file_status(template_dir: pathlib.Path, worksheet: str) -> dict[str, Any]:
    path = template_dir / worksheet
    expected_header = {**EXPECTED_CSV_HEADERS, **OPTIONAL_CSV_HEADERS}.get(worksheet)
    header = ""
    if path.exists():
        rows = path.read_text(encoding="utf-8").splitlines()
        header = rows[0] if rows else ""
    return {
        "worksheet": worksheet,
        "path": rel(path),
        "exists": path.exists(),
        "header_matches": bool(expected_header) and header == expected_header,
        "expected_header": expected_header,
        "actual_header": header,
    }


def script_statuses() -> list[dict[str, Any]]:
    return [
        {
            "path": rel(path),
            "exists": path.exists(),
            "is_file": path.is_file(),
        }
        for path in REQUIRED_SCRIPT_PATHS
    ]


def valid_packets_for_step(
    *,
    step_id: str,
    packets_by_step: dict[str, list[dict[str, Any]]],
    audits_by_packet: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    valid_packets: list[dict[str, Any]] = []
    for packet in packets_by_step.get(step_id, []):
        packet_metrics_path = path_from_row(packet)
        packet_dir = packet_metrics_path.parent.resolve()
        audits = audits_by_packet.get(str(packet_dir), [])
        valid_audits = [
            audit
            for audit in audits
            if audit_confirms_not_approved_packet(audit, step_id=step_id)
        ]
        if packet_passes_not_approved(packet) and valid_audits:
            valid_packets.append(
                {
                    "packet_metrics": rel(packet_metrics_path),
                    "packet_dir": rel(packet_dir),
                    "audit_metrics": [audit["path"] for audit in valid_audits],
                }
            )
    return valid_packets


def command_plan(step_id: str, allowed_worksheets: list[str]) -> list[str]:
    worksheet_note = ",".join(allowed_worksheets)
    return [
        "python3 scripts/create_read_only_calibration_measurement_run.py "
        "--run-id <fresh_run_id>",
        "Fill only the approved worksheet(s): "
        f"{worksheet_note}; leave all other worksheet CSVs empty.",
        "python3 scripts/finalize_read_only_calibration_measurement_evidence.py "
        "runs/read_only_calibration_measurement/<fresh_run_id> "
        f"--confirmation-phrase '{APPROVAL_PHRASE}' "
        f"--approved-step-id {step_id} "
        "--operator <operator> "
        "--live-hardware-accessed <true|false>",
        "python3 scripts/audit_read_only_calibration_measurement_run.py "
        "runs/read_only_calibration_measurement/<fresh_run_id> "
        "--audit-mode approved-read-only --run-id <fresh_audit_id>",
    ]


def build_payload(
    *,
    registry_path: pathlib.Path,
    packet_root: pathlib.Path,
    packet_audit_root: pathlib.Path,
    template_dir: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    registry = load_yaml(registry_path)
    validate_registry(registry, violations)
    steps = finalizer_steps(registry)
    packets = scan_metrics(packet_root)
    audits = scan_metrics(packet_audit_root)
    packets_by_step = packet_rows_by_step(packets)
    audits_by_packet = audit_rows_by_packet_path(audits)
    template_missing_files = [
        name for name in TEMPLATE_REQUIRED_FILES if not (template_dir / name).is_file()
    ]
    scripts = script_statuses()
    missing_scripts = [row["path"] for row in scripts if not row["exists"] or not row["is_file"]]

    rows: list[dict[str, Any]] = []
    for step in steps:
        step_id = step["step_id"]
        allowed_worksheets = list(step.get("allowed_worksheets", []))
        worksheet_statuses = [
            template_file_status(template_dir, worksheet) for worksheet in allowed_worksheets
        ]
        missing_or_bad_worksheets = [
            row["worksheet"]
            for row in worksheet_statuses
            if not row["exists"] or not row["header_matches"]
        ]
        valid_packets = valid_packets_for_step(
            step_id=step_id,
            packets_by_step=packets_by_step,
            audits_by_packet=audits_by_packet,
        )
        row_violations: list[str] = []
        if not valid_packets:
            row_violations.append("missing audited not-approved packet")
        if missing_or_bad_worksheets:
            row_violations.append(
                "missing template worksheet/header: " + ", ".join(missing_or_bad_worksheets)
            )
        if template_missing_files:
            row_violations.append("template missing required files")
        if missing_scripts:
            row_violations.append("required execution-path scripts missing")
        rows.append(
            {
                "step_id": step_id,
                "title": step["title"],
                "allowed_worksheets": allowed_worksheets,
                "minimum_required_rows": step.get("minimum_required_rows", {}),
                "valid_not_approved_packets": valid_packets,
                "worksheet_statuses": worksheet_statuses,
                "post_approval_command_plan": command_plan(step_id, allowed_worksheets),
                "blocking_conditions": [
                    "requires explicit user approval of this exact registered step",
                    "requires a fresh scaffold run before worksheet entry",
                    "requires approved-read-only finalization and audit before evidence claim",
                ],
                "preflight_ready": not row_violations,
                "violations": row_violations,
            }
        )

    preflight_ready_step_ids = [row["step_id"] for row in rows if row["preflight_ready"]]
    missing_ready_step_ids = [row["step_id"] for row in rows if not row["preflight_ready"]]
    approved_packet_count = sum(
        1
        for packet in packets
        if packet["metrics"].get("approval_request", {}).get("approval_status") == "approved"
    )
    execution_authorizing_packet_count = sum(
        1
        for packet in packets
        if packet["metrics"].get("approval_request", {}).get("packet_authorizes_execution") is True
    )
    live_access_authorizing_packet_count = sum(
        1
        for packet in packets
        if packet["metrics"].get("approval_request", {}).get("packet_authorizes_live_access") is True
    )
    artifacts = artifact_audit(packet_root, packet_audit_root, template_dir)
    if template_missing_files:
        violations.append("template missing required files: " + ", ".join(template_missing_files))
    if missing_scripts:
        violations.append("required scripts missing: " + ", ".join(missing_scripts))
    if missing_ready_step_ids:
        violations.append(
            "execution preflight incomplete for finalizer steps: "
            + ", ".join(missing_ready_step_ids)
        )
    if approved_packet_count:
        violations.append(f"approved approval packets found: {approved_packet_count}")
    if execution_authorizing_packet_count:
        violations.append(
            f"execution-authorizing approval packets found: {execution_authorizing_packet_count}"
        )
    if live_access_authorizing_packet_count:
        violations.append(
            f"live-access-authorizing approval packets found: {live_access_authorizing_packet_count}"
        )
    if artifacts["heavy_payloads"]:
        violations.append("heavy payloads found: " + ", ".join(artifacts["heavy_payloads"]))

    return {
        "run_source": "read-only step execution preflight audit",
        "audit_run_id": run_id,
        "registry_path": rel(registry_path),
        "packet_root": rel(packet_root),
        "packet_audit_root": rel(packet_audit_root),
        "template_dir": rel(template_dir),
        "required_scripts": scripts,
        "template_required_files": TEMPLATE_REQUIRED_FILES,
        "summary": {
            "audit_passed": not violations,
            "violations": violations,
            "finalizer_eligible_step_count": len(steps),
            "preflight_ready_step_count": len(preflight_ready_step_ids),
            "preflight_ready_step_ids": preflight_ready_step_ids,
            "missing_ready_step_ids": missing_ready_step_ids,
            "approved_packet_count": approved_packet_count,
            "execution_authorizing_packet_count": execution_authorizing_packet_count,
            "live_access_authorizing_packet_count": live_access_authorizing_packet_count,
            "explicit_user_approval_required": True,
            "preflight_authorizes_live_access": False,
            "preflight_authorizes_execution": False,
            "approved_read_only_evidence_created": False,
            "do_not_mark_goal_complete": True,
        },
        "preflight_rows": rows,
        "artifact_audit": artifacts,
        "claim_boundary": {
            "preflight_audit_only": True,
            "approval_record_created": False,
            "approved_read_only_evidence": False,
            "live_hardware_access_authorized": False,
            "execution_authorized": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "contact_calibration_claim": False,
            "setup_target_acceptance_claim": False,
            "gate_relaxation_claim": False,
            "hardware_readiness": False,
            "do_not_mark_goal_complete": True,
        },
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Read-Only Step Execution Preflight Audit",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Preflight ready steps: `{summary['preflight_ready_step_count']} / {summary['finalizer_eligible_step_count']}`",
        f"- Missing ready steps: `{summary['missing_ready_step_ids']}`",
        f"- Violations: `{summary['violations']}`",
        f"- Approved packets: `{summary['approved_packet_count']}`",
        f"- Execution-authorizing packets: `{summary['execution_authorizing_packet_count']}`",
        f"- Live-access-authorizing packets: `{summary['live_access_authorizing_packet_count']}`",
        "",
        "## Preflight Rows",
        "",
    ]
    for row in payload["preflight_rows"]:
        lines.append(
            f"- `{row['step_id']}`: ready `{row['preflight_ready']}`, "
            f"worksheets `{row['allowed_worksheets']}`"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This audit checks only offline command-path readiness. It does not",
            "approve any packet, authorize live access, instantiate an approved",
            "run, collect evidence, or support hardware readiness or goal",
            "completion.",
            "",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--packet-root", default=str(DEFAULT_PACKET_ROOT))
    parser.add_argument("--packet-audit-root", default=str(DEFAULT_PACKET_AUDIT_ROOT))
    parser.add_argument("--template-dir", default=str(DEFAULT_TEMPLATE_DIR))
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "read_only_step_execution_preflight" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        registry_path=pathlib.Path(args.registry),
        packet_root=pathlib.Path(args.packet_root),
        packet_audit_root=pathlib.Path(args.packet_audit_root),
        template_dir=pathlib.Path(args.template_dir),
        run_id=run_id,
    )
    payload["audit_root_path"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0 if payload["summary"]["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
