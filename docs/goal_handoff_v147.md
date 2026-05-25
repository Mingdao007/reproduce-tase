# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V147

Date: 2026-05-25

Use this after the v146 post-v145 offline blocker boundary audit. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v146 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v147.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/post_v145_offline_blocker_boundary_report.md`
- `runs/post_v145_offline_blocker_boundary/20260525T200000/metrics.yaml`
- `reports/user_completion_criterion_after_v144_report.md`
- `runs/user_completion_criterion_after_v144/20260525T190000/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: v146 confirms v145's two offline/non-final
blockers remain unresolved and that there is no known safe non-repeating
offline shortcut to close them:
`completion_closing_offline_shortcut_count = 0`,
`safe_nonrepeating_completion_action_available = false`,
`completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.
The unresolved offline/non-final requirements are still
`strict_terminal_or_full_staged_feasibility` and
`robustness_to_contact_model_perturbations`.

The exact first read-only candidate remains
`phase1_mounted_stack_tcp_contact_measurement`, scoped to
`tcp_contact_measurements.csv`, but it may only be executed after explicit user
confirmation with the exact registered phrase
`I approve this read-only measurement step` and exact step scope. Without that
approval, continue only non-final offline work. Do not upgrade v127-v146
readiness/status/frontier/freshness/criterion/boundary artifacts into
evidence. Do not repeat the v113-v116 strict-policy/terminal family over the
same accepted contact model and seeds, and do not rerun gate-blocked robustness
cells as closure evidence before approved contact/gate evidence exists. Keep
strict paper-equivalent setup, v38 relaxed trajectory-after-setup, and
v63-v146 diagnostic staged labels separate. Do not move or configure the real
UR10e; real hardware work is read-only unless a separate approved SOP exists.
```

## Current V146 Evidence

Expected branch:

```text
exp/tase-ur10e-v146-offline-blocker-boundary
```

V146 artifacts:

```text
scripts/audit_post_v145_offline_blocker_boundary.py
tests/test_post_v145_offline_blocker_boundary.py
runs/post_v145_offline_blocker_boundary/20260525T200000
reports/post_v145_offline_blocker_boundary_report.md
```

Key result:

```text
audit_passed = true
user_completion_criterion_met = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
offline_nonfinal_unresolved_count = 2
completion_closing_offline_shortcut_count = 0
safe_nonrepeating_completion_action_available = false
```

## Recommended V147 Work

If the user gives the exact approval phrase and exact phase1 scope, use only
that one audited packet and registered step. Instantiate a fresh scaffold run,
fill only valid `tcp_contact_measurements.csv` rows, finalize with
`phase1_mounted_stack_tcp_contact_measurement`, and audit in
approved-read-only mode.

If no exact approval exists, continue only non-final offline work that does not
upgrade v127-v146 readiness/status/frontier/freshness/criterion/boundary
artifacts into evidence. Do not rerun the v113-v116 strict-policy/terminal
family or gate-blocked robustness rows as closure evidence before approved
contact/gate evidence exists.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user using the exact registered approval scope.

## Validation

- `python3 -m py_compile scripts/audit_post_v145_offline_blocker_boundary.py`
- `scripts/run_tests.sh tests/test_post_v145_offline_blocker_boundary.py`
  reported `4 passed in 0.29s`.
- `python3 scripts/audit_post_v145_offline_blocker_boundary.py --run-id 20260525T200000`
- Full tests passed with `291 passed in 32.10s`.
- YAML anchor scan found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads in the v146 run artifact.
- `git diff --check` passed.
- Implementation commit:
  `4ce5b9c386301d8d4580be21f1c3ddbffbd1544b`
