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
APPROVAL_PHRASE = "I approve this read-only measurement step"
REQUIRED_FILES = {"approval_packet.md", "metrics.yaml", "metrics.json", "summary.md", "git_state.md"}
HEAVY_EXTENSIONS = {".npz", ".npy", ".mat", ".tar", ".gz", ".zip"}
FORBIDDEN_STEP_ACTIONS = {
    "robot_motion",
    "force_control",
    "zeroing_or_biasing",
    "tcp_payload_cog_urcap_onrobot_or_rtde_writes",
}


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(payload, f, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True)


def nested_get(payload: dict[str, Any], path: tuple[str, str]) -> Any:
    group, key = path
    return payload.get(group, {}).get(key)


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


def registry_step(registry: dict[str, Any], step_id: str) -> dict[str, Any] | None:
    matches = [step for step in registry.get("steps", []) if step.get("step_id") == step_id]
    if len(matches) != 1:
        return None
    return matches[0]


def artifact_audit(packet_dir: pathlib.Path) -> dict[str, Any]:
    files = [path for path in packet_dir.rglob("*") if path.is_file()]
    heavy_payloads = [
        str(path.relative_to(packet_dir)) for path in files if path.suffix.lower() in HEAVY_EXTENSIONS
    ]
    return {
        "file_count": len(files),
        "total_bytes": sum(path.stat().st_size for path in files),
        "heavy_payloads": heavy_payloads,
    }


def audit_packet(packet_dir: pathlib.Path) -> dict[str, Any]:
    violations: list[str] = []
    present_files = {path.name for path in packet_dir.iterdir() if path.is_file()} if packet_dir.exists() else set()
    missing_files = sorted(REQUIRED_FILES - present_files)
    if missing_files:
        violations.append("missing required files: " + ", ".join(missing_files))

    metrics_yaml: dict[str, Any] = {}
    metrics_json: dict[str, Any] = {}
    if (packet_dir / "metrics.yaml").exists():
        metrics_yaml = load_yaml(packet_dir / "metrics.yaml")
    if (packet_dir / "metrics.json").exists():
        metrics_json = load_json(packet_dir / "metrics.json")
    if metrics_yaml and metrics_json and metrics_yaml != metrics_json:
        violations.append("metrics.yaml and metrics.json differ")

    if metrics_yaml.get("status") != "approval_packet_created_not_approved":
        violations.append("metrics status is not approval_packet_created_not_approved")
    if metrics_yaml.get("registry_path") != "configs/read_only_sop_step_registry.yaml":
        violations.append("registry_path is not configs/read_only_sop_step_registry.yaml")
    if metrics_yaml.get("source_sop") != "reports/read_only_calibration_measurement_sop.md":
        violations.append("source_sop does not point to the v87 SOP")

    registry = load_yaml(DEFAULT_REGISTRY)
    step = metrics_yaml.get("selected_step", {})
    registry_match = registry_step(registry, step.get("step_id"))
    if registry_match is None:
        violations.append("selected_step.step_id is not a unique registry step")
    else:
        if step.get("title") != registry_match.get("title"):
            violations.append("selected_step.title does not match registry")
        if step.get("finalizer_eligible") is not bool(registry_match.get("finalizer_eligible")):
            violations.append("selected_step.finalizer_eligible does not match registry")
        if step.get("allowed_worksheets") != registry_match.get("allowed_worksheets"):
            violations.append("selected_step.allowed_worksheets does not match registry")
        missing_forbidden = sorted(FORBIDDEN_STEP_ACTIONS - set(step.get("forbidden_actions", [])))
        if missing_forbidden:
            violations.append("selected_step missing forbidden actions: " + ", ".join(missing_forbidden))

    request = metrics_yaml.get("approval_request", {})
    if request.get("approval_status") != "not_approved":
        violations.append("approval_request.approval_status is not not_approved")
    if request.get("required_confirmation_phrase") != APPROVAL_PHRASE:
        violations.append("approval_request.required_confirmation_phrase mismatch")
    if request.get("required_approved_step_id") != step.get("step_id"):
        violations.append("approval_request.required_approved_step_id does not match selected step")
    for key in [
        "operator",
        "approved_at_utc",
        "approval_source",
    ]:
        if request.get(key) is not None:
            violations.append(f"approval_request.{key} is not null")
    if request.get("packet_authorizes_execution") is not False:
        violations.append("approval_request.packet_authorizes_execution is not false")
    if request.get("packet_authorizes_live_access") is not False:
        violations.append("approval_request.packet_authorizes_live_access is not false")

    for path in [
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
    ]:
        if nested_get(metrics_yaml, path) is not False:
            violations.append("expected false field is not false: " + ".".join(path))
    if nested_get(metrics_yaml, ("claim_boundary", "do_not_mark_goal_complete")) is not True:
        violations.append("claim_boundary.do_not_mark_goal_complete is not true")

    packet_path = packet_dir / "approval_packet.md"
    if packet_path.exists():
        packet_text = packet_path.read_text(encoding="utf-8")
        if "Approval status: `not_approved`" not in packet_text:
            violations.append("approval_packet.md does not state not_approved status")
        if f"Step ID: `{step.get('step_id')}`" not in packet_text:
            violations.append("approval_packet.md does not state selected step ID")
        if "This packet is not an approval record." not in packet_text:
            violations.append("approval_packet.md does not preserve packet-only boundary")

    artifacts = artifact_audit(packet_dir)
    if artifacts["heavy_payloads"]:
        violations.append("heavy payloads found: " + ", ".join(artifacts["heavy_payloads"]))

    return {
        "audited_packet": str(packet_dir),
        "audit_passed": not violations,
        "violations": violations,
        "required_files_present": sorted(REQUIRED_FILES & present_files),
        "missing_files": missing_files,
        "packet_status": metrics_yaml.get("status"),
        "packet_id": metrics_yaml.get("packet_id"),
        "selected_step": step,
        "approval_request": request,
        "execution": metrics_yaml.get("execution", {}),
        "claim_boundary": metrics_yaml.get("claim_boundary", {}),
        "artifact_audit": artifacts,
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    step = payload.get("selected_step", {})
    lines = [
        "# Read-Only Step Approval Packet Audit",
        "",
        f"Run root: `{out_dir}`",
        f"Audited packet: `{payload['audited_packet']}`",
        "",
        f"- Audit passed: `{payload['audit_passed']}`",
        f"- Packet status: `{payload['packet_status']}`",
        f"- Step ID: `{step.get('step_id')}`",
        f"- File count: `{payload['artifact_audit']['file_count']}`",
        f"- Heavy payloads: `{payload['artifact_audit']['heavy_payloads']}`",
        "",
        "## Violations",
        "",
    ]
    if payload["violations"]:
        lines.extend(f"- {violation}" for violation in payload["violations"])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "The packet is not an approval record and does not authorize live access,",
            "robot motion, configuration writes, zeroing, force control, acceptance,",
            "hardware readiness, or goal completion.",
            "",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet_dir")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    packet_dir = pathlib.Path(args.packet_dir).resolve()
    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "read_only_step_approval_packet_audit" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = audit_packet(packet_dir)
    payload["audit_run_id"] = run_id
    payload["audit_root"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0 if payload["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
