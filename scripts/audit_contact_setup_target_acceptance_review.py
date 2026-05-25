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

REQUIRED_FILES = {
    "README.md",
    "review_plan.md",
    "contact_setup_target_acceptance_review.md",
    "metrics.yaml",
    "metrics.json",
    "summary.md",
    "git_state.md",
}

FALSE_FIELDS = [
    ("source_evidence", "approved_read_only_audit_passed"),
    ("source_evidence", "evidence_reviewed"),
    ("source_evidence", "terminal_optimization_reviewed"),
    ("source_evidence", "contact_geometry_measurement_reviewed"),
    ("source_evidence", "setup_target_definition_reviewed"),
    ("source_evidence", "force_source_reconciliation_reviewed"),
    ("review_execution", "user_approved_contact_setup_target_review"),
    ("review_execution", "live_hardware_accessed"),
    ("review_execution", "robot_motion_commanded"),
    ("review_execution", "configuration_written"),
    ("review_execution", "zeroing_or_biasing_performed"),
    ("review_execution", "force_control_run"),
    ("verdict", "supports_contact_model_update"),
    ("verdict", "supports_setup_target_update"),
    ("verdict", "supports_force_source_update"),
    ("verdict", "supports_gate_relaxation"),
    ("verdict", "supports_hardware_claim"),
    ("claim_boundary", "recovery_claim"),
    ("claim_boundary", "contact_calibration_claim"),
    ("claim_boundary", "setup_target_acceptance_claim"),
    ("claim_boundary", "gate_relaxation_claim"),
    ("claim_boundary", "paper_equivalent_feasibility"),
    ("claim_boundary", "hardware_readiness"),
]

NULL_FIELDS = [
    ("source_evidence", "source_read_only_run"),
    ("source_evidence", "source_run_audit"),
    ("contact_setup_target_acceptance", "accepted_contact_model"),
    ("contact_setup_target_acceptance", "accepted_setup_target_label"),
    ("contact_setup_target_acceptance", "accepted_tcp_contact_datum_source"),
    ("contact_setup_target_acceptance", "accepted_reference_xy_source"),
    ("contact_setup_target_acceptance", "accepted_surface_normal_source"),
    ("contact_setup_target_acceptance", "accepted_force_source"),
    ("contact_setup_target_acceptance", "accepted_uncertainty_budget"),
    ("contact_setup_target_acceptance", "accepted_gate_changes"),
    ("contact_setup_target_acceptance", "reviewer"),
    ("contact_setup_target_acceptance", "accepted_at_utc"),
]

HEAVY_EXTENSIONS = {".npz", ".npy", ".mat", ".tar", ".gz", ".zip"}


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_yaml(path: pathlib.Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)


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


def artifact_audit(review_dir: pathlib.Path) -> dict[str, Any]:
    files = [path for path in review_dir.rglob("*") if path.is_file()]
    heavy_payloads = [
        str(path.relative_to(review_dir)) for path in files if path.suffix.lower() in HEAVY_EXTENSIONS
    ]
    return {
        "file_count": len(files),
        "total_bytes": sum(path.stat().st_size for path in files),
        "heavy_payloads": heavy_payloads,
    }


