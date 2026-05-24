# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V100

Date: 2026-05-25

Use this after the v99 failed diagnostic robustness experiment matrix. Verify
every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v99 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v100.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/offline_completion_blockers_report.md`
- `reports/strict_feasibility_blockers_report.md`
- `reports/robustness_blockers_report.md`
- `reports/diagnostic_robustness_matrix_candidate_report.md`
- `reports/failed_diagnostic_robustness_experiment_matrix_report.md`
- `runs/diagnostic_robustness_matrix_candidate/20260525T053101/metrics.yaml`
- `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/metrics.yaml`
- `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/commands.sh`
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
robustness remains incomplete. V98 defines a single diagnostic robustness
matrix candidate with 12 cells: 7 diagnostic passes, 1 non-final diagnostic
recovery, and 4 failed cells (`base_z_plus1mm`,
`positive_fast_timing_0p0075`, `positive_orientation_gate_0p119`, and
`weighted_plus1mm_0p119_gate`). V99 converts those four failed cells into a
planned-not-executed offline experiment matrix and command script, but it does
not execute the experiments or prove robustness.

Concrete v100 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. The
clearest offline candidate is to run one v99 planned experiment command at a
time and add a separate audit that compares the output metrics against the
failed-cell closure criteria. Do not move the real UR10e. Do not write TCP,
payload, CoG, URCap settings, OnRobot settings, RTDE registers,
zero/bias/filter settings, or run force control unless the user separately
approves that exact SOP step.
```

## Current Verified V99 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v99-failed-robustness-experiment-matrix
```

Verified implementation commit:

```text
PENDING_IMPLEMENTATION_COMMIT
```

V99 failed-cell experiment-matrix artifacts:

```text
scripts/create_failed_diagnostic_robustness_experiment_matrix.py
tests/test_failed_diagnostic_robustness_experiment_matrix.py
runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909
reports/failed_diagnostic_robustness_experiment_matrix_report.md
```

Key result:

```text
status = planned_not_executed
experiment_count = 4
planned_not_executed_count = 4
source_failed_cell_ids = base_z_plus1mm, positive_fast_timing_0p0075, positive_orientation_gate_0p119, weighted_plus1mm_0p119_gate
do_not_mark_goal_complete = true
```

## Recommended V100 Work

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

If no live read-only step is approved, use the v95-v99 audits to choose
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
