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
DEFAULT_STEP_REGISTRY = ROOT / "configs" / "read_only_sop_step_registry.yaml"

REQUIRED_FILES = {
    "README.md",
    "measurement_plan.md",
    "operator_checklist.md",
    "tcp_contact_measurements.csv",
    "plane_normal_measurements.csv",
    "force_source_comparison.csv",
    "orientation_gate_decision.md",
    "photos_manifest.md",
    "metrics.yaml",
    "metrics.json",
    "summary.md",
    "git_state.md",
}

EXPECTED_CSV_HEADERS = {
    "tcp_contact_measurements.csv": "sample_id,datum,tool_axis_sign,distance_mm,instrument,resolution_mm,operator,notes",
    "plane_normal_measurements.csv": "sample_id,method,normal_x,normal_y,normal_z,angle_uncertainty_deg,notes",
    "force_source_comparison.csv": "timestamp_s,source,Fx_N,Fy_N,Fz_N,Tx_Nm,Ty_Nm,Tz_Nm,zero_state,frame,notes",
}

OPTIONAL_CSV_HEADERS = {
    "ksm_contact_patch_convention.csv": "sample_id,datum,contact_patch_description,seating_observation,instrument,operator,notes",
    "orientation_gate_semantics.csv": "sample_id,gate_type,gate_value_rad,normal_source,contact_datum_source,uncertainty_deg,geometry_uncertainty_um,decision,operator,notes",
}

SCAFFOLD_FALSE_FIELDS = [
    ("execution", "user_confirmed_read_only_step"),
    ("execution", "live_hardware_accessed"),
]

HARD_FALSE_FIELDS = [
    ("execution", "robot_motion_commanded"),
    ("execution", "configuration_written"),
    ("execution", "zeroing_or_biasing_performed"),
    ("execution", "force_control_run"),
    ("verdict", "supports_contact_model_update"),
    ("verdict", "supports_accepting_v85_margin"),
    ("verdict", "supports_gate_relaxation"),
    ("verdict", "supports_hardware_claim"),
    ("verdict", "supports_more_stage_b_qdot_tuning"),
    ("claim_boundary", "recovery_claim"),
    ("claim_boundary", "contact_calibration_claim"),
    ("claim_boundary", "gate_relaxation_claim"),
    ("claim_boundary", "paper_equivalent_feasibility"),
    ("claim_boundary", "hardware_readiness"),
]

EXPECTED_EVIDENCE_STATUS = {
    "mounted_stack_tcp_contact_point": "not_collected",
    "ksm_contact_patch_convention": "not_collected",
    "plane_normal_robot_base_frame": "not_collected",
    "force_source_frame_reconciliation": "not_collected",
    "orientation_gate_semantics": "not_accepted",
}

APPROVED_READ_ONLY_EVIDENCE_STATUSES = {
    "not_collected",
    "collected_read_only",
    "not_executable",
    "unresolved",
    "not_accepted",
}

HEAVY_EXTENSIONS = {".npz", ".npy", ".mat", ".tar", ".gz", ".zip"}

ORIENTATION_ACCEPTANCE_NULL_FIELDS = [
    "accepted_gate_type",
    "accepted_gate_value_rad",
    "accepted_normal_source",
    "accepted_contact_datum_source",
    "accepted_uncertainty_budget",
]

FORBIDDEN_STEP_ACTIONS = {
    "robot_motion",
    "force_control",
    "zeroing_or_biasing",
    "tcp_payload_cog_urcap_onrobot_or_rtde_writes",
}


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


def artifact_audit(run_dir: pathlib.Path) -> dict[str, Any]:
    files = [path for path in run_dir.rglob("*") if path.is_file()]
    heavy_payloads = [
        str(path.relative_to(run_dir)) for path in files if path.suffix.lower() in HEAVY_EXTENSIONS
    ]
    return {
        "file_count": len(files),
        "total_bytes": sum(path.stat().st_size for path in files),
        "heavy_payloads": heavy_payloads,
    }