def audit_review(review_dir: pathlib.Path) -> dict[str, Any]:
    violations: list[str] = []
    present_files = {path.name for path in review_dir.iterdir() if path.is_file()} if review_dir.exists() else set()
    missing_files = sorted(REQUIRED_FILES - present_files)
    if missing_files:
        violations.append(f"missing required files: {', '.join(missing_files)}")

    metrics_yaml_path = review_dir / "metrics.yaml"
    metrics_json_path = review_dir / "metrics.json"
    metrics_yaml: dict[str, Any] = {}
    metrics_json: dict[str, Any] = {}
    if metrics_yaml_path.exists():
        metrics_yaml = load_yaml(metrics_yaml_path)
    if metrics_json_path.exists():
        metrics_json = load_json(metrics_json_path)
    if metrics_yaml and metrics_json and metrics_yaml != metrics_json:
        violations.append("metrics.yaml and metrics.json differ")

    if metrics_yaml.get("status") != "review_scaffold_not_executed":
        violations.append("metrics status is not review_scaffold_not_executed")
    if metrics_yaml.get("template_source") != "templates/contact_setup_target_acceptance_review":
        violations.append("template_source does not point to the contact/setup-target review template")

    for field_path in FALSE_FIELDS:
        if nested_get(metrics_yaml, field_path) is not False:
            violations.append("expected false field is not false: " + ".".join(field_path))
    for field_path in NULL_FIELDS:
        if nested_get(metrics_yaml, field_path) is not None:
            violations.append("expected null field is not null: " + ".".join(field_path))

    acceptance = metrics_yaml.get("contact_setup_target_acceptance", {})
    if acceptance.get("decision") != "not_accepted":
        violations.append("contact_setup_target_acceptance.decision is not not_accepted")
    if acceptance.get("review_only") is not True:
        violations.append("contact_setup_target_acceptance.review_only is not true")

    if nested_get(metrics_yaml, ("claim_boundary", "do_not_mark_goal_complete")) is not True:
        violations.append("claim_boundary.do_not_mark_goal_complete is not true")

    terminal_context = metrics_yaml.get("terminal_compatibility_context", {})
    if terminal_context.get("strict_terminal_pass_count") not in (0, "0"):
        violations.append("terminal_compatibility_context.strict_terminal_pass_count is not zero")

    review_path = review_dir / "contact_setup_target_acceptance_review.md"
    if review_path.exists():
        review_text = review_path.read_text(encoding="utf-8")
        if "Decision status: `not_accepted`" not in review_text:
            violations.append("contact_setup_target_acceptance_review.md does not preserve not_accepted decision status")

    summary_path = review_dir / "summary.md"
    if summary_path.exists():
        summary = summary_path.read_text(encoding="utf-8")
        if "Status: `review_scaffold_not_executed`" not in summary:
            violations.append("summary does not state review_scaffold_not_executed")
        if "hardware-readiness claims remain false" not in summary:
            violations.append("summary does not preserve hardware-readiness claim boundary")

    artifacts = artifact_audit(review_dir)
    if artifacts["heavy_payloads"]:
        violations.append("heavy payloads found: " + ", ".join(artifacts["heavy_payloads"]))

    return {
        "audited_review": str(review_dir),
        "audit_passed": not violations,
        "violations": violations,
        "required_files_present": sorted(REQUIRED_FILES & present_files),
        "missing_files": missing_files,
        "review_status": metrics_yaml.get("status"),
        "review_id": metrics_yaml.get("review_id"),
        "source_evidence": metrics_yaml.get("source_evidence", {}),
        "terminal_compatibility_context": terminal_context,
        "review_execution": metrics_yaml.get("review_execution", {}),
        "contact_setup_target_acceptance": acceptance,
        "verdict": metrics_yaml.get("verdict", {}),
        "claim_boundary": metrics_yaml.get("claim_boundary", {}),
        "artifact_audit": artifacts,
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Contact Setup Target Acceptance Review Audit",
        "",
        f"Run root: `{out_dir}`",
        f"Audited review: `{payload['audited_review']}`",
        "",
        f"- Audit passed: `{payload['audit_passed']}`",
        f"- Review status: `{payload['review_status']}`",
        f"- File count: `{payload['artifact_audit']['file_count']}`",
        f"- Heavy payloads: `{payload['artifact_audit']['heavy_payloads']}`",
        "",
        "## Claim Boundary",
        "",
        f"- Decision: `{payload['contact_setup_target_acceptance'].get('decision')}`",
        f"- Review only: `{payload['contact_setup_target_acceptance'].get('review_only')}`",
        f"- User approved contact/setup-target review: `{payload['review_execution'].get('user_approved_contact_setup_target_review')}`",
        f"- Live hardware accessed: `{payload['review_execution'].get('live_hardware_accessed')}`",
        f"- Robot motion commanded: `{payload['review_execution'].get('robot_motion_commanded')}`",
        f"- Configuration written: `{payload['review_execution'].get('configuration_written')}`",
        f"- Force control run: `{payload['review_execution'].get('force_control_run')}`",
        f"- Supports contact model update: `{payload['verdict'].get('supports_contact_model_update')}`",
        f"- Supports setup target update: `{payload['verdict'].get('supports_setup_target_update')}`",
        f"- Supports hardware claim: `{payload['verdict'].get('supports_hardware_claim')}`",
        f"- Hardware readiness: `{payload['claim_boundary'].get('hardware_readiness')}`",
        f"- Do not mark goal complete: `{payload['claim_boundary'].get('do_not_mark_goal_complete')}`",
        "",
        "## Violations",
        "",
    ]
    if payload["violations"]:
        lines.extend(f"- {violation}" for violation in payload["violations"])
    else:
        lines.append("- none")
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("review_dir")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    review_dir = pathlib.Path(args.review_dir).resolve()
    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "contact_setup_target_acceptance_review_audit" / run_id
    )
    if out_dir.exists():
        raise FileExistsError(out_dir)
    out_dir.mkdir(parents=True)

    payload = audit_review(review_dir)
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
