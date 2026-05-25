# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V143

Date: 2026-05-25

Use this after the v142 robustness-dependency frontier audit. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v142 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v143.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/robustness_dependency_frontier_after_v141_report.md`
- `runs/robustness_dependency_frontier_after_v141/20260525T160000/metrics.yaml`
- `reports/post_v140_completion_gate_report.md`
- `runs/post_v140_completion_gate/20260525T150000/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V142 classifies the remaining robustness
frontier without running new simulations: `closed_cell_count = 0`,
`accepted_as_robustness_proof = false`,
`profile_overlay_supported_noncanonical_cell_ids = [base_z_plus1mm,
positive_fast_timing_0p0075]`,
`gate_or_contact_acceptance_blocked_cell_ids =
[positive_orientation_gate_0p119, weighted_plus1mm_0p119_gate]`,
`new_simulation_selected = false`,
`additional_failed_cell_execution_recommended = false`, and
`do_not_mark_goal_complete = true`.

The exact first read-only candidate remains
`phase1_mounted_stack_tcp_contact_measurement`, scoped to
`tcp_contact_measurements.csv`, but it may only be executed after explicit user
confirmation with the exact registered phrase
`I approve this read-only measurement step` and exact step scope. Without that
approval, continue only non-final offline work. Do not repeat the v113-v116
strict-policy/terminal family over the same accepted contact model and seeds,
and do not rerun gate-blocked robustness cells as closure evidence before
approved contact/gate evidence exists. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v142 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V142 Evidence

Expected branch:

```text
exp/tase-ur10e-v142-robustness-dependency-frontier
```

V142 artifacts:

```text
scripts/audit_robustness_dependency_frontier_after_v141.py
tests/test_robustness_dependency_frontier_after_v141.py
runs/robustness_dependency_frontier_after_v141/20260525T160000
reports/robustness_dependency_frontier_after_v141_report.md
```

Key result:

```text
audit_passed = true
robustness_complete = false
accepted_as_robustness_proof = false
closed_cell_count = 0
frontier_row_count = 4
profile_overlay_supported_noncanonical_count = 2
gate_or_contact_acceptance_blocked_count = 2
new_simulation_selected = false
additional_failed_cell_execution_recommended = false
requires_approved_read_only_evidence_for_closure = true
requires_contact_setup_target_acceptance_for_closure = true
requires_orientation_gate_acceptance_for_gate_rows = true
do_not_mark_goal_complete = true
```

## Recommended V143 Work

If the user gives the exact approval phrase and exact phase1 scope, use only
that one audited packet and registered step. Instantiate a fresh scaffold run,
fill only valid `tcp_contact_measurements.csv` rows, finalize with
`phase1_mounted_stack_tcp_contact_measurement`, and audit in
approved-read-only mode.

If no exact approval exists, continue only non-final offline work that does not
upgrade v127-v142 readiness/status/frontier artifacts into evidence. Do not
rerun the v113-v116 strict-policy/terminal family or the gate-blocked
robustness rows as closure evidence before approved contact/gate evidence
exists.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user using the exact registered approval scope.

## Validation

- `python3 -m py_compile scripts/audit_robustness_dependency_frontier_after_v141.py`
- `scripts/run_tests.sh tests/test_robustness_dependency_frontier_after_v141.py`
  reported `4 passed in 0.16s`.
- `python3 scripts/audit_robustness_dependency_frontier_after_v141.py --run-id 20260525T160000`
- Full tests passed with `275 passed in 31.32s`.
- YAML anchor scan found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads in the v142 run artifact.
- `git diff --check` passed.
