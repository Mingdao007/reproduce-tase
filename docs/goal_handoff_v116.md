# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V116

Date: 2026-05-25

Use this after the v115 explicit Stage A constraint probe. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v115 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v116.md`
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
- `runs/remaining_blocker_prioritization/20260525T072557/metrics.yaml`
- `runs/strict_feasibility_policy_probe/20260525T073519/metrics.yaml`
- `runs/strict_command_limited_stage_a/20260525T074557/metrics.yaml`
- `runs/explicit_stage_a_constraint_probe/20260525T082500/metrics.yaml`
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
E2 Stage A policies and still reports setup terminal-state pass `0 / 8`,
planned setup-then-trajectory pass `0 / 8`, and full staged feasibility pass
`0 / 8`. V114 changes Stage A command generation before allocation and still
reports strict setup-chain pass `0 / 4`, planned setup-then-trajectory pass
`0 / 4`, final x/y failures `4 / 4`, setup qdot saturation failures `4 / 4`,
setup tail qdot utilization failures `4 / 4`, strict paper-equivalent
feasibility `false`, and `do_not_mark_goal_complete = true`. V115 tests
explicit terminal/path constraints using the v56 contact-manifold cases and
the v62 diagnostic path reference. It reports strict setup-path pass `0 / 5`,
terminal strict-criteria pass `0 / 5`, qdot-criteria pass `5 / 5`, planned
setup-then-trajectory pass `0 / 5`, strict paper-equivalent feasibility
`false`, and `do_not_mark_goal_complete = true`.

Concrete v116 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. With no
approval, treat v115 as showing that qdot saturation can be removed by
explicit timing, but strict terminal compatibility remains blocked. The next
offline strict-feasibility step should either test a stronger constrained
optimization over the accepted contact model or wait for approved read-only
calibration evidence that can justify changing the setup target/contact model.
Do not move the real UR10e. Do not write TCP, payload, CoG, URCap settings,
OnRobot settings, RTDE registers, zero/bias/filter settings, or run force
control unless the user separately approves that exact SOP step.
```

## Current Verified V115 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v115-explicit-stage-a-constraint-probe
```

Verified implementation commit:

```text
IMPLEMENTATION_COMMIT_PENDING
```

V115 explicit Stage A constraint artifacts:

```text
scripts/audit_explicit_stage_a_constraint_probe.py
tests/test_explicit_stage_a_constraint_probe.py
runs/explicit_stage_a_constraint_probe/20260525T082500
reports/explicit_stage_a_constraint_probe_report.md
```

Key result:

```text
strict_setup_path_pass_count = 0 / 5
terminal_strict_criteria_pass_count = 0 / 5
qdot_criteria_pass_count = 5 / 5
planned_setup_then_trajectory_pass_count = 0 / 5
strict_paper_equivalent_feasibility = false
do_not_mark_goal_complete = true
```

## Recommended V116 Work

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

- Use v115 as the latest strict Stage A terminal/path constraint boundary.
- Treat `approved_read_only_calibration_evidence` as the top overall blocker.
- Treat strict feasibility as the highest-priority offline-actionable blocker.
- Avoid repeating v113 instantaneous priority, v114 command-limiting, or v115
  terminal/path timing matrices.
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
