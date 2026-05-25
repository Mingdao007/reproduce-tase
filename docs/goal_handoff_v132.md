# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V132

Date: 2026-05-25

Use this after the v131 phase1 approved-read-only evidence acceptance boundary
audit. Verify every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v131 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v132.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/phase1_approved_evidence_acceptance_boundary_report.md`
- `runs/phase1_approved_evidence_acceptance_boundary/20260525T114000/metrics.yaml`
- `reports/read_only_phase1_preapproval_finalizer_guard_report.md`
- `runs/read_only_phase1_preapproval_finalizer_guard/20260525T113000/metrics.yaml`
- `reports/read_only_phase1_approval_request_freeze_report.md`
- `runs/read_only_phase1_approval_request_freeze/20260525T112000/metrics.yaml`
- `reports/read_only_next_step_selection_report.md`
- `runs/read_only_next_step_selection/20260525T111000/metrics.yaml`
- `reports/read_only_evidence_dependency_map_report.md`
- `runs/read_only_evidence_dependency_map/20260525T110000/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V131 reports `audit_passed = true`,
`phase1_acceptance_boundary_complete = true`,
`current_repository_scan_finds_no_approved_evidence = true`, read-only runs
`3`, read-only audits `4`, approved read-only runs `0`, phase1 approved
read-only runs `0`, finalization records `0`, passed approved-read-only audits
`0`, `guard_rejected_case_count = 5`,
`guard_approved_evidence_created_count = 0`,
`approved_read_only_evidence_created = false`, `overall_goal_complete = false`,
`completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v131 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v131 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V131 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v131-phase1-evidence-acceptance-boundary
```

V131 artifacts:

```text
scripts/audit_phase1_approved_evidence_acceptance_boundary.py
tests/test_phase1_approved_evidence_acceptance_boundary.py
runs/phase1_approved_evidence_acceptance_boundary/20260525T114000
reports/phase1_approved_evidence_acceptance_boundary_report.md
```

Key result:

```text
audit_passed = true
phase1_acceptance_boundary_complete = true
completion_evidence_ids = []
readiness_artifacts_are_non_evidence = true
current_repository_scan_finds_no_approved_evidence = true
read_only_run_count = 3
read_only_audit_count = 4
approved_read_only_run_count = 0
phase1_approved_read_only_run_count = 0
read_only_evidence_finalization_present_count = 0
approved_read_only_audit_passed_count = 0
phase1_approved_read_only_audit_passed_count = 0
approved_packet_count = 0
execution_authorizing_packet_count = 0
live_access_authorizing_packet_count = 0
guard_rejected_case_count = 5
guard_scaffold_preserved_case_count = 5
guard_approved_evidence_created_count = 0
repository_evidence_run_created_by_guard = false
approved_read_only_evidence_created = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

## Recommended V132 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, use the frozen phase1 request:
`phase1_mounted_stack_tcp_contact_measurement`, worksheet
`tcp_contact_measurements.csv`, and phrase
`I approve this read-only measurement step`. Instantiate a fresh run folder,
fill only `tcp_contact_measurements.csv`, finalize with the matching
registered step ID, and audit in approved-read-only mode.

If no live read-only step is approved, continue only non-final offline probes.
Do not repeat the v113-v116 policy, timing, and terminal-objective families
over the same accepted contact model and seeds. Keep packet coverage,
execution preflight, the v127 dependency map, v128 selector, v129 freeze,
v130 finalizer guard, and v131 acceptance-boundary scan separate from approved
evidence.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Do not use OnRobot direct TCP DAQ as control truth until the force-source
  discrepancy is resolved.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user.

## Validation

- `python3 -m py_compile scripts/audit_phase1_approved_evidence_acceptance_boundary.py`
- `scripts/run_tests.sh tests/test_phase1_approved_evidence_acceptance_boundary.py`
  reported `4 passed in 0.25s`.
- `python3 scripts/audit_phase1_approved_evidence_acceptance_boundary.py --run-id 20260525T114000`
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v131 run
  directory.
- Full tests passed with `227 passed in 15.56s`.
- `git diff --check` passed.