def audit_orientation_gate_acceptance(
    metrics_yaml: dict[str, Any],
    evidence_status: dict[str, Any],
    violations: list[str],
) -> dict[str, Any]:
    orientation_gate_acceptance = metrics_yaml.get("orientation_gate_acceptance")
    orientation_evidence_changed = (
        evidence_status.get("orientation_gate_semantics")
        != EXPECTED_EVIDENCE_STATUS["orientation_gate_semantics"]
    )
    if orientation_gate_acceptance is None and orientation_evidence_changed:
        violations.append(
            "orientation_gate_acceptance is required when orientation_gate_semantics evidence changes"
        )
        return {}
    if orientation_gate_acceptance is None:
        return {}
    if not isinstance(orientation_gate_acceptance, dict):
        violations.append("orientation_gate_acceptance is not a mapping")
        return {}
    if orientation_gate_acceptance.get("decision") != "not_accepted":
        violations.append("orientation_gate_acceptance.decision is not not_accepted")
    if orientation_gate_acceptance.get("evidence_only") is not True:
        violations.append("orientation_gate_acceptance.evidence_only is not true")
    if orientation_gate_acceptance.get("requires_separate_gate_audit") is not True:
        violations.append("orientation_gate_acceptance.requires_separate_gate_audit is not true")
    for field in ORIENTATION_ACCEPTANCE_NULL_FIELDS:
        if orientation_gate_acceptance.get(field) is not None:
            violations.append(f"orientation_gate_acceptance.{field} is not null")
    row_count = orientation_gate_acceptance.get("orientation_semantics_rows")
    if row_count is not None and not isinstance(row_count, int):
        violations.append("orientation_gate_acceptance.orientation_semantics_rows is not integer")
    return orientation_gate_acceptance


def read_csv_row_counts(run_dir: pathlib.Path) -> dict[str, int]:
    row_counts: dict[str, int] = {}
    csv_headers = {**EXPECTED_CSV_HEADERS, **OPTIONAL_CSV_HEADERS}
    for csv_name, expected_header in csv_headers.items():
        csv_path = run_dir / csv_name
        if not csv_path.exists():
            row_counts[csv_name] = 0
            continue
        rows = csv_path.read_text(encoding="utf-8").splitlines()
        row_counts[csv_name] = max(0, len([row for row in rows[1:] if row.strip()]))
        if rows and rows[0] != expected_header:
            row_counts[csv_name] = 0
    return row_counts


def audit_approved_step_registry(
    metrics_yaml: dict[str, Any],
    row_counts: dict[str, int],
    violations: list[str],
) -> dict[str, Any]:
    finalization = metrics_yaml.get("read_only_evidence_finalization")
    if not isinstance(finalization, dict):
        violations.append("read_only_evidence_finalization is required in approved-read-only mode")
        return {}
    approved_step_id = finalization.get("approved_step_id")
    if not approved_step_id:
        violations.append("read_only_evidence_finalization.approved_step_id is missing")
        return finalization

    try:
        registry = load_yaml(DEFAULT_STEP_REGISTRY)
    except FileNotFoundError:
        violations.append(f"approved-step registry missing: {DEFAULT_STEP_REGISTRY.relative_to(ROOT)}")
        return finalization
    if registry.get("source_sop") != "reports/read_only_calibration_measurement_sop.md":
        violations.append("approved-step registry does not point to the v87 SOP")
    if registry.get("approval_phrase") != "I approve this read-only measurement step":
        violations.append("approved-step registry approval phrase mismatch")
    for key, value in registry.get("claim_boundary", {}).items():
        if value is not False:
            violations.append(f"approved-step registry claim_boundary.{key} is not false")

    steps = [step for step in registry.get("steps", []) if step.get("step_id") == approved_step_id]
    if not steps:
        violations.append(f"approved_step_id {approved_step_id!r} is not in approved-step registry")
        return finalization
    if len(steps) > 1:
        violations.append(f"approved_step_id {approved_step_id!r} is duplicated in approved-step registry")
        return finalization

    step = steps[0]
    if step.get("finalizer_eligible") is not True:
        violations.append(f"approved_step_id {approved_step_id!r} is not eligible for evidence finalization")
    forbidden_actions = set(step.get("forbidden_actions", []))
    for missing_action in sorted(FORBIDDEN_STEP_ACTIONS - forbidden_actions):
        violations.append(f"approved_step_id {approved_step_id!r} does not forbid {missing_action}")

    allowed_worksheets = set(step.get("allowed_worksheets", []))
    populated_disallowed = sorted(
        csv_name for csv_name, count in row_counts.items() if count > 0 and csv_name not in allowed_worksheets
    )
    if populated_disallowed:
        violations.append(
            f"approved_step_id {approved_step_id!r} does not allow rows in: "
            + ", ".join(populated_disallowed)
        )
    for csv_name, min_rows in step.get("minimum_required_rows", {}).items():
        if row_counts.get(csv_name, 0) < int(min_rows):
            violations.append(
                f"approved_step_id {approved_step_id!r} requires at least {min_rows} row(s) in {csv_name}"
            )
    recorded_allowed = sorted(finalization.get("allowed_worksheets", []))
    if recorded_allowed and recorded_allowed != sorted(allowed_worksheets):
        violations.append("read_only_evidence_finalization.allowed_worksheets does not match registry")
    return finalization


