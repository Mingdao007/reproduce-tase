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
DEFAULT_V139_STATUS = ROOT / "runs" / "full_reproduction_status_after_v138" / "20260525T130000" / "metrics.yaml"
DEFAULT_REGISTRY = ROOT / "configs" / "read_only_sop_step_registry.yaml"
DEFAULT_NEXT_SELECTION = ROOT / "runs" / "read_only_next_step_selection" / "20260525T111000" / "metrics.yaml"
DEFAULT_EXECUTION_PREFLIGHT = ROOT / "runs" / "read_only_step_execution_preflight" / "20260525T101000" / "metrics.yaml"
DEFAULT_OBSERVED_REQUEST = "continue"
REQUIRED_INCOMPLETE_IDS = [
    "approved_read_only_calibration_evidence",
    "contact_setup_target_acceptance",
    "orientation_gate_acceptance",
    "strict_terminal_or_full_staged_feasibility",
    "robustness_to_contact_model_perturbations",
    "hardware_readiness",
]
EXHAUSTED_STRICT_FAMILY_RUNS = [
    ROOT / "runs" / "strict_feasibility_policy_probe" / "20260525T073519" / "metrics.yaml",
    ROOT / "runs" / "strict_command_limited_stage_a" / "20260525T074557" / "metrics.yaml",
    ROOT / "runs" / "explicit_stage_a_constraint_probe" / "20260525T082500" / "metrics.yaml",
    ROOT / "runs" / "strict_terminal_constrained_optimization" / "20260525T085000" / "metrics.yaml",
]


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


def finalizer_step_ids(registry: dict[str, Any]) -> list[str]:
    return [
        step["step_id"]
        for step in registry.get("steps", [])
        if step.get("finalizer_eligible") is True
    ]


def count_existing(paths: list[pathlib.Path]) -> tuple[int, list[str]]:
    existing = [rel(path) for path in paths if path.exists()]
    return len(existing), existing


