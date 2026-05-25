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

DEFAULT_REGISTRY = "configs/read_only_sop_step_registry.yaml"
DEFAULT_MEASURED_GEOMETRY = "runs/measured_geometry_readiness/20260525T000739/metrics.yaml"
DEFAULT_REMAINING_BLOCKERS = "runs/remaining_blocker_prioritization/20260525T072557/metrics.yaml"
DEFAULT_RELAXATION_BUDGET = "runs/strict_terminal_relaxation_budget/20260525T105000/metrics.yaml"
DEFAULT_PACKET_COVERAGE = "runs/read_only_step_approval_packet_coverage/20260525T100500/metrics.yaml"
DEFAULT_PREFLIGHT = "runs/read_only_step_execution_preflight/20260525T101000/metrics.yaml"


READINESS_TO_STEP = {
    "mounted_stack_tcp_contact_point": {
        "step_id": "phase1_mounted_stack_tcp_contact_measurement",
        "worksheet": "tcp_contact_measurements.csv",
        "evidence_role": "mounted stack TCP/contact point",
    },
    "contact_patch_convention": {
        "step_id": "phase2_ksm_contact_patch_convention",
        "worksheet": "ksm_contact_patch_convention.csv",
        "evidence_role": "KSM contact patch convention",
    },
    "plane_contact_normal": {
        "step_id": "phase3_plane_normal_external_measurement",
        "worksheet": "plane_normal_measurements.csv",
        "evidence_role": "robot-base contact plane normal",
    },
    "force_source_frame": {
        "step_id": "phase4_force_source_read_only_comparison",
        "worksheet": "force_source_comparison.csv",
        "evidence_role": "force source/frame reconciliation",
    },
    "orientation_gate_semantics": {
        "step_id": "phase5_orientation_gate_semantics_evidence",
        "worksheet": "orientation_gate_semantics.csv",
        "evidence_role": "orientation gate semantics and uncertainty",
    },
}

ALL_STEP_IDS = [entry["step_id"] for entry in READINESS_TO_STEP.values()]

