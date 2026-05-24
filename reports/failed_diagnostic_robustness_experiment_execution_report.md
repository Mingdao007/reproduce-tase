# Failed Diagnostic Robustness Experiment Execution Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v100-base-z-failed-cell-execution`

## Objective

Execute one planned v99 offline experiment command and audit its output against
the failed-cell closure criteria without changing the claim boundary.

The executed cell is:

```text
base_z_plus1mm
```

## Artifacts

- Executed experiment output:
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm`
- New execution-audit script:
  `scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
- New execution-audit run:
  `runs/failed_diagnostic_robustness_experiment_audit/20260525T054646`
- New tests:
  `tests/test_failed_diagnostic_robustness_experiment_execution.py`

## Result

The exact planned `base_z_plus1mm` command ran with:

```text
base_z_deltas_mm = 1.0
stage_a_durations_s = 15.0, 16.0, 18.0
```

It did not close the failed cell:

```text
status = executed_unresolved
closure_passed = false
start_pass_count = 0
terminal_pass_count = 0
path_geometry_pass_count = 0
duration_recovered_count = 0
terminal_orientation_error_rad = 0.11948560786548146
```

The v100 audit reports:

```text
cell_count = 4
executed_cell_count = 1
closed_cell_count = 0
not_executed_cell_count = 3
all_failed_cells_closed = false
```

The other three v99 planned cells remain `not_executed`:

```text
positive_fast_timing_0p0075
positive_orientation_gate_0p119
weighted_plus1mm_0p119_gate
```

## Claim Boundary

V100 is offline simulation execution plus bookkeeping for one planned failed
cell. It does not collect live measurements, execute the read-only SOP, move
the UR10e, write configuration, zero/bias/filter the force sensor, run force
control, reconcile force-source frames, accept a replacement orientation gate,
calibrate the contact model, prove robustness, prove strict paper-equivalent
feasibility, or make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
  passed.
- `scripts/run_tests.sh tests/test_failed_diagnostic_robustness_experiment_execution.py`
  passed with `2 passed in 0.12s`.
- The planned `base_z_plus1mm` command created
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm`.
- `python3 scripts/audit_failed_diagnostic_robustness_experiment_execution.py --run-id 20260525T054646`
  created the v100 execution audit.
- `rg -n "&id|\*id" runs/failed_diagnostic_robustness_experiment_audit/20260525T054646/metrics.yaml runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm/metrics.yaml`
  found no YAML anchors.
- `scripts/run_tests.sh` passed with `138 passed in 5.87s`.
- `git diff --check` passed after validation.
- Branch push was verified at
  `ce48bcef63a1fa5f3c3969530774cfe59c6275b9`.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
The next offline step is either to run one of the remaining planned v99
commands or design a narrower diagnostic probe for the still-unresolved
`base_z_plus1mm` start-contact and terminal-orientation failure.
