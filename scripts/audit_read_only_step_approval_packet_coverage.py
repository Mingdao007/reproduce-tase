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
DEFAULT_REGISTRY = ROOT / "configs" / "read_only_sop_step_registry.yaml"
DEFAULT_PACKET_ROOT = ROOT / "runs" / "read_only_step_approval_packet"
DEFAULT_AUDIT_ROOT = ROOT / "runs" / "read_only_step_approval_packet_audit"
HEAVY_EXTENSIONS = {".npz", ".npy", ".mat", ".tar", ".gz", ".zip"}


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(payload, f, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True)


def rel(path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def git_value(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def write_git_state(out_dir: pathlib.Path, *, command: list[str]) -> None:
    branch = git_value(["branch", "--show-current"])
    commit = git_value(["rev-parse", "HEAD"])
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
    lines = [
        "# Git State",
        "",
        f"- Branch: `{branch}`",
        f"- Commit: `{commit}`",
        f"- Dirty tree: `{bool(status)}`",
        "- Status:",
        "",
        "```text",
        status,
        "```",
        "",
        "- Command:",
        "",
        "```bash",
        " ".join(command),
        "```",
        "",
    ]
    (out_dir / "git_state.md").write_text("\n".join(lines), encoding="utf-8")


def scan_metrics(root: pathlib.Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for metrics_path in sorted(root.glob("*/metrics.yaml")):
        metrics = load_yaml(metrics_path)
        rows.append(
            {
                "run_id": metrics_path.parent.name,
                "path": rel(metrics_path),
                "metrics": metrics,
            }
        )
    return rows


def artifact_audit(*roots: pathlib.Path) -> dict[str, Any]:
    files: list[pathlib.Path] = []
    for root in roots:
        if root.exists():
            files.extend(path for path in root.rglob("*") if path.is_file())
    heavy_payloads = [rel(path) for path in files if path.suffix.lower() in HEAVY_EXTENSIONS]
    return {
        "file_count": len(files),
        "total_bytes": sum(path.stat().st_size for path in files),
        "heavy_payloads": heavy_payloads,
    }


def finalizer_step_ids(registry: dict[str, Any]) -> list[str]:
    return [
        step["step_id"]
        for step in registry.get("steps", [])
        if step.get("finalizer_eligible") is True
    ]


def packet_rows_by_step(packets: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_step: dict[str, list[dict[str, Any]]] = {}
    for packet in packets:
        step_id = packet["metrics"].get("selected_step", {}).get("step_id")
        if step_id:
            by_step.setdefault(step_id, []).append(packet)
    return by_step


def audit_rows_by_packet_path(audits: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_packet: dict[str, list[dict[str, Any]]] = {}
    for audit in audits:
        packet_path = audit["metrics"].get("audited_packet")
        if packet_path:
            by_packet.setdefault(str(pathlib.Path(packet_path).resolve()), []).append(audit)
    return by_packet


EXPECTED_FALSE_FIELDS = [
    ("approval_request", "packet_authorizes_execution"),
    ("approval_request", "packet_authorizes_live_access"),
    ("execution", "live_hardware_accessed"),
    ("execution", "robot_motion_commanded"),
    ("execution", "configuration_written"),
    ("execution", "zeroing_or_biasing_performed"),
    ("execution", "force_control_run"),
    ("claim_boundary", "approved_read_only_evidence"),
    ("claim_boundary", "contact_calibration_claim"),
    ("claim_boundary", "setup_target_acceptance_claim"),
    ("claim_boundary", "gate_relaxation_claim"),
    ("claim_boundary", "strict_paper_equivalent_feasibility"),
    ("claim_boundary", "robustness_claim"),
    ("claim_boundary", "hardware_readiness"),
]


def nested_get(metrics: dict[str, Any], group: str, key: str) -> Any:
    return metrics.get(group, {}).get(key)


def packet_passes_not_approved(packet: dict[str, Any]) -> bool:
    metrics = packet["metrics"]
    return (
        metrics.get("status") == "approval_packet_created_not_approved"
        and metrics.get("approval_request", {}).get("approval_status") == "not_approved"
        and metrics.get("claim_boundary", {}).get("approval_packet_only") is True
        and all(nested_get(metrics, group, key) is False for group, key in EXPECTED_FALSE_FIELDS)
        and metrics.get("claim_boundary", {}).get("do_not_mark_goal_complete") is True
    )


def audit_confirms_not_approved_packet(audit: dict[str, Any], *, step_id: str) -> bool:
    metrics = audit["metrics"]
    return (
        metrics.get("audit_passed") is True
        and metrics.get("packet_status") == "approval_packet_created_not_approved"
        and metrics.get("selected_step", {}).get("step_id") == step_id
        and metrics.get("approval_request", {}).get("approval_status") == "not_approved"
        and all(nested_get(metrics, group, key) is False for group, key in EXPECTED_FALSE_FIELDS)
        and metrics.get("claim_boundary", {}).get("do_not_mark_goal_complete") is True
    )


def count_packets_with(packets: list[dict[str, Any]], group: str, key: str, value: Any) -> int:
    return sum(1 for packet in packets if nested_get(packet["metrics"], group, key) is value)


def build_payload(
    *,
    registry_path: pathlib.Path,
    packet_root: pathlib.Path,
    audit_root: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    registry = load_yaml(registry_path)
    required_step_ids = finalizer_step_ids(registry)
    packets = scan_metrics(packet_root)
    audits = scan_metrics(audit_root)
    packets_by_step = packet_rows_by_step(packets)
    audits_by_packet = audit_rows_by_packet_path(audits)

    rows: list[dict[str, Any]] = []
    for step_id in required_step_ids:
        step_packets = packets_by_step.get(step_id, [])
        valid_packets: list[dict[str, Any]] = []
        for packet in step_packets:
            packet_dir = (ROOT / packet["path"]).parent.resolve()
            packet_audits = audits_by_packet.get(str(packet_dir), [])
            valid_audits = [
                audit
                for audit in packet_audits
                if audit_confirms_not_approved_packet(audit, step_id=step_id)
            ]
            valid = packet_passes_not_approved(packet) and bool(valid_audits)
            if valid:
                valid_packets.append(
                    {
                        "packet_path": packet["path"],
                        "audit_paths": [audit["path"] for audit in valid_audits],
                    }
                )
        rows.append(
            {
                "step_id": step_id,
                "packet_count": len(step_packets),
                "valid_not_approved_packet_count": len(valid_packets),
                "valid_packets": valid_packets,
                "coverage_passed": bool(valid_packets),
            }
        )

    missing_step_ids = [row["step_id"] for row in rows if not row["coverage_passed"]]
    artifacts = artifact_audit(packet_root, audit_root)
    approved_packet_count = sum(
        1 for packet in packets if packet["metrics"].get("approval_request", {}).get("approval_status") == "approved"
    )
    execution_authorizing_packet_count = count_packets_with(
        packets, "approval_request", "packet_authorizes_execution", True
    )
    live_access_authorizing_packet_count = count_packets_with(
        packets, "approval_request", "packet_authorizes_live_access", True
    )
    violations: list[str] = []
    if missing_step_ids:
        violations.append(
            "missing audited not-approved packet coverage for finalizer steps: "
            + ", ".join(missing_step_ids)
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

    summary = {
        "required_finalizer_step_count": len(required_step_ids),
        "covered_step_count": len(required_step_ids) - len(missing_step_ids),
        "missing_step_count": len(missing_step_ids),
        "missing_step_ids": missing_step_ids,
        "coverage_complete": not missing_step_ids,
        "audit_passed": not violations,
        "violations": violations,
        "approval_packet_count": len(packets),
        "approval_packet_audit_count": len(audits),
        "approved_packet_count": approved_packet_count,
        "execution_authorizing_packet_count": execution_authorizing_packet_count,
        "live_access_authorizing_packet_count": live_access_authorizing_packet_count,
        "do_not_mark_goal_complete": True,
    }
    return {
        "run_source": "read-only step approval packet coverage audit",
        "audit_run_id": run_id,
        "registry_path": rel(registry_path),
        "packet_root": rel(packet_root),
        "audit_root": rel(audit_root),
        "summary": summary,
        "coverage_rows": rows,
        "artifact_audit": artifacts,
        "claim_boundary": {
            "coverage_audit_only": True,
            "approved_read_only_evidence": False,
            "packet_approves_live_access": False,
            "packet_authorizes_execution": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "contact_calibration_claim": False,
            "gate_relaxation_claim": False,
            "hardware_readiness": False,
            "do_not_mark_goal_complete": True,
        },
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Read-Only Step Approval Packet Coverage Audit",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Coverage complete: `{summary['coverage_complete']}`",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Covered steps: `{summary['covered_step_count']} / {summary['required_finalizer_step_count']}`",
        f"- Missing steps: `{summary['missing_step_ids']}`",
        f"- Violations: `{summary['violations']}`",
        f"- Approved packets: `{summary['approved_packet_count']}`",
        f"- Execution-authorizing packets: `{summary['execution_authorizing_packet_count']}`",
        f"- Live-access-authorizing packets: `{summary['live_access_authorizing_packet_count']}`",
        "",
        "## Coverage Rows",
        "",
    ]
    for row in payload["coverage_rows"]:
        lines.append(
            f"- `{row['step_id']}`: coverage `{row['coverage_passed']}`, "
            f"valid packets `{row['valid_not_approved_packet_count']}`"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This audit only checks not-approved packet coverage. It does not approve",
            "any packet, authorize live access, collect evidence, or support hardware",
            "readiness or goal completion.",
            "",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--packet-root", default=str(DEFAULT_PACKET_ROOT))
    parser.add_argument("--audit-root", default=str(DEFAULT_AUDIT_ROOT))
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "read_only_step_approval_packet_coverage" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        registry_path=pathlib.Path(args.registry),
        packet_root=pathlib.Path(args.packet_root),
        audit_root=pathlib.Path(args.audit_root),
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
