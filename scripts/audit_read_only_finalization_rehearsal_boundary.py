#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import pathlib
import subprocess
import sys
import tempfile
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from audit_read_only_calibration_measurement_run import (  # noqa: E402
    EXPECTED_CSV_HEADERS,
    OPTIONAL_CSV_HEADERS,
)

APPROVAL_PHRASE = "I approve this read-only measurement step"
DEFAULT_REGISTRY = ROOT / "configs" / "read_only_sop_step_registry.yaml"
DEFAULT_DOWNSTREAM_GUARD = (
    ROOT / "runs" / "downstream_row_quality_guard" / "20260525T121000" / "metrics.yaml"
)
DEFAULT_READ_ONLY_RUN_ROOT = ROOT / "runs" / "read_only_calibration_measurement"
DEFAULT_READ_ONLY_AUDIT_ROOT = ROOT / "runs" / "read_only_calibration_measurement_run_audit"

REHEARSAL_ROWS = {
    "phase1_mounted_stack_tcp_contact_measurement": {
        "worksheet": "tcp_contact_measurements.csv",
        "row": [
            "sample_001",
            "mounted_stack_contact_tip",
            "+z",
            "85.0",
            "digital_caliper",
            "0.01",
            "finalization_rehearsal",
            "synthetic offline finalization rehearsal only",
        ],
        "evidence_key": "mounted_stack_tcp_contact_point",
    },
    "phase2_ksm_contact_patch_convention": {
        "worksheet": "ksm_contact_patch_convention.csv",
        "row": [
            "sample_001",
            "ksm_fixture_face",
            "flat leading face contact patch",
            "fully seated against fixture witness marks",
            "visual_inspection",
            "finalization_rehearsal",
            "synthetic offline finalization rehearsal only",
        ],
        "evidence_key": "ksm_contact_patch_convention",
    },
    "phase3_plane_normal_external_measurement": {
        "worksheet": "plane_normal_measurements.csv",
        "row": [
            "sample_001",
            "external_metrology_fixture",
            "0.0",
            "0.0",
            "1.0",
            "0.03",
            "synthetic offline finalization rehearsal only",
        ],
        "evidence_key": "plane_normal_robot_base_frame",
    },
    "phase4_force_source_read_only_comparison": {
        "worksheet": "force_source_comparison.csv",
        "row": [
            "0.0",
            "ur_rtde",
            "0.0",
            "0.0",
            "32.0",
            "0.0",
            "0.0",
            "0.0",
            "bias_unchanged",
            "base",
            "synthetic offline finalization rehearsal only",
        ],
        "evidence_key": "force_source_frame_reconciliation",
    },
    "phase5_orientation_gate_semantics_evidence": {
        "worksheet": "orientation_gate_semantics.csv",
        "row": [
            "sample_001",
            "normal_alignment",
            "0.119",
            "plane_normal_fixture",
            "contact_fixture",
            "0.03",
            "14.0",
            "unresolved",
            "finalization_rehearsal",
            "synthetic offline finalization rehearsal only",
        ],
        "evidence_key": "orientation_gate_semantics",
    },
}

FORBIDDEN_STEP_ACTIONS = {
    "robot_motion",
    "force_control",
    "zeroing_or_biasing",
    "tcp_payload_cog_urcap_onrobot_or_rtde_writes",
}


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