def build_payload(
    *,
    v139_status_path: pathlib.Path,
    registry_path: pathlib.Path,
    next_selection_path: pathlib.Path,
    execution_preflight_path: pathlib.Path,
    observed_user_request: str,
    claimed_approved_step_id: str,
    run_id: str,
) -> dict[str, Any]:
    violations: list[str] = []
    for name, path in {
        "v139_status": v139_status_path,
        "registry": registry_path,
        "next_selection": next_selection_path,
        "execution_preflight": execution_preflight_path,
    }.items():
        if not path.exists():
            violations.append(f"missing {name} metrics: {rel(path)}")

    v139_status = load_yaml(v139_status_path) if v139_status_path.exists() else {}
    registry = load_yaml(registry_path) if registry_path.exists() else {}
    next_selection = load_yaml(next_selection_path) if next_selection_path.exists() else {}
    execution_preflight = (
        load_yaml(execution_preflight_path) if execution_preflight_path.exists() else {}
    )

    v139_summary = v139_status.get("summary", {})
    registry_steps = finalizer_step_ids(registry)
    next_summary = next_selection.get("summary", {})
    preflight_summary = execution_preflight.get("summary", {})
    approval_phrase = registry.get("approval_phrase")
    first_candidate = next_summary.get("first_candidate_step_id")
    first_worksheet = next_summary.get("first_candidate_worksheet")
    incomplete_ids = v139_summary.get("incomplete_requirement_ids", [])
    missing_required = [
        requirement_id for requirement_id in REQUIRED_INCOMPLETE_IDS if requirement_id not in incomplete_ids
    ]
    strict_run_count, strict_runs = count_existing(EXHAUSTED_STRICT_FAMILY_RUNS)

    exact_phrase_observed = observed_user_request.strip() == approval_phrase
    exact_step_observed = claimed_approved_step_id in registry_steps
    approval_is_exact_and_registered = exact_phrase_observed and exact_step_observed

    expected_false_v139_flags = [
        "full_reproduction_complete",
        "source_overall_goal_complete",
        "source_completion_claim_allowed",
    ]
    for key in expected_false_v139_flags:
        if v139_summary.get(key) is not False:
            violations.append(f"v139 summary {key} is {v139_summary.get(key)!r}, expected False")
    expected_true_v139_flags = [
        "audit_passed",
        "continue_required",
        "source_do_not_mark_goal_complete",
        "do_not_mark_goal_complete",
    ]
    for key in expected_true_v139_flags:
        if v139_summary.get(key) is not True:
            violations.append(f"v139 summary {key} is {v139_summary.get(key)!r}, expected True")
    if v139_summary.get("safe_continuation_mode") != "explicit_read_only_approval_or_nonfinal_offline":
        violations.append("v139 safe continuation mode changed")
    if v139_summary.get("top_blocker") != "approved_read_only_calibration_evidence":
        violations.append("v139 top blocker changed")
    if missing_required:
        violations.append("v139 missing required incomplete IDs: " + ", ".join(missing_required))
    if approval_phrase != "I approve this read-only measurement step":
        violations.append("registry approval phrase mismatch")
    if first_candidate != "phase1_mounted_stack_tcp_contact_measurement":
        violations.append(f"unexpected first read-only candidate: {first_candidate!r}")
    if first_worksheet != "tcp_contact_measurements.csv":
        violations.append(f"unexpected first read-only worksheet: {first_worksheet!r}")
    if next_summary.get("selection_authorizes_live_access") is not False:
        violations.append("next-step selection authorizes live access")
    if next_summary.get("selection_authorizes_execution") is not False:
        violations.append("next-step selection authorizes execution")
    if preflight_summary.get("preflight_authorizes_live_access") is not False:
        violations.append("execution preflight authorizes live access")
    if preflight_summary.get("preflight_authorizes_execution") is not False:
        violations.append("execution preflight authorizes execution")
    if preflight_summary.get("approved_read_only_evidence_created") is not False:
        violations.append("execution preflight created approved evidence")
    if strict_run_count != len(EXHAUSTED_STRICT_FAMILY_RUNS):
        violations.append("strict-family exhaustion evidence missing")

    read_only_sop_can_execute_now = approval_is_exact_and_registered and not violations
    live_access_authorized_now = False
    execution_authorized_now = False
    selected_mode = (
        "exact_approval_detected_but_audit_does_not_execute"
        if approval_is_exact_and_registered
        else "await_exact_phase1_approval_or_nonfinal_offline"
    )

    summary = {
        "audit_passed": not violations,
        "violations": violations,
        "observed_user_request": observed_user_request,
        "approval_phrase_required": approval_phrase,
        "exact_approval_phrase_observed": exact_phrase_observed,
        "claimed_approved_step_id": claimed_approved_step_id,
        "exact_registered_step_observed": exact_step_observed,
        "approval_is_exact_and_registered": approval_is_exact_and_registered,
        "freeform_continue_is_approval": False,
        "selected_safe_continuation_mode": selected_mode,
        "first_read_only_candidate_step_id": first_candidate,
        "first_read_only_candidate_worksheet": first_worksheet,
        "read_only_sop_can_execute_now": read_only_sop_can_execute_now,
        "live_access_authorized_now": live_access_authorized_now,
        "execution_authorized_now": execution_authorized_now,
        "nonfinal_offline_work_allowed": not approval_is_exact_and_registered,
        "strict_policy_terminal_family_exhausted": strict_run_count == len(EXHAUSTED_STRICT_FAMILY_RUNS),
        "strict_family_existing_run_count": strict_run_count,
        "strict_family_existing_runs": strict_runs,
        "repeat_strict_family_recommended": False,
        "v139_full_reproduction_complete": v139_summary.get("full_reproduction_complete"),
        "v139_continue_required": v139_summary.get("continue_required"),
        "v139_top_blocker": v139_summary.get("top_blocker"),
        "v139_incomplete_requirement_count": v139_summary.get("incomplete_requirement_count"),
        "v139_incomplete_requirement_ids": incomplete_ids,
        "required_incomplete_ids_present": not missing_required,
        "missing_required_incomplete_ids": missing_required,
        "approved_read_only_run_count": v139_summary.get("approved_read_only_run_count"),
        "approved_read_only_audit_passed_count": v139_summary.get(
            "approved_read_only_audit_passed_count"
        ),
        "do_not_mark_goal_complete": True,
    }
    return {
        "run_source": "post-v139 continuation boundary audit",
        "audit_run_id": run_id,
        "source_files": {
            "v139_status": rel(v139_status_path),
            "read_only_sop_step_registry": rel(registry_path),
            "read_only_next_step_selection": rel(next_selection_path),
            "read_only_step_execution_preflight": rel(execution_preflight_path),
        },
        "summary": summary,
        "prompt_to_artifact_checklist": [
            {
                "prompt_requirement": "Continue after v139 without explicit live-read approval.",
                "evidence": "observed request, registry approval phrase, and v139 safe continuation mode",
                "status": selected_mode,
            },
            {
                "prompt_requirement": "Do not treat free-form continuation as SOP approval.",
                "evidence": "exact_approval_phrase_observed and exact_registered_step_observed",
                "status": "guarded",
            },
            {
                "prompt_requirement": "Preserve the top blocker and incomplete-requirement set.",
                "evidence": "v139 full reproduction status metrics",
                "status": "preserved" if not missing_required else "violated",
            },
            {
                "prompt_requirement": "Avoid repeating exhausted strict-policy and terminal probes.",
                "evidence": "v113-v116 run artifacts",
                "status": "exhausted_not_recommended",
            },
        ],
        "claim_boundary": {
            "post_hoc_existing_metrics_only": True,
            "new_simulation_run": False,
            "live_hardware_access": False,
            "live_hardware_access_authorized": live_access_authorized_now,
            "execution_authorized": execution_authorized_now,
            "robot_motion_authorized": False,
            "hardware_writes_authorized": False,
            "force_control_authorized": False,
            "approval_record_created": False,
            "approved_read_only_evidence_created": False,
            "contact_calibration_claim": False,
            "setup_target_acceptance_claim": False,
            "orientation_gate_acceptance_claim": False,
            "strict_paper_equivalent_feasibility": False,
            "robustness_proof": False,
            "hardware_readiness": False,
            "completion_claim_allowed": False,
            "do_not_mark_goal_complete": True,
        },
    }


