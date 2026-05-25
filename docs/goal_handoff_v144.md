# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V144

Date: 2026-05-25

Use this after the v143 post-v142 completion-gate audit. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v143 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v144.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/post_v142_completion_gate_report.md`
- `runs/post_v142_completion_gate/20260525T170000/metrics.yaml`
- `reports/robustness_dependency_frontier_after_v141_report.md`
- `runs/robustness_dependency_frontier_after_v141/20260525T160000/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V143 classifies the v142 robustness frontier as
non-evidence: `readiness_artifact_count = 7`,
`readiness_completion_evidence_ids = []`,
`robustness_frontier_is_non_evidence = true`,
`v142_closed_cell_count = 0`, `v142_new_simulation_selected = false`,
`v142_additional_failed_cell_execution_recommended = false`, and
`do_not_mark_goal_complete = true`.

The exact first read-only candidate remains
`phase1_mounted_stack_tcp_contact_measurement`, scoped to
`tcp_contact_measurements.csv`, but it may only be executed after explicit user
confirmation with the exact registered phrase
`I approve this read-only measurement step` and exact step scope. Without that
approval, continue only non-final offline work. Do not upgrade v127-v143
readiness/status/frontier artifacts into evidence. Do not repeat the v113-v116
strict-policy/terminal family over the same accepted contact model and seeds,
and do not rerun gate-blocked robustness cells as closure evidence before
approved contact/gate evidence exists. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v143 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V143 Evidence

Expected branch:

```text
exp/tase-ur10e-v143-post-v142-completion-gate
```

V143 artifacts:

```text
scripts/audit_post_v142_completion_gate.py
tests/test_post_v142_completion_gate.py
runs/post_v142_completion_gate/20260525T170000
reports/post_v142_completion_gate_report.md
```

Key result:

```text
audit_passed = true
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
readiness_artifact_count = 7
readiness_completion_evidence_ids = []
robustness_frontier_is_non_evidence = true
v142_robustness_complete = false
v142_accepted_as_robustness_proof = false
v142_closed_cell_count = 0
v142_new_simulation_selected = false
v142_additional_failed_cell_execution_recommended = false
```

## Recommended V144 Work

If the user gives the exact approval phrase and exact phase1 scope, use only
that one audited packet and registered step. Instantiate a fresh scaffold run,
fill only valid `tcp_contact_measurements.csv` rows, finalize with
`phase1_mounted_stack_tcp_contact_measurement`, and audit in
approved-read-only mode.

If no exact approval exists, continue only non-final offline work that does not
upgrade v127-v143 readiness/status/frontier artifacts into evidence. Do not
rerun the v113-v116 strict-policy/terminal family or gate-blocked robustness
rows as closure evidence before approved contact/gate evidence exists.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user using the exact registered approval scope.

## Validation

- `python3 -m py_compile scripts/audit_post_v142_completion_gate.py`
- `scripts/run_tests.sh tests/test_post_v142_completion_gate.py`
  reported `4 passed in 0.48s`.
- `python3 scripts/audit_post_v142_completion_gate.py --run-id 20260525T170000`

Full tests, YAML anchor scan, raw/heavy artifact scan, and `git diff --check`
are pending final closeout for this branch.
