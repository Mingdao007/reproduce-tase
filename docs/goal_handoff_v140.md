# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V140

Date: 2026-05-25

Use this after the v139 full-reproduction status audit. Verify every claim from
repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v139 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v140.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/full_reproduction_status_after_v138_report.md`
- `runs/full_reproduction_status_after_v138/20260525T130000/metrics.yaml`
- `reports/post_v137_completion_gate_report.md`
- `runs/post_v137_completion_gate/20260525T125000/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V139 directly answers the user's completion
question with `user_question_answer = not_fully_reproduced`,
`full_reproduction_complete = false`, `continue_required = true`,
`safe_continuation_mode = explicit_read_only_approval_or_nonfinal_offline`,
`top_blocker = approved_read_only_calibration_evidence`,
`incomplete_requirement_count = 6`, approved read-only runs `0`, passed
approved-read-only audits `0`, strict terminal pass count `0`, closed
robustness cells `0`, hardware gate report false, and
`do_not_mark_goal_complete = true`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v139 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v139 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V139 Evidence

Expected branch:

```text
exp/tase-ur10e-v139-full-reproduction-status
```

V139 artifacts:

```text
scripts/audit_full_reproduction_status_after_v138.py
tests/test_full_reproduction_status_after_v138.py
runs/full_reproduction_status_after_v138/20260525T130000
reports/full_reproduction_status_after_v138_report.md
```

Key result:

```text
user_question_answer = not_fully_reproduced
full_reproduction_complete = false
continue_required = true
safe_continuation_mode = explicit_read_only_approval_or_nonfinal_offline
top_blocker = approved_read_only_calibration_evidence
incomplete_requirement_count = 6
approved_read_only_run_count = 0
approved_read_only_audit_passed_count = 0
strict_terminal_pass_count = 0
closed_robustness_cell_count = 0
hardware_gate_report_exists = false
do_not_mark_goal_complete = true
```

## Recommended V140 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, use only that packet's exact step ID and
worksheet scope. Instantiate a fresh run folder, fill only valid rows for the
approved worksheet, finalize with the matching registered step ID, and audit in
approved-read-only mode. Do not bundle multiple registered steps into one
approval.

If no live read-only step is approved, continue only non-final offline probes.
Do not repeat the v113-v116 policy, timing, and terminal-objective families
over the same accepted contact model and seeds. Keep v127-v139 readiness,
sequence, acceptance, row-quality, finalization-rehearsal, completion-gate,
margin-separation, and status artifacts separate from approved evidence.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user.

## Validation

- `python3 -m py_compile scripts/audit_full_reproduction_status_after_v138.py`
- `scripts/run_tests.sh tests/test_full_reproduction_status_after_v138.py`
  reported `4 passed in 0.13s`.
- `python3 scripts/audit_full_reproduction_status_after_v138.py --run-id 20260525T130000`
- Full tests, YAML anchor scan, raw/heavy artifact scan, and `git diff --check`
  are recorded in the v139 iteration log.