def audit_run(run_dir: pathlib.Path, *, audit_mode: str) -> dict[str, Any]:
    violations: list[str] = []
    present_files = {path.name for path in run_dir.iterdir() if path.is_file()} if run_dir.exists() else set()
    missing_files = sorted(REQUIRED_FILES - present_files)
    if missing_files:
        violations.append(f"missing required files: {', '.join(missing_files)}")

    metrics_yaml_path = run_dir / "metrics.yaml"
    metrics_json_path = run_dir / "metrics.json"
    metrics_yaml: dict[str, Any] = {}
    metrics_json: dict[str, Any] = {}
    if metrics_yaml_path.exists():
        metrics_yaml = load_yaml(metrics_yaml_path)
    if metrics_json_path.exists():
        metrics_json = load_json(metrics_json_path)
    if metrics_yaml and metrics_json and metrics_yaml != metrics_json:
        violations.append("metrics.yaml and metrics.json differ")

    expected_status = {
        "scaffold": "scaffold_created_not_executed",
        "approved-read-only": "approved_read_only_evidence",
    }[audit_mode]
    if metrics_yaml.get("status") != expected_status:
        violations.append(f"metrics status is not {expected_status}")
    if metrics_yaml.get("source_sop") != "reports/read_only_calibration_measurement_sop.md":
        violations.append("source_sop does not point to the v87 SOP")
    if metrics_yaml.get("template_source") != "templates/read_only_calibration_measurement":
        violations.append("template_source does not point to the v88 template")

    false_fields = list(HARD_FALSE_FIELDS)
    if audit_mode == "scaffold":
        false_fields.extend(SCAFFOLD_FALSE_FIELDS)
    for field_path in false_fields:
        if nested_get(metrics_yaml, field_path) is not False:
            violations.append("expected false field is not false: " + ".".join(field_path))

    if audit_mode == "approved-read-only":
        if nested_get(metrics_yaml, ("execution", "user_confirmed_read_only_step")) is not True:
            violations.append("approved read-only mode requires execution.user_confirmed_read_only_step true")
        live_read = nested_get(metrics_yaml, ("execution", "live_hardware_accessed"))
        if not isinstance(live_read, bool):
            violations.append("execution.live_hardware_accessed must be boolean")

    evidence_status = metrics_yaml.get("evidence_status", {})
    if audit_mode == "scaffold":
        for key, expected in EXPECTED_EVIDENCE_STATUS.items():
            if evidence_status.get(key) != expected:
                violations.append(f"evidence_status.{key} is not {expected}")
    else:
        changed_evidence_fields = []
        for key, scaffold_value in EXPECTED_EVIDENCE_STATUS.items():
            actual = evidence_status.get(key)
            if actual not in APPROVED_READ_ONLY_EVIDENCE_STATUSES:
                violations.append(f"evidence_status.{key} has unsupported status {actual!r}")
            if actual != scaffold_value:
                changed_evidence_fields.append(key)
        if not changed_evidence_fields:
            violations.append("approved read-only mode requires at least one evidence_status field to change")

    orientation_gate_acceptance = audit_orientation_gate_acceptance(
        metrics_yaml, evidence_status, violations
    )

    csv_headers = {**EXPECTED_CSV_HEADERS, **OPTIONAL_CSV_HEADERS}
    for csv_name, expected_header in csv_headers.items():
        csv_path = run_dir / csv_name
        if csv_path.exists():
            rows = csv_path.read_text(encoding="utf-8").splitlines()
            actual_header = rows[0] if rows else ""
            if actual_header != expected_header:
                violations.append(f"{csv_name} header changed")
            if audit_mode == "scaffold" and len(rows) > 1:
                violations.append(f"{csv_name} contains rows in scaffold mode")

    row_counts = read_csv_row_counts(run_dir)
    finalization = {}
    if audit_mode == "approved-read-only":
        finalization = audit_approved_step_registry(metrics_yaml, row_counts, violations)

    orientation_decision_path = run_dir / "orientation_gate_decision.md"
    if orientation_decision_path.exists():
        orientation_decision = orientation_decision_path.read_text(encoding="utf-8")
        if "Decision status: `not_accepted`" not in orientation_decision:
            violations.append("orientation_gate_decision.md does not preserve not_accepted decision status")

    summary_path = run_dir / "summary.md"
    if summary_path.exists():
        summary = summary_path.read_text(encoding="utf-8")
        if audit_mode == "scaffold" and "Status: `scaffold_created_not_executed`" not in summary:
            violations.append("summary does not state scaffold_created_not_executed")
        if "hardware-readiness claims remain false" not in summary:
            violations.append("summary does not preserve hardware-readiness claim boundary")

    artifacts = artifact_audit(run_dir)
    if artifacts["heavy_payloads"]:
        violations.append("heavy payloads found: " + ", ".join(artifacts["heavy_payloads"]))

    return {
        "audited_run": str(run_dir),
        "audit_mode": audit_mode,
        "audit_passed": not violations,
        "violations": violations,
        "required_files_present": sorted(REQUIRED_FILES & present_files),
        "missing_files": missing_files,
        "run_status": metrics_yaml.get("status"),
        "run_id": metrics_yaml.get("run_id"),
        "execution": metrics_yaml.get("execution", {}),
        "evidence_status": evidence_status,
        "orientation_gate_acceptance": orientation_gate_acceptance,
        "read_only_evidence_finalization": finalization,
        "worksheet_row_counts": row_counts,
        "verdict": metrics_yaml.get("verdict", {}),
        "claim_boundary": metrics_yaml.get("claim_boundary", {}),
        "artifact_audit": artifacts,
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Read-Only Calibration Measurement Run Audit",
        "",
        f"Run root: `{out_dir}`",
        f"Audited run: `{payload['audited_run']}`",
        "",
        f"- Audit mode: `{payload['audit_mode']}`",
        f"- Audit passed: `{payload['audit_passed']}`",
        f"- Run status: `{payload['run_status']}`",
        f"- File count: `{payload['artifact_audit']['file_count']}`",
        f"- Heavy payloads: `{payload['artifact_audit']['heavy_payloads']}`",
        "",
        "## Claim Boundary",
        "",
        f"- Live hardware accessed: `{payload['execution'].get('live_hardware_accessed')}`",
        f"- User confirmed read-only step: `{payload['execution'].get('user_confirmed_read_only_step')}`",
        f"- Robot motion commanded: `{payload['execution'].get('robot_motion_commanded')}`",
        f"- Configuration written: `{payload['execution'].get('configuration_written')}`",
        f"- Force control run: `{payload['execution'].get('force_control_run')}`",
        f"- Supports gate relaxation: `{payload['verdict'].get('supports_gate_relaxation')}`",
        f"- Orientation gate decision: `{payload['orientation_gate_acceptance'].get('decision')}`",
        f"- Orientation evidence only: `{payload['orientation_gate_acceptance'].get('evidence_only')}`",
        f"- Supports hardware claim: `{payload['verdict'].get('supports_hardware_claim')}`",
        f"- Hardware readiness: `{payload['claim_boundary'].get('hardware_readiness')}`",
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
    parser.add_argument("run_dir")
    parser.add_argument(
        "--audit-mode",
        choices=("scaffold", "approved-read-only"),
        default="scaffold",
        help="Use scaffold for untouched templates; use approved-read-only for explicitly approved worksheet runs.",
    )
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_dir = pathlib.Path(args.run_dir).resolve()
    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        pathlib.Path(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "read_only_calibration_measurement_run_audit" / run_id
    )
    if out_dir.exists():
        raise FileExistsError(out_dir)
    out_dir.mkdir(parents=True)

    payload = audit_run(run_dir, audit_mode=args.audit_mode)
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