def resolve(path: str | pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(path)
    if path.is_absolute():
        return path
    return ROOT / path


def rel(path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


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


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def scan_metrics(root: pathlib.Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for metrics_path in sorted(root.glob("*/metrics.yaml")):
        rows.append(
            {
                "run_id": metrics_path.parent.name,
                "path": rel(metrics_path),
                "metrics": load_yaml(metrics_path),
            }
        )
    return rows


def nested_get(payload: dict[str, Any], path: list[str], default: Any = None) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def read_only_repository_state(
    *, run_root: pathlib.Path, audit_root: pathlib.Path
) -> dict[str, Any]:
    runs = scan_metrics(run_root)
    audits = scan_metrics(audit_root)
    approved_runs = [
        row
        for row in runs
        if row["metrics"].get("status") == "approved_read_only_evidence"
        and nested_get(row["metrics"], ["execution", "user_confirmed_read_only_step"]) is True
    ]
    finalization_records = [
        row for row in runs if isinstance(row["metrics"].get("read_only_evidence_finalization"), dict)
    ]
    approved_audits = [
        row
        for row in audits
        if row["metrics"].get("audit_mode") == "approved-read-only"
        and row["metrics"].get("audit_passed") is True
    ]
    return {
        "run_root": rel(run_root),
        "audit_root": rel(audit_root),
        "read_only_run_count": len(runs),
        "read_only_audit_count": len(audits),
        "approved_read_only_run_count": len(approved_runs),
        "read_only_evidence_finalization_present_count": len(finalization_records),
        "approved_read_only_audit_passed_count": len(approved_audits),
        "approved_run_paths": [row["path"] for row in approved_runs],
        "finalization_record_paths": [row["path"] for row in finalization_records],
        "approved_audit_paths": [row["path"] for row in approved_audits],
    }


def append_row(run_dir: pathlib.Path, worksheet: str, row: list[str]) -> None:
    with (run_dir / worksheet).open("a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(row)


def create_temp_scaffold(temp_root: pathlib.Path, step_id: str) -> pathlib.Path:
    run_dir = temp_root / step_id / "run"
    completed = run_command(
        [
            sys.executable,
            "scripts/create_read_only_calibration_measurement_run.py",
            "--output-dir",
            str(run_dir),
            "--run-id",
            f"rehearsal_{step_id}",
        ]
    )
    if completed.returncode != 0:
        raise RuntimeError(f"failed to create scaffold for {step_id}: {completed.stderr}")
    return run_dir


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
    known_worksheets = set(registry.get("known_worksheets", []))
    expected_worksheets = set(EXPECTED_CSV_HEADERS) | set(OPTIONAL_CSV_HEADERS)
    if known_worksheets != expected_worksheets:
        violations.append("registry known_worksheets do not match read-only template headers")
    for key, value in registry.get("claim_boundary", {}).items():
        if value is not False:
            violations.append(f"registry claim_boundary.{key} is not false")
    for step in finalizer_steps(registry):
        step_id = step.get("step_id")
        if step_id not in REHEARSAL_ROWS:
            violations.append(f"no rehearsal row configured for registered step {step_id!r}")
        if set(step.get("forbidden_actions", [])) != FORBIDDEN_STEP_ACTIONS:
            violations.append(f"registered step {step_id!r} forbidden action set changed")
        allowed = list(step.get("allowed_worksheets", []))
        if len(allowed) != 1:
            violations.append(f"registered step {step_id!r} does not have exactly one worksheet")
        if step_id in REHEARSAL_ROWS and allowed != [REHEARSAL_ROWS[step_id]["worksheet"]]:
            violations.append(f"registered step {step_id!r} worksheet does not match rehearsal row")


def validate_downstream_guard(metrics: dict[str, Any], violations: list[str]) -> None:
    summary = metrics.get("summary", {})
    expected = {
        "audit_passed": True,
        "downstream_row_quality_guard_complete": True,
        "source_phase1_guard_audit_passed": True,
        "case_count": 4,
        "rejected_case_count": 4,
        "scaffold_preserved_case_count": 4,
        "approved_read_only_evidence_created_count": 0,
        "repository_evidence_run_created": False,
        "approved_read_only_evidence_created": False,
        "guard_authorizes_execution": False,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            violations.append(f"v134 source summary {key} is {summary.get(key)!r}, expected {value!r}")


def load_rehearsal_state(run_dir: pathlib.Path, audit_dir: pathlib.Path) -> dict[str, Any]:
    metrics = load_yaml(run_dir / "metrics.yaml")
    audit = load_yaml(audit_dir / "metrics.yaml")
    finalization = metrics.get("read_only_evidence_finalization", {})
    hard_false_execution_fields = {
        key: metrics.get("execution", {}).get(key)
        for key in [
            "robot_motion_commanded",
            "configuration_written",
            "zeroing_or_biasing_performed",
            "force_control_run",
        ]
    }
    hard_false_verdict_fields = {
        key: metrics.get("verdict", {}).get(key)
        for key in [
            "supports_contact_model_update",
            "supports_accepting_v85_margin",
            "supports_gate_relaxation",
            "supports_hardware_claim",
            "supports_more_stage_b_qdot_tuning",
        ]
    }
    return {
        "status_after_rehearsal": metrics.get("status"),
        "audit_passed": audit.get("audit_passed"),
        "audit_mode": audit.get("audit_mode"),
        "audit_violations": audit.get("violations", []),
        "user_confirmed_after_rehearsal": metrics.get("execution", {}).get(
            "user_confirmed_read_only_step"
        ),
        "live_hardware_accessed_after_rehearsal": metrics.get("execution", {}).get(
            "live_hardware_accessed"
        ),
        "hard_false_execution_fields": hard_false_execution_fields,
        "hard_false_verdict_fields": hard_false_verdict_fields,
        "claim_boundary": metrics.get("claim_boundary", {}),
        "evidence_status": metrics.get("evidence_status", {}),
        "orientation_gate_acceptance": metrics.get("orientation_gate_acceptance", {}),
        "read_only_evidence_finalization": finalization,
        "worksheet_row_counts": finalization.get("worksheet_row_counts", {}),
        "allowed_worksheets": finalization.get("allowed_worksheets", []),
    }


def run_rehearsal_case(
    *,
    temp_root: pathlib.Path,
    step: dict[str, Any],
    finalized_at_utc: str,
) -> dict[str, Any]:
    step_id = step["step_id"]
    row_config = REHEARSAL_ROWS[step_id]
    worksheet = row_config["worksheet"]
    evidence_key = row_config["evidence_key"]
    run_dir = create_temp_scaffold(temp_root, step_id)
    append_row(run_dir, worksheet, row_config["row"])
    finalize_command = [
        sys.executable,
        "scripts/finalize_read_only_calibration_measurement_evidence.py",
        str(run_dir),
        "--confirmation-phrase",
        APPROVAL_PHRASE,
        "--approved-step-id",
        step_id,
        "--operator",
        "finalization_rehearsal",
        "--live-hardware-accessed",
        "false",
        "--finalized-at-utc",
        finalized_at_utc,
    ]
    finalize_completed = run_command(finalize_command)
    audit_dir = temp_root / step_id / "audit"
    audit_command = [
        sys.executable,
        "scripts/audit_read_only_calibration_measurement_run.py",
        str(run_dir),
        "--audit-mode",
        "approved-read-only",
        "--output-dir",
        str(audit_dir),
        "--run-id",
        f"rehearsal_audit_{step_id}",
    ]
    audit_completed = run_command(audit_command)
    if not (run_dir / "metrics.yaml").exists() or not (audit_dir / "metrics.yaml").exists():
        return {
            "step_id": step_id,
            "worksheet": worksheet,
            "evidence_key": evidence_key,
            "finalize_returncode": finalize_completed.returncode,
            "audit_returncode": audit_completed.returncode,
            "finalize_stderr_excerpt": finalize_completed.stderr.strip()[:240],
            "audit_stderr_excerpt": audit_completed.stderr.strip()[:240],
            "rehearsal_passed": False,
        }
    state = load_rehearsal_state(run_dir, audit_dir)
    row_counts = state["worksheet_row_counts"]
    populated = [name for name, count in row_counts.items() if count]
    scope_preserved = populated == [worksheet] and state["allowed_worksheets"] == [worksheet]
    evidence_changed_only_for_step = (
        state["evidence_status"].get(evidence_key) == "collected_read_only"
        and all(
            value in {"not_collected", "not_accepted", "collected_read_only"}
            for value in state["evidence_status"].values()
        )
        and populated == [worksheet]
    )
    claim_boundary_preserved = (
        all(value is False for value in state["hard_false_execution_fields"].values())
        and all(value is False for value in state["hard_false_verdict_fields"].values())
        and state["claim_boundary"].get("hardware_readiness") is False
        and state["orientation_gate_acceptance"].get("decision") == "not_accepted"
        and state["orientation_gate_acceptance"].get("evidence_only") is True
    )
    rehearsal_passed = (
        finalize_completed.returncode == 0
        and audit_completed.returncode == 0
        and state["status_after_rehearsal"] == "approved_read_only_evidence"
        and state["audit_mode"] == "approved-read-only"
        and state["audit_passed"] is True
        and state["user_confirmed_after_rehearsal"] is True
        and state["live_hardware_accessed_after_rehearsal"] is False
        and scope_preserved
        and evidence_changed_only_for_step
        and claim_boundary_preserved
    )
    return {
        "step_id": step_id,
        "title": step.get("title"),
        "worksheet": worksheet,
        "evidence_key": evidence_key,
        "temporary_run_dir": str(run_dir),
        "temporary_audit_dir": str(audit_dir),
        "finalize_returncode": finalize_completed.returncode,
        "audit_returncode": audit_completed.returncode,
        "finalize_stderr_excerpt": finalize_completed.stderr.strip()[:240],
        "audit_stderr_excerpt": audit_completed.stderr.strip()[:240],
        "rehearsal_passed": rehearsal_passed,
        "scope_preserved": scope_preserved,
        "evidence_changed_only_for_step": evidence_changed_only_for_step,
        "claim_boundary_preserved": claim_boundary_preserved,
        **state,
    }


def build_payload(
    *,
    registry_path: pathlib.Path,
    downstream_guard_path: pathlib.Path,
    read_only_run_root: pathlib.Path,
    read_only_audit_root: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    if not registry_path.exists():
        violations.append(f"missing registry: {rel(registry_path)}")
        registry: dict[str, Any] = {}
    else:
        registry = load_yaml(registry_path)
        validate_registry(registry, violations)

    if not downstream_guard_path.exists():
        violations.append(f"missing v134 downstream guard metrics: {rel(downstream_guard_path)}")
        downstream_guard: dict[str, Any] = {}
    else:
        downstream_guard = load_yaml(downstream_guard_path)
        validate_downstream_guard(downstream_guard, violations)

    before_state = read_only_repository_state(
        run_root=read_only_run_root,
        audit_root=read_only_audit_root,
    )

    rehearsal_rows: list[dict[str, Any]] = []
    temp_root_removed = False
    temp_root_path = ""
    finalized_at_utc = "2026-05-25T12:20:00Z"
    with tempfile.TemporaryDirectory(prefix="read_only_finalization_rehearsal_") as tmp:
        temp_root = pathlib.Path(tmp)
        temp_root_path = str(temp_root)
        for step in finalizer_steps(registry):
            try:
                rehearsal_rows.append(
                    run_rehearsal_case(
                        temp_root=temp_root,
                        step=step,
                        finalized_at_utc=finalized_at_utc,
                    )
                )
            except Exception as exc:
                rehearsal_rows.append(
                    {
                        "step_id": step.get("step_id"),
                        "worksheet": REHEARSAL_ROWS.get(step.get("step_id"), {}).get("worksheet"),
                        "rehearsal_passed": False,
                        "finalize_returncode": None,
                        "audit_returncode": None,
                        "finalize_stderr_excerpt": str(exc)[:240],
                        "audit_stderr_excerpt": "",
                    }
                )
    if temp_root_path:
        temp_root_removed = not pathlib.Path(temp_root_path).exists()

    after_state = read_only_repository_state(
        run_root=read_only_run_root,
        audit_root=read_only_audit_root,
    )
    if before_state != after_state:
        violations.append("repository read-only evidence state changed during rehearsal")
    if not temp_root_removed:
        violations.append("temporary rehearsal root was not removed")

    for row in rehearsal_rows:
        if row.get("rehearsal_passed") is not True:
            violations.append(f"rehearsal failed for step {row.get('step_id')}")
        if row.get("live_hardware_accessed_after_rehearsal") is not False:
            violations.append(f"rehearsal live_hardware_accessed drift for step {row.get('step_id')}")
        if row.get("claim_boundary_preserved") is not True:
            violations.append(f"rehearsal claim boundary drift for step {row.get('step_id')}")

    expected_step_count = len(finalizer_steps(registry))
    passed_rows = [row for row in rehearsal_rows if row.get("rehearsal_passed") is True]
    temporary_finalization_count = sum(
        1 for row in rehearsal_rows if row.get("status_after_rehearsal") == "approved_read_only_evidence"
    )
    approved_verifier_passed_count = sum(
        1
        for row in rehearsal_rows
        if row.get("audit_mode") == "approved-read-only" and row.get("audit_passed") is True
    )
    live_hardware_accessed_count = sum(
        1 for row in rehearsal_rows if row.get("live_hardware_accessed_after_rehearsal") is True
    )
    repository_approved_run_delta = (
        after_state["approved_read_only_run_count"] - before_state["approved_read_only_run_count"]
    )
    repository_finalization_delta = (
        after_state["read_only_evidence_finalization_present_count"]
        - before_state["read_only_evidence_finalization_present_count"]
    )
    repository_audit_delta = (
        after_state["approved_read_only_audit_passed_count"]
        - before_state["approved_read_only_audit_passed_count"]
    )

    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "finalization_rehearsal_boundary_complete": not violations,
        "source_downstream_guard_audit_passed": downstream_guard.get("summary", {}).get("audit_passed"),
        "registered_finalizer_step_count": expected_step_count,
        "rehearsed_step_count": len(rehearsal_rows),
        "rehearsal_passed_step_count": len(passed_rows),
        "temporary_finalization_count": temporary_finalization_count,
        "approved_read_only_verifier_passed_count": approved_verifier_passed_count,
        "synthetic_row_only_count": len(rehearsal_rows),
        "live_hardware_accessed_count": live_hardware_accessed_count,
        "temporary_root_removed": temp_root_removed,
        "repository_approved_read_only_run_delta": repository_approved_run_delta,
        "repository_finalization_record_delta": repository_finalization_delta,
        "repository_approved_read_only_audit_delta": repository_audit_delta,
        "repository_evidence_run_created_by_rehearsal": repository_approved_run_delta > 0,
        "repository_evidence_audit_created_by_rehearsal": repository_audit_delta > 0,
        "approval_record_created": False,
        "approved_packet_count": 0,
        "execution_authorizing_packet_count": 0,
        "live_access_authorizing_packet_count": 0,
        "approved_read_only_evidence_created": False,
        "rehearsal_authorizes_live_access": False,
        "rehearsal_authorizes_execution": False,
        "rehearsal_creates_repository_evidence": False,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }
    return {
        "run_source": "read-only finalization rehearsal boundary audit",
        "audit_run_id": run_id,
        "source_files": {
            "registry": rel(registry_path),
            "downstream_row_quality_guard": rel(downstream_guard_path),
        },
        "summary": summary,
        "repository_state_before": before_state,
        "repository_state_after": after_state,
        "rehearsal_rows": rehearsal_rows,
        "claim_boundary": {
            "post_hoc_offline_audit_only": True,
            "temporary_rehearsal_only": True,
            "synthetic_rows_only": True,
            "approval_record_created": False,
            "approved_read_only_evidence": False,
            "approved_read_only_evidence_created_in_repository": False,
            "contact_calibration_claim": False,
            "setup_target_acceptance_claim": False,
            "gate_relaxation_claim": False,
            "strict_terminal_relaxation_accepted": False,
            "strict_paper_equivalent_feasibility": False,
            "robustness_claim": False,
            "hardware_readiness": False,
            "live_hardware_access_authorized": False,
            "execution_authorized": False,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "do_not_mark_goal_complete": True,
        },
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Read-Only Finalization Rehearsal Boundary Audit",
        "",
        f"Run id: `{payload['audit_run_id']}`",
        "",
        f"Audit passed: `{summary['audit_passed']}`",
        f"Rehearsal boundary complete: `{summary['finalization_rehearsal_boundary_complete']}`",
        f"Rehearsed steps: `{summary['rehearsal_passed_step_count']} / {summary['registered_finalizer_step_count']}`",
        f"Temporary finalizations: `{summary['temporary_finalization_count']}`",
        f"Approved-read-only verifier passes: `{summary['approved_read_only_verifier_passed_count']}`",
        f"Live hardware accessed in rehearsal: `{summary['live_hardware_accessed_count']}`",
        f"Temporary root removed: `{summary['temporary_root_removed']}`",
        f"Repository approved run delta: `{summary['repository_approved_read_only_run_delta']}`",
        f"Repository finalization record delta: `{summary['repository_finalization_record_delta']}`",
        f"Repository approved audit delta: `{summary['repository_approved_read_only_audit_delta']}`",
        f"Completion claim allowed: `{summary['completion_claim_allowed']}`",
        f"Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "## Rehearsal Rows",
        "",
        "| Step | Worksheet | Rehearsal passed | Scope preserved | Claim boundary preserved |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in payload["rehearsal_rows"]:
        lines.append(
            f"| `{row.get('step_id')}` | `{row.get('worksheet')}` | "
            f"`{row.get('rehearsal_passed')}` | `{row.get('scope_preserved')}` | "
            f"`{row.get('claim_boundary_preserved')}` |"
        )
    lines.extend(["", "## Violations", ""])
    if summary["violations"]:
        lines.extend(f"- {violation}" for violation in summary["violations"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The finalizer and approved-read-only verifier can process one valid "
                "synthetic worksheet row for each registered finalizer step in a "
                "temporary rehearsal area. The temporary area is deleted, the "
                "repository read-only evidence state is unchanged, and no live "
                "access or execution is authorized."
            ),
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--downstream-guard-path", default=str(DEFAULT_DOWNSTREAM_GUARD))
    parser.add_argument("--read-only-run-root", default=str(DEFAULT_READ_ONLY_RUN_ROOT))
    parser.add_argument("--read-only-audit-root", default=str(DEFAULT_READ_ONLY_AUDIT_ROOT))
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "read_only_finalization_rehearsal_boundary" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        registry_path=resolve(args.registry),
        downstream_guard_path=resolve(args.downstream_guard_path),
        read_only_run_root=resolve(args.read_only_run_root),
        read_only_audit_root=resolve(args.read_only_audit_root),
        run_id=run_id,
    )
    payload["audit_root"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[sys.executable, *sys.argv])
    print(out_dir)
    return 0 if payload["summary"]["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
