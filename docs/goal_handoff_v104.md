# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V104

Date: 2026-05-25

Use this after the v103 weighted `+1.0 mm` gate failed-cell execution audit.
Verify every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v103 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v104.md`
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
- `runs/diagnostic_robustness_matrix_candidate/20260525T053101/metrics.yaml`
- `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/metrics.yaml`
- `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/commands.sh`
- `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm/metrics.yaml`
- `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075/metrics.yaml`
- `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119/metrics.yaml`
- `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate/metrics.yaml`
- `runs/failed_diagnostic_robustness_experiment_audit/20260525T061328/metrics.yaml`
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
approval/evidence. V96 confirms strict setup remains incomplete. V97 confirms
robustness remains incomplete. V98 defines a diagnostic robustness matrix
candidate with 12 cells: 7 diagnostic passes, 1 non-final diagnostic recovery,
and 4 failed cells. V99 converts those failed cells into a planned offline
experiment matrix. V100 executes `base_z_plus1mm`, V101 executes
`positive_fast_timing_0p0075`, V102 executes `positive_orientation_gate_0p119`,
and V103 executes `weighted_plus1mm_0p119_gate`; all four planned failed cells
remain `executed_unresolved`. The current execution audit has
`executed_cell_count = 4`, `closed_cell_count = 0`,
`not_executed_cell_count = 0`, and `all_failed_cells_closed = false`.

Concrete v104 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. Since all
v99 planned commands have now been executed, the clearest offline candidates
are narrower diagnostic probes for the unresolved `+1.0 mm` rows. Do not move
the real UR10e. Do not write TCP, payload, CoG, URCap settings, OnRobot
settings, RTDE registers, zero/bias/filter settings, or run force control
unless the user separately approves that exact SOP step.
```

## Current Verified V103 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v103-weighted-plus1mm-gate-execution
```

Verified implementation commit:

```text
PENDING_IMPLEMENTATION_COMMIT
```

V103 weighted gate execution artifacts:

```text
scripts/audit_stage_b_priority_recovery.py
scripts/audit_positive_stitched_sensitivity.py
scripts/audit_weighted_timing_recovery.py
scripts/audit_failed_diagnostic_robustness_experiment_execution.py
tests/test_weighted_gate_time_matrix.py
tests/test_failed_diagnostic_robustness_experiment_execution.py
runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate
runs/failed_diagnostic_robustness_experiment_audit/20260525T061328
reports/weighted_plus1mm_gate_failed_cell_execution_report.md
```

Key result:

```text
weighted_plus1mm_0p119_gate status = executed_unresolved
current_gate_rad = 0.119
min_passing_gate_time_0p0075_rad = 0.11955
min_passing_gate_time_0p01_rad = 0.1196
closed_cell_count = 0
not_executed_cell_count = 0
all_failed_cells_closed = false
do_not_mark_goal_complete = true
```

## Recommended V104 Work

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

If no live read-only step is approved, use the v95-v103 audits to choose
non-final offline work only. Do not claim completion from offline work unless
every completion blocker in the v95 audit is actually closed by concrete
evidence.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zero/bias/filter, OnRobot
  configuration, or RTDE registers unless the user approves a separate exact
  SOP step.
- Do not use OnRobot direct TCP DAQ as control truth until the force-source
  discrepancy is resolved.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user.
