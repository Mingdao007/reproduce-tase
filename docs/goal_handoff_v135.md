# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V135

Date: 2026-05-25

Use this after the v134 downstream row-quality guard audit. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v134 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v135.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
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
is diagnostic simulation only. V134 reports `audit_passed = true`,
`downstream_row_quality_guard_complete = true`, rejected row-quality cases
`4 / 4`, scaffold-preserved cases `4 / 4`,
`approved_read_only_evidence_created_count = 0`,
`repository_evidence_run_created = false`, guarded downstream steps `4`, and
guards worksheets `ksm_contact_patch_convention.csv`,
`plane_normal_measurements.csv`, `force_source_comparison.csv`, and
`orientation_gate_semantics.csv`. It also keeps approved packets `0`,
execution-authorizing packets `0`, live-access-authorizing packets `0`,
`guard_authorizes_execution = false`, `completion_claim_allowed = false`, and
`do_not_mark_goal_complete = true`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v134 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v134 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V134 Evidence

Expected branch:

```text
exp/tase-ur10e-v134-downstream-row-quality-guard
```

V134 artifacts:

```text
scripts/audit_read_only_calibration_measurement_run.py
scripts/finalize_read_only_calibration_measurement_evidence.py
scripts/audit_downstream_row_quality_guard.py
tests/test_downstream_row_quality_guard.py
runs/downstream_row_quality_guard/20260525T121000
reports/downstream_row_quality_guard_report.md
```

Key result:

```text
downstream_row_quality_guard_complete = true
case_count = 4
rejected_case_count = 4
scaffold_preserved_case_count = 4
approved_read_only_evidence_created_count = 0
repository_evidence_run_created = false
guarded_downstream_step_count = 4
approved_read_only_evidence_created = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

## Recommended V135 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, use only that packet's exact step ID and
worksheet scope. Instantiate a fresh run folder, fill only valid rows for the
approved worksheet, finalize with the matching registered step ID, and audit in
approved-read-only mode. Do not bundle multiple registered steps into one
approval.

If no live read-only step is approved, continue only non-final offline probes.
Do not repeat the v113-v116 policy, timing, and terminal-objective families
over the same accepted contact model and seeds. Keep v127-v134 readiness,
sequence, acceptance, and row-quality guard artifacts separate from approved
evidence.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user.

## Validation

- `python3 -m py_compile scripts/audit_read_only_calibration_measurement_run.py scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_downstream_row_quality_guard.py`
- `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py tests/test_downstream_row_quality_guard.py`
  reported `21 passed in 6.27s`.
- `python3 scripts/audit_downstream_row_quality_guard.py --run-id 20260525T121000`
- Full tests reported `243 passed in 23.16s`.
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v134 run
  directory.
- `git diff --check` passed.
