# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V131

Date: 2026-05-25

Use this after the v130 phase1 preapproval finalizer guard audit. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v130 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v131.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
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
is diagnostic simulation only. V130 reports `audit_passed = true`,
`preapproval_finalizer_guard_complete = true`, case count `5`, rejected cases
`5`, scaffold-preserved cases `5`,
`approved_read_only_evidence_created_count = 0`,
`successful_finalization_count = 0`,
`repository_evidence_run_created = false`, `temp_only_dry_run = true`,
`guard_authorizes_live_access = false`, `guard_authorizes_execution = false`,
`overall_goal_complete = false`, `completion_claim_allowed = false`, and
`do_not_mark_goal_complete = true`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v130 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v130 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V130 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v130-phase1-preapproval-finalizer-guard
```

V130 artifacts:

```text
scripts/audit_read_only_phase1_preapproval_finalizer_guard.py
tests/test_read_only_phase1_preapproval_finalizer_guard.py
runs/read_only_phase1_preapproval_finalizer_guard/20260525T113000
reports/read_only_phase1_preapproval_finalizer_guard_report.md
```

Key result:

```text
audit_passed = true
preapproval_finalizer_guard_complete = true
case_count = 5
rejected_case_count = 5
scaffold_preserved_case_count = 5
approved_read_only_evidence_created_count = 0
successful_finalization_count = 0
repository_evidence_run_created = false
temp_only_dry_run = true
approved_packet_count = 0
execution_authorizing_packet_count = 0
live_access_authorizing_packet_count = 0
approved_read_only_evidence_created = false
guard_authorizes_live_access = false
guard_authorizes_execution = false
guard_creates_approved_evidence = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

## Recommended V131 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, use the frozen phase1 request:
`phase1_mounted_stack_tcp_contact_measurement`, worksheet
`tcp_contact_measurements.csv`, and phrase
`I approve this read-only measurement step`. Instantiate a fresh run folder,
fill only `tcp_contact_measurements.csv`, finalize with the matching registered
step ID, and audit in approved-read-only mode.

If no live read-only step is approved, continue only non-final offline probes:

- Treat `approved_read_only_calibration_evidence` as the top overall blocker.
- Keep packet coverage, execution preflight, the v127 dependency map, the v128
  selector, v129 freeze, and v130 finalizer guard separate from approved
  evidence.
- Keep formula-convergence and tuned Fig.6 paper-platform evidence separate
  from full paper-equivalent parity.
- Do not accept any strict-terminal relaxation from v126; it is a budget audit
  only and accepts no gate change.
- Keep contact/setup-target acceptance, orientation gate acceptance, contact
  calibration, robustness proof, strict feasibility, and hardware readiness
  false unless a later audit supplies stronger evidence.

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

- `python3 -m py_compile scripts/audit_read_only_phase1_preapproval_finalizer_guard.py`
- `scripts/run_tests.sh tests/test_read_only_phase1_preapproval_finalizer_guard.py`
  reported `3 passed in 3.21s`.
- `python3 scripts/audit_read_only_phase1_preapproval_finalizer_guard.py --run-id 20260525T113000`
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v130 run
  directory.
- Full tests passed with `223 passed in 15.10s`.
- `git diff --check` passed.