BLOCKER_DEPENDENCIES = {
    "approved_read_only_calibration_evidence": ALL_STEP_IDS,
    "calibrated_contact_geometry": [
        "phase1_mounted_stack_tcp_contact_measurement",
        "phase2_ksm_contact_patch_convention",
        "phase3_plane_normal_external_measurement",
        "phase4_force_source_read_only_comparison",
    ],
    "orientation_gate_acceptance": [
        "phase1_mounted_stack_tcp_contact_measurement",
        "phase2_ksm_contact_patch_convention",
        "phase3_plane_normal_external_measurement",
        "phase5_orientation_gate_semantics_evidence",
    ],
    "strict_paper_equivalent_full_staged_feasibility": ALL_STEP_IDS,
    "robustness_to_contact_model_perturbations": ALL_STEP_IDS,
    "hardware_readiness": ALL_STEP_IDS,
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


def by_key(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {str(row.get(key)): row for row in rows if row.get(key) is not None}


def int_value(mapping: dict[str, Any], key: str) -> int:
    return int(mapping.get(key) or 0)


def build_step_dependency_rows(
    *,
    registry: dict[str, Any],
    measured_geometry: dict[str, Any],
    packet_coverage: dict[str, Any],
    preflight: dict[str, Any],
    violations: list[str],
) -> list[dict[str, Any]]:
    registry_steps = by_key(registry.get("steps", []), "step_id")
    readiness_checks = by_key(measured_geometry.get("readiness_checks", []), "name")
    coverage_rows = by_key(packet_coverage.get("coverage_rows", []), "step_id")
    preflight_rows = by_key(preflight.get("preflight_rows", []), "step_id")
    finalizer_step_ids = {
        step_id for step_id, step in registry_steps.items() if step.get("finalizer_eligible") is True
    }
    mapped_step_ids = {entry["step_id"] for entry in READINESS_TO_STEP.values()}

    if finalizer_step_ids != mapped_step_ids:
        missing = sorted(finalizer_step_ids - mapped_step_ids)
        extra = sorted(mapped_step_ids - finalizer_step_ids)
        if missing:
            violations.append(f"finalizer-eligible registry steps missing from map: {missing}")
        if extra:
            violations.append(f"mapped steps are not finalizer-eligible registry steps: {extra}")

    rows: list[dict[str, Any]] = []
    for readiness_name, mapping in READINESS_TO_STEP.items():
        step_id = mapping["step_id"]
        worksheet = mapping["worksheet"]
        readiness = readiness_checks.get(readiness_name)
        step = registry_steps.get(step_id)
        coverage = coverage_rows.get(step_id)
        preflight_row = preflight_rows.get(step_id)

        if readiness is None:
            violations.append(f"missing measured-geometry readiness check: {readiness_name}")
            readiness = {}
        if step is None:
            violations.append(f"missing registry step: {step_id}")
            step = {}
        if coverage is None:
            violations.append(f"missing approval-packet coverage row: {step_id}")
            coverage = {}
        if preflight_row is None:
            violations.append(f"missing execution-preflight row: {step_id}")
            preflight_row = {}

        allowed_worksheets = step.get("allowed_worksheets", [])
        if step.get("finalizer_eligible") is not True:
            violations.append(f"mapped registry step is not finalizer eligible: {step_id}")
        if allowed_worksheets != [worksheet]:
            violations.append(
                f"worksheet mismatch for {step_id}: expected {[worksheet]}, got {allowed_worksheets}"
            )
        if coverage.get("coverage_passed") is not True:
            violations.append(f"approval-packet coverage is not passed for {step_id}")
        if int_value(coverage, "valid_not_approved_packet_count") < 1:
            violations.append(f"no valid not-approved packet is mapped for {step_id}")
        if preflight_row.get("preflight_ready") is not True:
            violations.append(f"execution preflight is not ready for {step_id}")

        worksheet_statuses = preflight_row.get("worksheet_statuses", [])
        worksheet_status = next(
            (status for status in worksheet_statuses if status.get("worksheet") == worksheet),
            {},
        )
        if worksheet_status.get("header_matches") is not True:
            violations.append(f"preflight worksheet header is not matched for {step_id}")

        rows.append(
            {
                "readiness_check": readiness_name,
                "readiness_status": readiness.get("status"),
                "has_measured_record": readiness.get("has_measured_record"),
                "constrains_v85_margin": readiness.get("constrains_v85_margin"),
                "evidence_role": mapping["evidence_role"],
                "required_next": readiness.get("required_next", []),
                "step_id": step_id,
                "title": step.get("title"),
                "worksheet": worksheet,
                "finalizer_eligible": step.get("finalizer_eligible"),
                "packet_coverage_passed": coverage.get("coverage_passed"),
                "valid_not_approved_packet_count": int_value(
                    coverage, "valid_not_approved_packet_count"
                ),
                "valid_packet_paths": [
                    packet.get("packet_path") for packet in coverage.get("valid_packets", [])
                ],
                "preflight_ready": preflight_row.get("preflight_ready"),
                "preflight_valid_packet_paths": [
                    packet.get("packet_metrics")
                    for packet in preflight_row.get("valid_not_approved_packets", [])
                ],
                "worksheet_header_matched": worksheet_status.get("header_matches"),
                "post_approval_command_plan": preflight_row.get("post_approval_command_plan", []),
                "blocker_ids_supported": [
                    blocker_id
                    for blocker_id, step_ids in BLOCKER_DEPENDENCIES.items()
                    if step_id in step_ids
                ],
                "approval_required": True,
                "live_authorized_now": False,
                "execution_authorized_now": False,
                "creates_completion_evidence": False,
            }
        )
    return rows


def build_blocker_dependency_rows(
    *,
    remaining_blockers: dict[str, Any],
    step_dependency_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    blockers = by_key(remaining_blockers.get("blocker_rows", []), "blocker_id")
    steps_by_id = {row["step_id"]: row for row in step_dependency_rows}
    rows: list[dict[str, Any]] = []
    for blocker_id, required_step_ids in BLOCKER_DEPENDENCIES.items():
        blocker = blockers.get(blocker_id, {})
        required_rows = [steps_by_id.get(step_id, {}) for step_id in required_step_ids]
        all_packet_covered = all(row.get("packet_coverage_passed") is True for row in required_rows)
        all_preflight_ready = all(row.get("preflight_ready") is True for row in required_rows)
        rows.append(
            {
                "blocker_id": blocker_id,
                "title": blocker.get("title"),
                "source_status": blocker.get("status"),
                "source_priority_rank": blocker.get("priority_rank"),
                "source_requires_explicit_approval": blocker.get("requires_explicit_approval"),
                "source_completion_claim_allowed": blocker.get("completion_claim_allowed"),
                "required_step_ids": required_step_ids,
                "required_worksheets": [
                    steps_by_id.get(step_id, {}).get("worksheet") for step_id in required_step_ids
                ],
                "all_packets_covered": all_packet_covered,
                "all_preflight_ready": all_preflight_ready,
                "approved_evidence_exists": False,
                "completion_claim_allowed": False,
                "status": (
                    "packet_preflight_ready_but_approval_missing"
                    if all_packet_covered and all_preflight_ready
                    else "dependency_map_incomplete"
                ),
            }
        )
    return rows


def validate_sources(
    *,
    registry: dict[str, Any],
    measured_geometry: dict[str, Any],
    remaining_blockers: dict[str, Any],
    relaxation_budget: dict[str, Any],
    packet_coverage: dict[str, Any],
    preflight: dict[str, Any],
    violations: list[str],
) -> None:
    registry_boundary = registry.get("claim_boundary", {})
    for key in [
        "registry_authorizes_live_access",
        "registry_authorizes_robot_motion",
        "registry_authorizes_configuration_writes",
        "registry_authorizes_zeroing_or_biasing",
        "registry_authorizes_force_control",
        "registry_accepts_contact_model",
        "registry_accepts_setup_target",
        "registry_accepts_orientation_gate",
        "registry_establishes_hardware_readiness",
    ]:
        if registry_boundary.get(key) is not False:
            violations.append(f"registry claim boundary drifted true: {key}")

    if measured_geometry.get("verdict", {}).get("records_sufficient_for_v85_margin") is not False:
        violations.append("measured-geometry source no longer rejects v85 margin sufficiency")
    if measured_geometry.get("verdict", {}).get("supports_gate_relaxation") is not False:
        violations.append("measured-geometry source now supports gate relaxation")
    if remaining_blockers.get("summary", {}).get("overall_goal_complete") is not False:
        violations.append("remaining-blocker source no longer reports incomplete goal")
    if remaining_blockers.get("summary", {}).get("completion_claim_allowed_count") != 0:
        violations.append("remaining-blocker source now has completion-claim-allowed blockers")
    if relaxation_budget.get("summary", {}).get("relaxation_budget_acceptance_allowed") is not False:
        violations.append("v126 relaxation-budget source now allows gate relaxation")
    if relaxation_budget.get("summary", {}).get("do_not_mark_goal_complete") is not True:
        violations.append("v126 relaxation-budget source no longer blocks goal completion")

    coverage_summary = packet_coverage.get("summary", {})
    if coverage_summary.get("audit_passed") is not True:
        violations.append("approval-packet coverage audit is not passed")
    if coverage_summary.get("coverage_complete") is not True:
        violations.append("approval-packet coverage is not complete")
    if coverage_summary.get("covered_step_count") != len(ALL_STEP_IDS):
        violations.append("approval-packet coverage count does not match mapped finalizer steps")
    if coverage_summary.get("approved_packet_count") != 0:
        violations.append("approval-packet coverage source contains approved packets")
    if coverage_summary.get("execution_authorizing_packet_count") != 0:
        violations.append("approval-packet coverage source contains execution-authorizing packets")
    if coverage_summary.get("live_access_authorizing_packet_count") != 0:
        violations.append("approval-packet coverage source contains live-access-authorizing packets")

    preflight_summary = preflight.get("summary", {})
    if preflight_summary.get("audit_passed") is not True:
        violations.append("execution preflight audit is not passed")
    if preflight_summary.get("preflight_ready_step_count") != len(ALL_STEP_IDS):
        violations.append("execution preflight ready count does not match mapped finalizer steps")
    if preflight_summary.get("approved_packet_count") != 0:
        violations.append("execution preflight source contains approved packets")
    if preflight_summary.get("execution_authorizing_packet_count") != 0:
        violations.append("execution preflight source contains execution-authorizing packets")
    if preflight_summary.get("live_access_authorizing_packet_count") != 0:
        violations.append("execution preflight source contains live-access-authorizing packets")
    if preflight_summary.get("explicit_user_approval_required") is not True:
        violations.append("execution preflight no longer requires explicit user approval")
    if preflight_summary.get("preflight_authorizes_live_access") is not False:
        violations.append("execution preflight now authorizes live access")
    if preflight_summary.get("preflight_authorizes_execution") is not False:
        violations.append("execution preflight now authorizes execution")
    if preflight_summary.get("approved_read_only_evidence_created") is not False:
        violations.append("execution preflight now claims approved read-only evidence")


def build_payload(
    *,
    registry_path: pathlib.Path,
    measured_geometry_path: pathlib.Path,
    remaining_blockers_path: pathlib.Path,
    relaxation_budget_path: pathlib.Path,
    packet_coverage_path: pathlib.Path,
    preflight_path: pathlib.Path,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    for path in [
        registry_path,
        measured_geometry_path,
        remaining_blockers_path,
        relaxation_budget_path,
        packet_coverage_path,
        preflight_path,
    ]:
        if not path.exists():
            violations.append(f"missing required source file: {rel(path)}")

    registry = load_yaml(registry_path) if registry_path.exists() else {}
    measured_geometry = load_yaml(measured_geometry_path) if measured_geometry_path.exists() else {}
    remaining_blockers = load_yaml(remaining_blockers_path) if remaining_blockers_path.exists() else {}
    relaxation_budget = load_yaml(relaxation_budget_path) if relaxation_budget_path.exists() else {}
    packet_coverage = load_yaml(packet_coverage_path) if packet_coverage_path.exists() else {}
    preflight = load_yaml(preflight_path) if preflight_path.exists() else {}

    validate_sources(
        registry=registry,
        measured_geometry=measured_geometry,
        remaining_blockers=remaining_blockers,
        relaxation_budget=relaxation_budget,
        packet_coverage=packet_coverage,
        preflight=preflight,
        violations=violations,
    )
    step_rows = build_step_dependency_rows(
        registry=registry,
        measured_geometry=measured_geometry,
        packet_coverage=packet_coverage,
        preflight=preflight,
        violations=violations,
    )
    blocker_rows = build_blocker_dependency_rows(
        remaining_blockers=remaining_blockers,
        step_dependency_rows=step_rows,
    )

    coverage_summary = packet_coverage.get("summary", {})
    preflight_summary = preflight.get("summary", {})
    mapped_step_count = len({row["step_id"] for row in step_rows})
    packet_covered_step_count = sum(1 for row in step_rows if row["packet_coverage_passed"] is True)
    preflight_ready_step_count = sum(1 for row in step_rows if row["preflight_ready"] is True)
    approved_packet_count = max(
        int_value(coverage_summary, "approved_packet_count"),
        int_value(preflight_summary, "approved_packet_count"),
    )
    execution_authorizing_packet_count = max(
        int_value(coverage_summary, "execution_authorizing_packet_count"),
        int_value(preflight_summary, "execution_authorizing_packet_count"),
    )
    live_access_authorizing_packet_count = max(
        int_value(coverage_summary, "live_access_authorizing_packet_count"),
        int_value(preflight_summary, "live_access_authorizing_packet_count"),
    )
    approved_read_only_evidence_created = bool(
        preflight_summary.get("approved_read_only_evidence_created")
    )
    execution_authorized = bool(preflight_summary.get("preflight_authorizes_execution"))
    live_access_authorized = bool(preflight_summary.get("preflight_authorizes_live_access"))

    dependency_map_complete = (
        mapped_step_count == len(ALL_STEP_IDS)
        and packet_covered_step_count == len(ALL_STEP_IDS)
        and preflight_ready_step_count == len(ALL_STEP_IDS)
        and not violations
    )
    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "dependency_map_complete": dependency_map_complete,
        "mapped_readiness_check_count": len(step_rows),
        "finalizer_step_count": len(ALL_STEP_IDS),
        "mapped_step_count": mapped_step_count,
        "packet_covered_step_count": packet_covered_step_count,
        "preflight_ready_step_count": preflight_ready_step_count,
        "approved_packet_count": approved_packet_count,
        "execution_authorizing_packet_count": execution_authorizing_packet_count,
        "live_access_authorizing_packet_count": live_access_authorizing_packet_count,
        "approved_read_only_evidence_created": approved_read_only_evidence_created,
        "explicit_user_approval_required": bool(
            preflight_summary.get("explicit_user_approval_required")
        ),
        "live_access_authorized": live_access_authorized,
        "execution_authorized": execution_authorized,
        "overall_goal_complete": False,
        "completion_claim_allowed": False,
        "do_not_mark_goal_complete": True,
    }

    return {
        "run_source": "read-only evidence dependency map audit",
        "audit_run_id": run_id,
        "source_files": {
            "read_only_sop_step_registry": rel(registry_path),
            "measured_geometry_readiness": rel(measured_geometry_path),
            "remaining_blocker_prioritization": rel(remaining_blockers_path),
            "strict_terminal_relaxation_budget": rel(relaxation_budget_path),
            "read_only_step_approval_packet_coverage": rel(packet_coverage_path),
            "read_only_step_execution_preflight": rel(preflight_path),
        },
        "summary": summary,
        "step_dependency_rows": step_rows,
        "blocker_dependency_rows": blocker_rows,
        "source_guardrails": {
            "registry_approval_phrase": registry.get("approval_phrase"),
            "remaining_top_priority_blocker_id": remaining_blockers.get("summary", {}).get(
                "top_priority_blocker_id"
            ),
            "remaining_overall_goal_complete": remaining_blockers.get("summary", {}).get(
                "overall_goal_complete"
            ),
            "v126_relaxation_budget_acceptance_allowed": relaxation_budget.get("summary", {}).get(
                "relaxation_budget_acceptance_allowed"
            ),
            "packet_coverage_complete": coverage_summary.get("coverage_complete"),
            "preflight_authorizes_execution": preflight_summary.get(
                "preflight_authorizes_execution"
            ),
            "preflight_authorizes_live_access": preflight_summary.get(
                "preflight_authorizes_live_access"
            ),
            "approved_read_only_evidence_created": preflight_summary.get(
                "approved_read_only_evidence_created"
            ),
        },
        "claim_boundary": {
            "dependency_map_only": True,
            "readiness_artifacts_are_non_evidence": True,
            "approved_read_only_evidence": False,
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
        "# Read-Only Evidence Dependency Map Audit",
        "",
        f"Run id: `{payload['audit_run_id']}`",
        "",
        f"Audit passed: `{summary['audit_passed']}`",
        f"Dependency map complete: `{summary['dependency_map_complete']}`",
        f"Mapped readiness checks: `{summary['mapped_readiness_check_count']}`",
        f"Mapped finalizer steps: `{summary['mapped_step_count']}`",
        f"Packet-covered steps: `{summary['packet_covered_step_count']}`",
        f"Preflight-ready steps: `{summary['preflight_ready_step_count']}`",
        f"Approved packets: `{summary['approved_packet_count']}`",
        f"Execution-authorizing packets: `{summary['execution_authorizing_packet_count']}`",
        f"Live-access-authorizing packets: `{summary['live_access_authorizing_packet_count']}`",
        f"Approved read-only evidence created: `{summary['approved_read_only_evidence_created']}`",
        f"Explicit user approval required: `{summary['explicit_user_approval_required']}`",
        f"Completion claim allowed: `{summary['completion_claim_allowed']}`",
        f"Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "Mapped steps:",
        "",
        "| Readiness check | Step | Worksheet | Packet covered | Preflight ready |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for row in payload["step_dependency_rows"]:
        lines.append(
            f"| `{row['readiness_check']}` | `{row['step_id']}` | "
            f"`{row['worksheet']}` | `{row['packet_coverage_passed']}` | "
            f"`{row['preflight_ready']}` |"
        )
    lines.extend(["", "Blocker dependencies:", ""])
    for row in payload["blocker_dependency_rows"]:
        lines.append(
            f"- `{row['blocker_id']}`: `{row['status']}`; steps "
            f"`{', '.join(row['required_step_ids'])}`"
        )
    lines.extend(["", "Violations:", ""])
    if summary["violations"]:
        lines.extend(f"- {violation}" for violation in summary["violations"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            (
                "The read-only evidence path is mapped from each unresolved readiness "
                "check to an exact registered SOP step, audited not-approved packet, "
                "and preflight-ready worksheet. This map is readiness bookkeeping "
                "only. It creates no approved evidence, authorizes no live access or "
                "execution, and leaves completion blocked on explicit approval and "
                "later accepted evidence."
            ),
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--registry-path", default=DEFAULT_REGISTRY)
    parser.add_argument("--measured-geometry-path", default=DEFAULT_MEASURED_GEOMETRY)
    parser.add_argument("--remaining-blockers-path", default=DEFAULT_REMAINING_BLOCKERS)
    parser.add_argument("--relaxation-budget-path", default=DEFAULT_RELAXATION_BUDGET)
    parser.add_argument("--packet-coverage-path", default=DEFAULT_PACKET_COVERAGE)
    parser.add_argument("--preflight-path", default=DEFAULT_PREFLIGHT)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "read_only_evidence_dependency_map" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(
        registry_path=resolve(args.registry_path),
        measured_geometry_path=resolve(args.measured_geometry_path),
        remaining_blockers_path=resolve(args.remaining_blockers_path),
        relaxation_budget_path=resolve(args.relaxation_budget_path),
        packet_coverage_path=resolve(args.packet_coverage_path),
        preflight_path=resolve(args.preflight_path),
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
