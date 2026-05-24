# Positive Fast-Timing Failed-Cell Execution Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v101-positive-fast-timing-execution`

## Objective

Execute the v99 planned `positive_fast_timing_0p0075` offline experiment and
audit its output against the failed-cell closure criteria without changing the
claim boundary.

## Artifacts

- Executed experiment output:
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075`
- Updated execution-audit script:
  `scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
- New execution-audit run:
  `runs/failed_diagnostic_robustness_experiment_audit/20260525T055322`
- Updated tests:
  `tests/test_failed_diagnostic_robustness_experiment_execution.py`

## Result

The exact planned `positive_fast_timing_0p0075` command ran with:

```text
base_z_deltas_mm = 1.0
scenario = paper_time_scale_0p0075
paper_time_scale = 0.0075
```

It did not close the failed cell:

```text
status = executed_unresolved
closure_passed = false
stage_a_passed = true
stitched_passed = false
handoff_pass_count = 3 / 4
stage_b_failed_row = e2-figure-eight
failed_criteria = qdot_saturation_fraction, tail_max_qdot_utilization, max_orientation_error_rad
stage_b_max_qdot_saturation_fraction = 0.999
stage_b_max_tail_qdot_utilization = 1.0
stage_b_max_orientation_error_rad = 0.12020305872871904
```

The v101 audit now reports:

```text
cell_count = 4
executed_cell_count = 2
closed_cell_count = 0
not_executed_cell_count = 2
all_failed_cells_closed = false
```

The other two v99 planned cells remain `not_executed`:

```text
positive_orientation_gate_0p119
weighted_plus1mm_0p119_gate
```

## Claim Boundary

V101 is offline simulation execution plus bookkeeping for one additional
planned failed cell. It does not collect live measurements, execute the
read-only SOP, move the UR10e, write configuration, zero/bias/filter the force
sensor, run force control, reconcile force-source frames, accept a replacement
orientation gate, calibrate the contact model, prove robustness, prove strict
paper-equivalent feasibility, or make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
  passed.
- `scripts/run_tests.sh tests/test_failed_diagnostic_robustness_experiment_execution.py`
  passed with `3 passed in 0.20s`.
- The planned `positive_fast_timing_0p0075` command created
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075`.
- `python3 scripts/audit_failed_diagnostic_robustness_experiment_execution.py --run-id 20260525T055322`
  created the v101 execution audit.
- `rg -n "&id|\*id" runs/failed_diagnostic_robustness_experiment_audit/20260525T055322/metrics.yaml runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075/metrics.yaml`
  found no YAML anchors.
- `scripts/run_tests.sh` passed with `139 passed in 5.89s`.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
The next offline step is either to run one of the two remaining planned v99
commands or design narrower diagnostic probes for the unresolved `+1.0 mm`
rows.
