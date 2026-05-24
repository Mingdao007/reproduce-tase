# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V115

Date: 2026-05-25

Use this after the v114 strict command-limited Stage A probe. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v114 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v115.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/offline_completion_blockers_report.md`
- `reports/strict_feasibility_blockers_report.md`
- `reports/remaining_blocker_prioritization_report.md`
- `reports/strict_feasibility_policy_probe_report.md`
- `reports/strict_command_limited_stage_a_report.md`
- `runs/remaining_blocker_prioritization/20260525T072557/metrics.yaml`
- `runs/strict_feasibility_policy_probe/20260525T073519/metrics.yaml`
- `runs/strict_command_limited_stage_a/20260525T074557/metrics.yaml`
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
`0 / 8`. V114 changes Stage A command generation before allocation by lowering
force gain, capping force-normal angular commands, and extending durations; it
still reports strict setup-chain pass `0 / 4`, planned setup-then-trajectory
pass `0 / 4`, final x/y failures `4 / 4`, setup qdot saturation failures
`4 / 4`, setup tail qdot utilization failures `4 / 4`, strict
paper-equivalent feasibility `false`, and `do_not_mark_goal_complete = true`.

Concrete v115 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. With no
approval, the next strict-feasibility probe should stop treating Stage A as a
command-limited instantaneous velocity problem and instead test an explicit
path or terminal constraint formulation that can hold x/y while restoring
force-normal orientation without setup qdot saturation. Do not move the real
UR10e. Do not write TCP, payload, CoG, URCap settings, OnRobot settings, RTDE
registers, zero/bias/filter settings, or run force control unless the user
separately approves that exact SOP step.
```

## Current Verified V114 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v114-strict-command-limited-stage-a
```

Verified implementation commit:

```text
aaa42097f6778cc0b2c8617c9ffc21f57b5fbfb4
```

V114 strict command-limited Stage A artifacts:

```text
scripts/audit_strict_command_limited_stage_a.py
tests/test_strict_command_limited_stage_a.py
runs/strict_command_limited_stage_a/20260525T074557
reports/strict_command_limited_stage_a_report.md
```

Key result:

```text
strict_setup_chain_pass_count = 0 / 4
trajectory_feasibility_pass_count = 2 / 4
planned_setup_then_trajectory_pass_count = 0 / 4
final_tangential_position_error_m failures = 4 / 4
setup_max_qdot_saturation_fraction failures = 4 / 4
setup_max_tail_qdot_utilization failures = 4 / 4
strict_paper_equivalent_feasibility = false
do_not_mark_goal_complete = true
```

## Recommended V115 Work

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

- Use v114 as the latest strict Stage A command-limiting boundary.
- Treat `approved_read_only_calibration_evidence` as the top overall blocker.
- Treat strict feasibility as the highest-priority offline-actionable blocker.
- Avoid repeating v113 instantaneous priority and v114 command-limiting
  matrices.
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