def write_summary(out_dir: pathlib.Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# Post-V139 Continuation Boundary",
        "",
        f"Run root: `{out_dir}`",
        "",
        f"- Audit passed: `{summary['audit_passed']}`",
        f"- Observed user request: `{summary['observed_user_request']}`",
        f"- Required approval phrase: `{summary['approval_phrase_required']}`",
        f"- Exact approval phrase observed: `{summary['exact_approval_phrase_observed']}`",
        f"- Exact registered step observed: `{summary['exact_registered_step_observed']}`",
        f"- Selected safe mode: `{summary['selected_safe_continuation_mode']}`",
        f"- First read-only candidate: `{summary['first_read_only_candidate_step_id']}`",
        f"- First worksheet: `{summary['first_read_only_candidate_worksheet']}`",
        f"- Read-only SOP can execute now: `{summary['read_only_sop_can_execute_now']}`",
        f"- Live access authorized now: `{summary['live_access_authorized_now']}`",
        f"- Execution authorized now: `{summary['execution_authorized_now']}`",
        f"- Repeat strict family recommended: `{summary['repeat_strict_family_recommended']}`",
        f"- Do not mark goal complete: `{summary['do_not_mark_goal_complete']}`",
        "",
        "## Interpretation",
        "",
        "The current continuation request is not the registered read-only",
        "approval phrase, so no live read-only SOP execution is authorized by",
        "this audit. The exact first candidate remains",
        "`phase1_mounted_stack_tcp_contact_measurement` scoped to",
        "`tcp_contact_measurements.csv`. Without that exact approval, only",
        "non-final offline work may continue, and the exhausted v113-v116",
        "strict-feasibility family should not be repeated over the same model",
        "and seeds.",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v139-status", default=str(DEFAULT_V139_STATUS))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--next-selection", default=str(DEFAULT_NEXT_SELECTION))
    parser.add_argument("--execution-preflight", default=str(DEFAULT_EXECUTION_PREFLIGHT))
    parser.add_argument("--observed-user-request", default=DEFAULT_OBSERVED_REQUEST)
    parser.add_argument("--claimed-approved-step-id", default="")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = (
        resolve(args.output_dir)
        if args.output_dir
        else ROOT / "runs" / "post_v139_continuation_boundary" / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        v139_status_path=resolve(args.v139_status),
        registry_path=resolve(args.registry),
        next_selection_path=resolve(args.next_selection),
        execution_preflight_path=resolve(args.execution_preflight),
        observed_user_request=args.observed_user_request,
        claimed_approved_step_id=args.claimed_approved_step_id,
        run_id=run_id,
    )
    payload["audit_root"] = str(out_dir)
    write_yaml(out_dir / "metrics.yaml", payload)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_summary(out_dir, payload)
    write_git_state(out_dir, command=[str(pathlib.Path(sys.argv[0]).resolve()), *sys.argv[1:]])
    print(out_dir)
    return 0 if payload["summary"]["audit_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
