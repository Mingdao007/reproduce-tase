# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V146

Date: 2026-05-25

Use this after the v145 user-completion-criterion audit. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v145 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v146.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/user_completion_criterion_after_v144_report.md`
- `runs/user_completion_criterion_after_v144/20260525T190000/metrics.yaml`
- `reports/phase1_packet_freshness_after_v143_report.md`
- `runs/phase1_packet_freshness_after_v143/20260525T180000/metrics.yaml`
- `runs/post_v142_completion_gate/20260525T170000/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: v145 directly answers the user's
real-data-only completion criterion and returns
`answer = not_complete_not_only_real_data_missing`,
`user_completion_criterion_met = false`,
`only_real_or_explicit_approval_data_missing = false`,
`offline_nonfinal_unresolved_count = 2`, and
`do_not_mark_goal_complete = true`. The unresolved offline/non-final
requirements are `strict_terminal_or_full_staged_feasibility` and
`robustness_to_contact_model_perturbations`. The approval/live-data blocked
requirements are `approved_read_only_calibration_evidence`,
`contact_setup_target_acceptance`, `orientation_gate_acceptance`, and
`hardware_readiness`.

The exact first read-only candidate remains
`phase1_mounted_stack_tcp_contact_measurement`, scoped to
`tcp_contact_measurements.csv`, but it may only be executed after explicit user
confirmation with the exact registered phrase
`I approve this read-only measurement step` and exact step scope. Without that
approval, continue only non-final offline work. Do not upgrade v127-v145
readiness/status/frontier/freshness/criterion artifacts into evidence. Do not
repeat the v113-v116 strict-policy/terminal family over the same accepted
contact model and seeds, and do not rerun gate-blocked robustness cells as
closure evidence before approved contact/gate evidence exists. Keep strict
paper-equivalent setup, v38 relaxed trajectory-after-setup, and v63-v145
diagnostic staged labels separate. Do not move or configure the real UR10e;
real hardware work is read-only unless a separate approved SOP exists.
```

## Current V145 Evidence

Expected branch:

```text
exp/tase-ur10e-v145-user-completion-criterion
```

V145 artifacts:

```text
scripts/audit_user_completion_criterion_after_v144.py
tests/test_user_completion_criterion_after_v144.py
runs/user_completion_criterion_after_v144/20260525T190000
reports/user_completion_criterion_after_v144_report.md
```

Key result:

```text
audit_passed = true
answer = not_complete_not_only_real_data_missing
user_completion_criterion_met = false
only_real_or_explicit_approval_data_missing = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
incomplete_requirement_count = 6
approval_or_live_data_blocked_count = 4
offline_nonfinal_unresolved_count = 2
```

## Recommended V146 Work

If the user gives the exact approval phrase and exact phase1 scope, use only
that one audited packet and registered step. Instantiate a fresh scaffold run,
fill only valid `tcp_contact_measurements.csv` rows, finalize with
`phase1_mounted_stack_tcp_contact_measurement`, and audit in
approved-read-only mode.

If no exact approval exists, continue only non-final offline work that does not
upgrade v127-v145 readiness/status/frontier/freshness/criterion artifacts into
evidence. Do not rerun the v113-v116 strict-policy/terminal family or
gate-blocked robustness rows as closure evidence before approved contact/gate
evidence exists.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user using the exact registered approval scope.

## Validation

- `python3 -m py_compile scripts/audit_user_completion_criterion_after_v144.py`
- `scripts/run_tests.sh tests/test_user_completion_criterion_after_v144.py`
  reported `4 passed in 0.18s`.
- `python3 scripts/audit_user_completion_criterion_after_v144.py --run-id 20260525T190000`

Full tests, YAML anchor scan, raw/heavy artifact scan, and `git diff --check`
are pending final closeout for this branch.
