# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V107

Date: 2026-05-25

Use this after the v106 positive fast-timing E2 orientation-margin probe.
Verify every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v106 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v107.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/offline_completion_blockers_report.md`
- `reports/strict_feasibility_blockers_report.md`
- `reports/robustness_blockers_report.md`
- `reports/diagnostic_robustness_matrix_candidate_report.md`
- `reports/failed_diagnostic_robustness_experiment_matrix_report.md`
- `reports/failed_diagnostic_robustness_experiment_execution_report.md`
- `reports/weighted_plus1mm_gate_failed_cell_execution_report.md`
- `reports/plus1mm_unresolved_diagnostic_probe_report.md`
- `reports/positive_fast_timing_e2_qdot_isolation_report.md`
- `reports/positive_fast_e2_orientation_margin_report.md`
- `runs/plus1mm_unresolved_diagnostic_probe/20260525T062237/metrics.yaml`
- `runs/positive_fast_timing_e2_qdot_isolation/20260525T063019/metrics.yaml`
- `runs/positive_fast_e2_orientation_margin/20260525T063817/metrics.yaml`
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
simulation only. V100-v103 execute all four v99 planned failed-cell commands;
all four remain `executed_unresolved`. V104 classifies the remaining
`+1.0 mm` signatures and identifies `positive_fast_timing_0p0075` as the only
qdot-limited cell. V105 isolates that E2 row: at
`paper_time_scale = 0.0075`, raising the qdot limit through `0.3 rad/s` clears
qdot saturation but still fails orientation, while slowing E2 first passes at
`paper_time_scale = 0.0052` under the run-local `0.12 rad` gate. V106 probes
E2-only Stage B priority formulations at the same fixed timing, qdot limit,
and orientation gate. The weighted rows pass E2 with
`max_orientation_error_rad = 0.11954627160547111`, but this does not rerun the
full E1-E4 failed-cell audit, does not make `weighted` canonical, and does not
close the failed cell.

Concrete v107 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. With no
approval, the clearest offline candidates are either a full E1-E4 rerun of the
`positive_fast_timing_0p0075` failed-cell audit with the weighted priority
formulation while keeping the `0.12 rad` gate fixed, or a `base_z_plus1mm`
start-contact versus terminal-orientation split probe. Do not move the real
UR10e. Do not write TCP, payload, CoG, URCap settings, OnRobot settings, RTDE
registers, zero/bias/filter settings, or run force control unless the user
separately approves that exact SOP step.
```

## Current Verified V106 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v106-positive-fast-e2-orientation-margin
```

Verified implementation commit:

```text
716ecde74a428c15ce17445018ca7028b1db9527
```

V106 E2 orientation-margin artifacts:

```text
scripts/audit_positive_fast_e2_orientation_margin.py
tests/test_positive_fast_e2_orientation_margin.py
runs/positive_fast_e2_orientation_margin/20260525T063817
reports/positive_fast_e2_orientation_margin_report.md
```

Key result:

```text
scenario_count = 6
e2_pass_count = 2 / 6
passing_scenarios = weighted_kp0_normal1, weighted_kp0_normal30
best_orientation_scenario = weighted_kp0_normal1
min_orientation_error_rad = 0.11954627160547111
orientation_gate_rad = 0.12
failed_cell_closed = false
canonical_controller_change = false
```

## Recommended V107 Work

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

- For `positive_fast_timing_0p0075`, V106 suggests weighted priority can clear
  the isolated E2 row at fixed `0.12 rad`, but it has not been tested across
  the full E1-E4 failed-cell audit.
- A next offline probe can rerun the failed-cell audit with weighted E1-E4
  priority while keeping `paper_time_scale = 0.0075`, `qdot_limit = 0.15
  rad/s`, and the `0.12 rad` orientation gate fixed.
- The other clean offline target remains `base_z_plus1mm`, splitting
  start-contact recovery from terminal-orientation/path recovery.

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
