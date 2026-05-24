# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V105

Date: 2026-05-25

Use this after the v104 `+1.0 mm` unresolved diagnostic probe. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v104 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v105.md`
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
- `reports/positive_fast_timing_failed_cell_execution_report.md`
- `reports/positive_orientation_gate_failed_cell_execution_report.md`
- `reports/weighted_plus1mm_gate_failed_cell_execution_report.md`
- `reports/plus1mm_unresolved_diagnostic_probe_report.md`
- `runs/failed_diagnostic_robustness_experiment_audit/20260525T061328/metrics.yaml`
- `runs/plus1mm_unresolved_diagnostic_probe/20260525T062237/metrics.yaml`
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
simulation only. V95 classifies strict paper-equivalent full staged
feasibility and robustness as non-final offline-actionable items, while
approved read-only calibration evidence, calibrated contact geometry,
orientation-gate acceptance, and hardware readiness remain blocked on explicit
approval/evidence. V100-v103 execute all four v99 planned failed-cell
commands; all four remain `executed_unresolved`. V104 classifies the remaining
`+1.0 mm` signatures: only `positive_fast_timing_0p0075` still has a
qdot-saturation blocker; `base_z_plus1mm`,
`positive_orientation_gate_0p119`, and `weighted_plus1mm_0p119_gate` remain
orientation/contact-definition blocked under the current `0.119 rad` gate or
unrecovered start/path conditions.

Concrete v105 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. Since all
v99 planned commands have now been executed and v104 classified the unresolved
signatures, the clearest offline candidates are either a narrower
`base_z_plus1mm` start-contact versus terminal-orientation split probe or a
focused `positive_fast_timing_0p0075` E2 qdot/usage isolation probe. Do not
move the real UR10e. Do not write TCP, payload, CoG, URCap settings, OnRobot
settings, RTDE registers, zero/bias/filter settings, or run force control
unless the user separately approves that exact SOP step.
```

## Current Verified V104 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v104-plus1mm-unresolved-probe
```

Verified implementation commit:

```text
TBD_AFTER_V104_IMPLEMENTATION_COMMIT
```

V104 unresolved diagnostic probe artifacts:

```text
scripts/audit_plus1mm_unresolved_diagnostic_probe.py
tests/test_plus1mm_unresolved_diagnostic_probe.py
runs/plus1mm_unresolved_diagnostic_probe/20260525T062237
reports/plus1mm_unresolved_diagnostic_probe_report.md
```

Key result:

```text
planned_failed_cell_count = 4
executed_cell_count = 4
closed_cell_count = 0
not_executed_cell_count = 0
unresolved_cell_count = 4
qdot_limited_cell_ids = positive_fast_timing_0p0075
probe_closes_failed_cells = false
do_not_mark_goal_complete = true
```

## Recommended V105 Work

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

If no live read-only step is approved, continue only non-final offline probes.
Use v104 to avoid broad repetition:

- `base_z_plus1mm`: split start-contact recovery from terminal-orientation
  margin and path-geometry recovery.
- `positive_fast_timing_0p0075`: isolate E2 qdot saturation and tail qdot
  utilization from the remaining orientation excess.
- `positive_orientation_gate_0p119` and `weighted_plus1mm_0p119_gate`: do not
  accept diagnostic gate relaxations without calibrated geometry or an
  approved orientation-gate decision.

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
