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

from audit_read_only_calibration_measurement_run import (
    EXPECTED_CSV_HEADERS,
    OPTIONAL_CSV_HEADERS,
)

DEFAULT_REGISTRY = ROOT / "configs" / "read_only_sop_step_registry.yaml"
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


def audit_registry(registry_path: pathlib.Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    violations: list[str] = []
    registry = load_yaml(registry_path)

    if registry.get("source_sop") != "reports/read_only_calibration_measurement_sop.md":
        violations.append("source_sop does not point to the v87 SOP")
    if registry.get("template_source") != "templates/read_only_calibration_measurement":
        violations.append("template_source does not point to the v88/v93 template")
    if registry.get("approval_phrase") != "I approve this read-only measurement step":
        violations.append("approval_phrase does not match the finalizer phrase")

    for key, value in registry.get("claim_boundary", {}).items():
        if value is not False:
            violations.append(f"claim_boundary.{key} is not false")

    expected_worksheets = set(EXPECTED_CSV_HEADERS) | set(OPTIONAL_CSV_HEADERS)
    known_worksheets = set(registry.get("known_worksheets", []))
    if known_worksheets != expected_worksheets:
        violations.append("known_worksheets does not match the read-only audit worksheet set")

    steps = registry.get("steps", [])
    step_ids = [step.get("step_id") for step in steps]
    duplicated_step_ids = sorted({step_id for step_id in step_ids if step_ids.count(step_id) > 1})
    for step_id in duplicated_step_ids:
        violations.append(f"duplicate step_id: {step_id}")

    finalizer_eligible_steps: list[str] = []
    live_hardware_eligible_steps: list[str] = []
    for step in steps:
        step_id = step.get("step_id", "<missing>")
        allowed_worksheets = set(step.get("allowed_worksheets", []))
        forbidden_actions = set(step.get("forbidden_actions", []))
        missing_forbidden_actions = sorted(FORBIDDEN_STEP_ACTIONS - forbidden_actions)
        if missing_forbidden_actions:
            violations.append(
                f"{step_id} does not explicitly forbid: " + ", ".join(missing_forbidden_actions)
            )
        if not allowed_worksheets <= expected_worksheets:
            violations.append(f"{step_id} references unknown worksheets")
        if step.get("finalizer_eligible") is True:
            finalizer_eligible_steps.append(step_id)
            if not allowed_worksheets:
                violations.append(f"{step_id} is finalizer-eligible without allowed worksheets")
            minimum_required_rows = step.get("minimum_required_rows", {})
            for worksheet in allowed_worksheets:
                if int(minimum_required_rows.get(worksheet, 0)) < 1:
                    violations.append(f"{step_id} does not require a row in {worksheet}")
        else:
            if allowed_worksheets:
                violations.append(f"{step_id} is not finalizer-eligible but allows worksheets")
        if step.get("live_hardware_access_allowed_if_user_approved") is True:
            live_hardware_eligible_steps.append(step_id)

    return {
        "run_source": "read-only SOP step registry audit",
        "registry_path": str(registry_path.relative_to(ROOT)),
        "audit_passed": not violations,
        "violations": violations,
        "step_count": len(steps),
        "finalizer_eligible_step_count": len(finalizer_eligible_steps),
        "finalizer_eligible_step_ids": finalizer_eligible_steps,
        "live_hardware_eligible_step_ids": live_hardware_eligible_steps,
        "known_worksheets": sorted(known_worksheets),
        "claim_boundary": registry.get("claim_boundary", {}),
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Read-Only SOP Step Registry Audit",
        "",
        f"Run root: `{out_dir}`",
        f"Registry: `{payload['registry_path']}`",
        "",
        f"- Audit passed: `{payload['audit_passed']}`",
        f"- Step count: `{payload['step_count']}`",
        f"- Finalizer-eligible step count: `{payload['finalizer_eligible_step_count']}`",
        f"- Finalizer-eligible steps: `{payload['finalizer_eligible_step_ids']}`",
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
            "The registry is an approval-scoping artifact only. It does not authorize",
            "live access, robot motion, configuration writes, zeroing, force control,",
            "contact/setup-target acceptance, gate relaxation, or hardware readiness.",
            "",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "read_only_sop_step_registry_audit" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = audit_registry(pathlib.Path(args.registry))
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
