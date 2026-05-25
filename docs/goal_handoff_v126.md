# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V126

Date: 2026-05-25

Use this after the v125 strict-terminal tradeoff boundary audit. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v125 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v126.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/strict_terminal_tradeoff_boundary_report.md`
- `runs/strict_terminal_tradeoff_boundary/20260525T104000/metrics.yaml`
- `reports/paper_platform_claim_boundary_report.md`
- `runs/paper_platform_claim_boundary/20260525T103000/metrics.yaml`
- `reports/post_v122_completion_gate_report.md`
- `runs/post_v122_completion_gate/20260525T102000/metrics.yaml`
- `reports/read_only_step_execution_preflight_report.md`
- `runs/read_only_step_execution_preflight/20260525T101000/metrics.yaml`
- `reports/read_only_step_approval_packet_coverage_report.md`
- `runs/read_only_step_approval_packet_coverage/20260525T100500/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V125 reports `audit_passed = true`,
`strict_terminal_pass_count = 0`,
`best_combined_max_gate_ratio = 2.11994927622362`,
`best_combined_failed_all_three_scalar_gates = true`,
`force_xy_without_orientation_count = 1`,
`xy_orientation_without_force_or_contact_count = 2`,
`tradeoff_boundary_preserved = true`, `new_optimization_run = false`,
`overall_goal_complete = false`, `completion_claim_allowed = false`, and
`do_not_mark_goal_complete = true`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v125 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v125 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current Verified V125 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v125-strict-terminal-tradeoff-boundary
```

Verified implementation commit:

```text
PENDING_BRANCH_CLOSE_COMMIT
```

V125 artifacts:

```text
scripts/audit_strict_terminal_tradeoff_boundary.py
tests/test_strict_terminal_tradeoff_boundary.py
runs/strict_terminal_tradeoff_boundary/20260525T104000
reports/strict_terminal_tradeoff_boundary_report.md
```

Key result:

```text
audit_passed = true
strict_terminal_pass_count = 0
optimization_case_count = 12
best_combined_case_id = xy_force_orientation__best_candidate__slsqp
best_combined_max_gate_ratio = 2.11994927622362
best_combined_failed_all_three_scalar_gates = true
force_xy_without_orientation_count = 1
xy_orientation_without_force_or_contact_count = 2
tradeoff_boundary_preserved = true
new_optimization_run = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

## Recommended V126 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, instantiate a fresh run folder, fill only
that registered step's allowed worksheet, finalize with the matching
registered step ID, and audit in approved-read-only mode.

If no live read-only step is approved, continue only non-final offline probes:

- Treat `approved_read_only_calibration_evidence` as the top overall blocker.
- Keep packet coverage and preflight readiness separate from evidence.
- Keep formula-convergence and tuned Fig.6 paper-platform evidence separate
  from full paper-equivalent parity.
- Do not repeat the v116 bounded smooth-minimax optimizer over the same
  accepted contact model and seeds as a likely closer.
- Keep contact/setup-target acceptance, orientation gate acceptance, contact
  calibration, robustness proof, strict feasibility, and hardware readiness
  false unless a later audit supplies stronger evidence.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Do not use OnRobot direct TCP DAQ as control truth until the force-source
  discrepancy is resolved.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user.

## Validation

- `python3 -m py_compile scripts/audit_strict_terminal_tradeoff_boundary.py`
- `scripts/run_tests.sh tests/test_strict_terminal_tradeoff_boundary.py`
  reported `3 passed in 0.24s`.
- `python3 scripts/audit_strict_terminal_tradeoff_boundary.py --run-id 20260525T104000`
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v125 run
  directory.
- Full tests passed with `208 passed in 11.32s`.
- `git diff --check` passed.
