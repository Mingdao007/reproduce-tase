# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V108

Date: 2026-05-25

Use this after the v107 positive fast-timing weighted full-cell probe. Verify
every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v107 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v108.md`
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
- `reports/positive_fast_weighted_full_cell_report.md`
- `runs/plus1mm_unresolved_diagnostic_probe/20260525T062237/metrics.yaml`
- `runs/positive_fast_timing_e2_qdot_isolation/20260525T063019/metrics.yaml`
- `runs/positive_fast_e2_orientation_margin/20260525T063817/metrics.yaml`
- `runs/positive_fast_weighted_full_cell/20260525T064719/metrics.yaml`
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
qdot-limited cell. V105 shows qdot-limit increases alone do not recover that
E2 row at `paper_time_scale = 0.0075`. V106 shows weighted priority clears the
isolated E2 row at fixed `qdot_limit = 0.15 rad/s` and the fixed `0.12 rad`
orientation gate. V107 reruns the exact `+1.0 mm` full E1-E4 fast-timing face:
the linear-primary baseline still fails E2, while `weighted_kp0_normal1` and
`weighted_kp0_normal30` each pass `4 / 4`. V107 still does not close the
original failed cell because it does not accept `weighted` as a canonical
controller default.

Concrete v108 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. With no
approval, the clearest offline candidates are either a weighted-priority
acceptance-boundary audit before treating weighted priority as canonical, or a
`base_z_plus1mm` start-contact versus terminal-orientation split probe. Do not
move the real UR10e. Do not write TCP, payload, CoG, URCap settings, OnRobot
settings, RTDE registers, zero/bias/filter settings, or run force control
unless the user separately approves that exact SOP step.
```

## Current Verified V107 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v107-positive-fast-weighted-full-cell
```

Verified implementation commit:

```text
2e94f4bbd9ac25228c819bdc789eb6bc1f75f719
```

V107 weighted full-cell artifacts:

```text
scripts/audit_positive_fast_weighted_full_cell.py
tests/test_positive_fast_weighted_full_cell.py
runs/positive_fast_weighted_full_cell/20260525T064719
reports/positive_fast_weighted_full_cell_report.md
```

Key result:

```text
scenario_count = 3
passing_scenario_count = 2
passing_scenarios = weighted_kp0_normal1, weighted_kp0_normal30
weighted_candidate_recovered = true
all_weighted_candidates_recovered = true
original_failed_cell_closed = false
canonical_controller_change_accepted = false
```

## Recommended V108 Work

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

- For `positive_fast_timing_0p0075`, V107 shows weighted priority recovers the
  full E1-E4 face, but canonical adoption is not accepted. A next audit can
  define the acceptance boundary for promoting weighted priority into a named
  diagnostic controller profile without claiming robustness or hardware
  readiness.
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
