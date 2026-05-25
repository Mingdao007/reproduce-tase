# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V136

Date: 2026-05-25

Use this after the v135 read-only finalization rehearsal boundary audit.
Verify every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v135 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v136.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_finalization_rehearsal_boundary_report.md`
- `runs/read_only_finalization_rehearsal_boundary/20260525T122000/metrics.yaml`
- `reports/downstream_row_quality_guard_report.md`
- `runs/downstream_row_quality_guard/20260525T121000/metrics.yaml`
- `reports/phase1_row_quality_guard_report.md`
- `runs/phase1_row_quality_guard/20260525T120000/metrics.yaml`
- `reports/read_only_evidence_sequence_boundary_report.md`
- `runs/read_only_evidence_sequence_boundary/20260525T115000/metrics.yaml`
- `reports/phase1_approved_evidence_acceptance_boundary_report.md`
- `runs/phase1_approved_evidence_acceptance_boundary/20260525T114000/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V135 reports `audit_passed = true`,
`finalization_rehearsal_boundary_complete = true`, registered finalizer steps
`5`, rehearsed steps `5`, temporary finalizations `5`, approved-read-only
verifier passes `5`, synthetic rows only `5`, live hardware accessed `0`,
temporary root removed true, repository approved-read-only run delta `0`,
repository finalization record delta `0`, repository approved-read-only audit
delta `0`, `approved_read_only_evidence_created = false`,
`rehearsal_authorizes_execution = false`, `completion_claim_allowed = false`,
and `do_not_mark_goal_complete = true`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v135 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v135 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V135 Evidence

Expected branch:

```text
exp/tase-ur10e-v135-finalization-rehearsal-boundary
```

V135 artifacts:

```text
scripts/audit_read_only_finalization_rehearsal_boundary.py
tests/test_read_only_finalization_rehearsal_boundary.py
runs/read_only_finalization_rehearsal_boundary/20260525T122000
reports/read_only_finalization_rehearsal_boundary_report.md
```

Key result:

```text
finalization_rehearsal_boundary_complete = true
registered_finalizer_step_count = 5
rehearsed_step_count = 5
rehearsal_passed_step_count = 5
temporary_finalization_count = 5
approved_read_only_verifier_passed_count = 5
synthetic_row_only_count = 5
live_hardware_accessed_count = 0
temporary_root_removed = true
repository_approved_read_only_run_delta = 0
repository_finalization_record_delta = 0
repository_approved_read_only_audit_delta = 0
repository_evidence_run_created_by_rehearsal = false
approval_record_created = false
approved_read_only_evidence_created = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

## Recommended V136 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, use only that packet's exact step ID and
worksheet scope. Instantiate a fresh run folder, fill only valid rows for the
approved worksheet, finalize with the matching registered step ID, and audit in
approved-read-only mode. Do not bundle multiple registered steps into one
approval.

If no live read-only step is approved, continue only non-final offline probes.
Do not repeat the v113-v116 policy, timing, and terminal-objective families
over the same accepted contact model and seeds. Keep v127-v135 readiness,
sequence, acceptance, row-quality, and finalization-rehearsal artifacts
separate from approved evidence.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user.

## Validation

- `python3 -m py_compile scripts/audit_read_only_finalization_rehearsal_boundary.py`
- `scripts/run_tests.sh tests/test_read_only_finalization_rehearsal_boundary.py`
  reported `4 passed in 6.16s`.
- `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py tests/test_downstream_row_quality_guard.py tests/test_read_only_finalization_rehearsal_boundary.py`
  reported `25 passed in 12.74s`.
- `python3 scripts/audit_read_only_finalization_rehearsal_boundary.py --run-id 20260525T122000`
- Full tests reported `247 passed in 29.31s`.
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v135 run
  directory.
- `git diff --check` passed.
