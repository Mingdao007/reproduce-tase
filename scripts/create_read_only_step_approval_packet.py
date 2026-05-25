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


def registry_step(registry: dict[str, Any], step_id: str) -> dict[str, Any]:
    matches = [step for step in registry.get("steps", []) if step.get("step_id") == step_id]
    if not matches:
        raise ValueError(f"step_id {step_id!r} is not in {DEFAULT_REGISTRY.relative_to(ROOT)}")
    if len(matches) > 1:
        raise ValueError(f"step_id {step_id!r} is duplicated in {DEFAULT_REGISTRY.relative_to(ROOT)}")
    return matches[0]


def validate_registry(registry: dict[str, Any]) -> None:
    if registry.get("source_sop") != "reports/read_only_calibration_measurement_sop.md":
        raise ValueError("registry source_sop does not point to the v87 SOP")
    if registry.get("approval_phrase") != APPROVAL_PHRASE:
        raise ValueError("registry approval phrase mismatch")
    for key, value in registry.get("claim_boundary", {}).items():
        if value is not False:
            raise ValueError(f"registry claim_boundary.{key} is not false")


def build_payload(*, packet_id: str, step: dict[str, Any]) -> dict[str, Any]:
    allowed_worksheets = list(step.get("allowed_worksheets", []))
    minimum_required_rows = dict(step.get("minimum_required_rows", {}))
    forbidden_actions = list(step.get("forbidden_actions", []))
    return {
        "packet_source": "read-only SOP exact-step approval packet",
        "packet_id": packet_id,
        "status": "approval_packet_created_not_approved",
        "registry_path": str(DEFAULT_REGISTRY.relative_to(ROOT)),
        "source_sop": "reports/read_only_calibration_measurement_sop.md",
        "selected_step": {
            "step_id": step["step_id"],
            "title": step["title"],
            "finalizer_eligible": bool(step.get("finalizer_eligible")),
            "allowed_worksheets": allowed_worksheets,
            "minimum_required_rows": minimum_required_rows,
            "live_hardware_access_allowed_if_user_approved": bool(
                step.get("live_hardware_access_allowed_if_user_approved")
            ),
            "forbidden_actions": forbidden_actions,
        },
        "approval_request": {
            "approval_status": "not_approved",
            "required_confirmation_phrase": APPROVAL_PHRASE,
            "required_approved_step_id": step["step_id"],
            "operator": None,
            "approved_at_utc": None,
            "approval_source": None,
            "packet_authorizes_execution": False,
            "packet_authorizes_live_access": False,
        },
        "execution": {
            "live_hardware_accessed": False,
            "robot_motion_commanded": False,
            "configuration_written": False,
            "zeroing_or_biasing_performed": False,
            "force_control_run": False,
        },
        "claim_boundary": {
            "approval_packet_only": True,
            "approved_read_only_evidence": False,
            "contact_calibration_claim": False,
            "setup_target_acceptance_claim": False,
            "gate_relaxation_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "robustness_claim": False,
            "hardware_readiness": False,
            "do_not_mark_goal_complete": True,
        },
    }


def write_packet(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    step = payload["selected_step"]
    request = payload["approval_request"]
    lines = [
        "# Read-Only Step Approval Packet",
        "",
        f"Packet ID: `{payload['packet_id']}`",
        f"Approval status: `{request['approval_status']}`",
        "",
        "## Exact Step",
        "",
        f"- Step ID: `{step['step_id']}`",
        f"- Title: `{step['title']}`",
        f"- Registry: `{payload['registry_path']}`",
        f"- Source SOP: `{payload['source_sop']}`",
        f"- Finalizer eligible: `{step['finalizer_eligible']}`",
        f"- Live hardware access allowed only if separately approved: `{step['live_hardware_access_allowed_if_user_approved']}`",
        "",
        "## Worksheet Scope",
        "",
    ]
    lines.extend(f"- `{worksheet}`" for worksheet in step["allowed_worksheets"])
    lines.extend(
        [
            "",
            "## Forbidden Actions",
            "",
        ]
    )
    lines.extend(f"- `{action}`" for action in step["forbidden_actions"])
    lines.extend(
        [
            "",
            "## Required Confirmation",
            "",
            f"- Confirmation phrase: `{request['required_confirmation_phrase']}`",
            f"- Approved step ID: `{request['required_approved_step_id']}`",
            "- Operator: `TBD`",
            "- Live hardware accessed metadata: `true` or `false`, explicitly selected at finalization time",
            "",
            "This packet is not an approval record. It does not authorize live access,",
            "robot motion, configuration writes, zeroing, force control, contact/setup-target",
            "acceptance, gate relaxation, or hardware readiness.",
            "",
        ]
    )
    (out_dir / "approval_packet.md").write_text("\n".join(lines), encoding="utf-8")


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    step = payload["selected_step"]
    lines = [
        "# Read-Only Step Approval Packet Summary",
        "",
        f"Packet ID: `{payload['packet_id']}`",
        f"Run root: `{out_dir}`",
        "",
        f"Status: `{payload['status']}`",
        f"Step ID: `{step['step_id']}`",
        f"Allowed worksheets: `{step['allowed_worksheets']}`",
        "",
        "No live hardware access, robot motion, configuration write, zeroing, biasing,",
        "or force-control action was performed by creating this packet.",
        "",
        "The packet is a reviewable approval scope only. It is not approved evidence",
        "and does not support calibration, gate relaxation, hardware readiness, or",
        "goal completion.",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def write_metrics(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--step-id", required=True)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--packet-id", default=None)
    parser.add_argument("--allow-nonfinalizer-step", action="store_true")
    args = parser.parse_args()

    packet_id = args.packet_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "read_only_step_approval_packet" / packet_id
    )
    if out_dir.exists():
        raise FileExistsError(out_dir)

    registry = load_yaml(DEFAULT_REGISTRY)
    validate_registry(registry)
    step = registry_step(registry, args.step_id)
    if step.get("finalizer_eligible") is not True and not args.allow_nonfinalizer_step:
        raise ValueError(f"step_id {args.step_id!r} is not finalizer-eligible")

    out_dir.mkdir(parents=True)
    payload = build_payload(packet_id=packet_id, step=step)
    write_metrics(out_dir, payload)
    write_packet(out_dir, payload)
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
