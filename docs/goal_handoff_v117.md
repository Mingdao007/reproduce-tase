# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V117

Date: 2026-05-25

Use this after the v116 strict terminal constrained optimization audit. Verify
every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v116 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v117.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/offline_completion_blockers_report.md`
- `reports/strict_feasibility_blockers_report.md`
- `reports/remaining_blocker_prioritization_report.md`
- `reports/strict_feasibility_policy_probe_report.md`
- `reports/strict_command_limited_stage_a_report.md`
- `reports/explicit_stage_a_constraint_probe_report.md`
- `reports/strict_terminal_constrained_optimization_report.md`
- `runs/remaining_blocker_prioritization/20260525T072557/metrics.yaml`
- `runs/strict_feasibility_policy_probe/20260525T073519/metrics.yaml`
- `runs/strict_command_limited_stage_a/20260525T074557/metrics.yaml`
- `runs/explicit_stage_a_constraint_probe/20260525T082500/metrics.yaml`
- `runs/strict_terminal_constrained_optimization/20260525T085000/metrics.yaml`
- `reports/read_only_calibration_measurement_sop.md`
- `reports/read_only_calibration_measurement_orientation_acceptance_boundary_report.md`
- `reports/orientation_gate_acceptance_review_template_report.md`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, not contact
calibrated, and not hardware-ready. The UR10e adapted line is diagnostic
simulation only. V112 ranks the remaining blockers: top priority is
`approved_read_only_calibration_evidence`, remaining blocker count is `6`,
live/approval-blocked count is `4`, offline-actionable non-final count is `2`,
closed cells remain `0`, candidate matrix complete is `false`, and
`do_not_mark_goal_complete = true`. V113 probes strict feasibility with eight
E2 Stage A policies and still reports setup terminal-state pass `0 / 8`.
V114 command-limited Stage A still reports strict setup-chain pass `0 / 4`.
V115 explicit terminal/path constraints report strict setup-path pass `0 / 5`,
terminal strict-criteria pass `0 / 5`, qdot-criteria pass `5 / 5`, and planned
setup-then-trajectory pass `0 / 5`. V116 stronger bounded smooth-minimax
terminal optimization reports strict terminal pass `0 / 12`, improves the v56
strict best max-gate ratio from `2.413534442118322` to
`2.11994927622362`, but the best target-contacting row still fails force,
x/y, and orientation thresholds. Strict paper-equivalent feasibility remains
`false`, and `do_not_mark_goal_complete = true`.

Concrete v117 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. With no
approval, avoid repeating v113 instantaneous priority, v114 command limiting,
v115 terminal/path timing, or v116 bounded smooth-minimax terminal optimization
over the same accepted contact model and seeds. The practical next blocker is
approved read-only calibration evidence or a new explicitly accepted
contact/setup-target definition. Do not move the real UR10e. Do not write TCP,
payload, CoG, URCap settings, OnRobot settings, RTDE registers,
zero/bias/filter settings, or run force control unless the user separately
approves that exact SOP step.
```

## Current Verified V116 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v116-strict-terminal-constrained-optimization
```

Verified implementation commit:

```text
b956ee36c659fb01bc23fc7d3db3e66bed9e8077
```

V116 strict terminal constrained optimization artifacts:

```text
scripts/audit_strict_terminal_constrained_optimization.py
tests/test_strict_terminal_constrained_optimization.py
runs/strict_terminal_constrained_optimization/20260525T085000
reports/strict_terminal_constrained_optimization_report.md
```

Key result:

```text
strict_terminal_pass_count = 0 / 12
best_max_gate_ratio = 2.11994927622362
v56_strict_best_max_gate_ratio = 2.413534442118322
strict_paper_equivalent_feasibility = false
do_not_mark_goal_complete = true
```

## Recommended V117 Work

Start with explicit user approval before any live bench read. If a specific
read-only step is approved, instantiate a fresh run folder, collect only the
approved worksheet rows, then run:

```bash
python3 scripts/finalize_read_only_calibration_measurement_evidence.py <run-folder> \
  --confirmation-phrase "I approve this read-only measurement step" \
  --approved-step-id <approved-step-id> \
  --operator <operator> \
  --live-hardware-accessed true

python3 scripts/audit_read_only_calibration_measurement_run.py <run-folder> \
  --audit-mode approved-read-only
```

If no live read-only step is approved, continue only non-final offline probes:

- Use v116 as the latest strict terminal compatibility boundary.
- Treat `approved_read_only_calibration_evidence` as the top overall blocker.
- Avoid repeating v113-v116 matrices over the same policy, timing, seed, and
  objective families.
- Keep gate acceptance, contact calibration, hardware readiness, failed-cell
  closure, canonical controller changes, and robustness claims false unless a
  later audit supplies stronger evidence.

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
