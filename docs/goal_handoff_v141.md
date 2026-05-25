# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V141

Date: 2026-05-25

Use this after the v140 post-v139 continuation-boundary audit. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v140 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v141.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/post_v139_continuation_boundary_report.md`
- `runs/post_v139_continuation_boundary/20260525T140000/metrics.yaml`
- `reports/full_reproduction_status_after_v138_report.md`
- `runs/full_reproduction_status_after_v138/20260525T130000/metrics.yaml`
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
`full_reproduction_complete = false`, `continue_required = true`, and
`do_not_mark_goal_complete = true`. V140 confirms that the current free-form
continuation request is not the exact approval phrase
`I approve this read-only measurement step`, so
`read_only_sop_can_execute_now = false`, `live_access_authorized_now = false`,
and `execution_authorized_now = false`.

The exact first read-only candidate remains
`phase1_mounted_stack_tcp_contact_measurement`, scoped to
`tcp_contact_measurements.csv`, but it may only be executed after explicit user
confirmation with the exact registered phrase and exact step scope. Without
that approval, continue only non-final offline work. Do not repeat the
v113-v116 strict-policy/terminal family over the same accepted contact model
and seeds. Use the v117 scaffold before accepting any contact/setup-target
definition. Keep strict paper-equivalent setup, v38 relaxed
trajectory-after-setup, and v63-v140 diagnostic staged labels separate. Do not
move or configure the real UR10e; real hardware work is read-only unless a
separate approved SOP exists.
```

## Current V140 Evidence

Expected branch:

```text
exp/tase-ur10e-v140-post-status-continuation-boundary
```

V140 artifacts:

```text
scripts/audit_post_v139_continuation_boundary.py
tests/test_post_v139_continuation_boundary.py
runs/post_v139_continuation_boundary/20260525T140000
reports/post_v139_continuation_boundary_report.md
```

Key result:

```text
audit_passed = true
freeform_continue_is_approval = false
selected_safe_continuation_mode = await_exact_phase1_approval_or_nonfinal_offline
first_read_only_candidate_step_id = phase1_mounted_stack_tcp_contact_measurement
first_read_only_candidate_worksheet = tcp_contact_measurements.csv
read_only_sop_can_execute_now = false
live_access_authorized_now = false
execution_authorized_now = false
nonfinal_offline_work_allowed = true
strict_policy_terminal_family_exhausted = true
repeat_strict_family_recommended = false
do_not_mark_goal_complete = true
```

## Recommended V141 Work

If the user gives the exact approval phrase and exact phase1 scope, use only
that one audited packet and registered step. Instantiate a fresh scaffold run,
fill only valid `tcp_contact_measurements.csv` rows, finalize with
`phase1_mounted_stack_tcp_contact_measurement`, and audit in
approved-read-only mode.

If no exact approval exists, continue only non-final offline work that is not a
repeat of the v113-v116 strict-feasibility policy and terminal-objective
family. Do not upgrade v127-v140 readiness, sequence, acceptance, row-quality,
finalization-rehearsal, completion-gate, margin-separation, status, or
continuation-boundary artifacts into evidence.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user using the exact registered approval scope.

## Validation

- `python3 -m py_compile scripts/audit_post_v139_continuation_boundary.py`
- `scripts/run_tests.sh tests/test_post_v139_continuation_boundary.py`
  reported `4 passed in 0.16s`.
- `python3 scripts/audit_post_v139_continuation_boundary.py --run-id 20260525T140000 --observed-user-request '019e5d70-5cf8-7553-aa82-1b3cf93759f9 continue'`

Full tests, YAML anchor scan, raw/heavy artifact scan, and `git diff --check`
are pending final closeout for this branch.
