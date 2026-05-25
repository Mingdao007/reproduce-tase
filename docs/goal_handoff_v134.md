# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V134

Date: 2026-05-25

Use this after the v133 phase1 row-quality guard audit. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v133 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v134.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/phase1_row_quality_guard_report.md`
- `runs/phase1_row_quality_guard/20260525T120000/metrics.yaml`
- `reports/read_only_evidence_sequence_boundary_report.md`
- `runs/read_only_evidence_sequence_boundary/20260525T115000/metrics.yaml`
- `reports/phase1_approved_evidence_acceptance_boundary_report.md`
- `runs/phase1_approved_evidence_acceptance_boundary/20260525T114000/metrics.yaml`
- `reports/read_only_phase1_preapproval_finalizer_guard_report.md`
- `runs/read_only_phase1_preapproval_finalizer_guard/20260525T113000/metrics.yaml`
- `reports/read_only_phase1_approval_request_freeze_report.md`
- `runs/read_only_phase1_approval_request_freeze/20260525T112000/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V133 reports `audit_passed = true`,
`phase1_row_quality_guard_complete = true`, rejected row-quality cases `5 / 5`,
scaffold-preserved cases `5 / 5`,
`approved_read_only_evidence_created_count = 0`,
`repository_evidence_run_created = false`, guarded step
`phase1_mounted_stack_tcp_contact_measurement`, guarded worksheet
`tcp_contact_measurements.csv`, approved packets `0`,
execution-authorizing packets `0`, live-access-authorizing packets `0`,
`guard_authorizes_execution = false`, `completion_claim_allowed = false`, and
`do_not_mark_goal_complete = true`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v133 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v133 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V133 Evidence

Expected branch:

```text
exp/tase-ur10e-v133-phase1-row-quality-guard
```

V133 artifacts:

```text
scripts/audit_read_only_calibration_measurement_run.py
scripts/finalize_read_only_calibration_measurement_evidence.py
scripts/audit_phase1_row_quality_guard.py
tests/test_read_only_calibration_measurement_template.py
tests/test_phase1_row_quality_guard.py
runs/phase1_row_quality_guard/20260525T120000
reports/phase1_row_quality_guard_report.md
```

Key result:

```text
phase1_row_quality_guard_complete = true
case_count = 5
rejected_case_count = 5
scaffold_preserved_case_count = 5
approved_read_only_evidence_created_count = 0
repository_evidence_run_created = false
guarded_step_id = phase1_mounted_stack_tcp_contact_measurement
guarded_worksheet = tcp_contact_measurements.csv
approved_read_only_evidence_created = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

## Recommended V134 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, use the frozen phase1 request:
`phase1_mounted_stack_tcp_contact_measurement`, worksheet
`tcp_contact_measurements.csv`, and phrase
`I approve this read-only measurement step`. Instantiate a fresh run folder,
fill only valid `tcp_contact_measurements.csv` rows, finalize with the matching
registered step ID, and audit in approved-read-only mode. Do not bundle
phase2-phase5 into that approval.

If no live read-only step is approved, continue only non-final offline probes.
Do not repeat the v113-v116 policy, timing, and terminal-objective families
over the same accepted contact model and seeds. Keep v127-v133 readiness,
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

- `python3 -m py_compile scripts/audit_read_only_calibration_measurement_run.py scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_phase1_row_quality_guard.py`
- `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py tests/test_phase1_row_quality_guard.py`
  reported `17 passed in 6.00s`.
- `python3 scripts/audit_phase1_row_quality_guard.py --run-id 20260525T120000`
- Full tests reported `236 passed in 19.47s`.
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v133 run
  directory.
- `git diff --check` passed.
