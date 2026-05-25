# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V137

Date: 2026-05-25

Use this after the v136 post-v135 completion gate audit. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v136 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v137.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/post_v135_completion_gate_report.md`
- `runs/post_v135_completion_gate/20260525T123000/metrics.yaml`
- `reports/read_only_finalization_rehearsal_boundary_report.md`
- `runs/read_only_finalization_rehearsal_boundary/20260525T122000/metrics.yaml`
- `reports/downstream_row_quality_guard_report.md`
- `runs/downstream_row_quality_guard/20260525T121000/metrics.yaml`
- `reports/phase1_row_quality_guard_report.md`
- `runs/phase1_row_quality_guard/20260525T120000/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V136 reports `audit_passed = true`,
`overall_goal_complete = false`, `completion_claim_allowed = false`,
`do_not_mark_goal_complete = true`, top blocker
`approved_read_only_calibration_evidence`, approved read-only runs `0`,
approved-read-only audits `0`, accepted orientation reviews `0`, accepted
contact/setup-target reviews `0`, strict terminal pass count `0`, closed
robustness cells `0`, hardware gate report false, readiness artifact count
`3`, `readiness_completion_evidence_ids = []`,
`readiness_artifacts_are_non_evidence = true`, and
`finalization_rehearsal_is_non_evidence = true`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v136 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v136 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V136 Evidence

Expected branch:

```text
exp/tase-ur10e-v136-post-rehearsal-completion-gate
```

V136 artifacts:

```text
scripts/audit_post_v135_completion_gate.py
tests/test_post_v135_completion_gate.py
runs/post_v135_completion_gate/20260525T123000
reports/post_v135_completion_gate_report.md
```

Key result:

```text
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
top_blocker = approved_read_only_calibration_evidence
approved_read_only_run_count = 0
approved_read_only_audit_passed_count = 0
accepted_orientation_review_count = 0
accepted_contact_setup_target_review_count = 0
strict_terminal_pass_count = 0
closed_robustness_cell_count = 0
hardware_gate_report_exists = false
readiness_artifact_count = 3
readiness_completion_evidence_ids = []
readiness_artifacts_are_non_evidence = true
finalization_rehearsal_is_non_evidence = true
```

## Recommended V137 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, use only that packet's exact step ID and
worksheet scope. Instantiate a fresh run folder, fill only valid rows for the
approved worksheet, finalize with the matching registered step ID, and audit in
approved-read-only mode. Do not bundle multiple registered steps into one
approval.

If no live read-only step is approved, continue only non-final offline probes.
Do not repeat the v113-v116 policy, timing, and terminal-objective families
over the same accepted contact model and seeds. Keep v127-v136 readiness,
sequence, acceptance, row-quality, finalization-rehearsal, and completion-gate
artifacts separate from approved evidence.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user.

## Validation

- `python3 -m py_compile scripts/audit_post_v135_completion_gate.py`
- `scripts/run_tests.sh tests/test_post_v135_completion_gate.py`
  reported `4 passed in 0.45s`.
- `scripts/run_tests.sh tests/test_post_v117_evidence_readiness.py tests/test_post_v122_completion_gate.py tests/test_post_v135_completion_gate.py`
  reported `10 passed in 0.95s`.
- `python3 scripts/audit_post_v135_completion_gate.py --run-id 20260525T123000`
- Full tests reported `251 passed in 29.98s`.
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v136 run
  directory.
- `git diff --check` passed.
