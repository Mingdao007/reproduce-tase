# Positive Orientation Gate Failed-Cell Execution Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v102-positive-orientation-gate-execution`

## Objective

Execute the v99 planned `positive_orientation_gate_0p119` offline experiment
and audit its output against the failed-cell closure criteria without changing
the claim boundary.

## Artifacts

- Executed experiment output:
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119`
- Updated orientation-boundary script:
  `scripts/audit_positive_orientation_gate_boundary.py`
- Updated execution-audit script:
  `scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
- New execution-audit run:
  `runs/failed_diagnostic_robustness_experiment_audit/20260525T060119`
- Updated tests:
  `tests/test_failed_diagnostic_robustness_experiment_execution.py`
  `tests/test_positive_orientation_gate_boundary.py`

## Result

The exact planned `positive_orientation_gate_0p119` command ran with:

```text
base_z_delta_mm = 1.0
orientation_gates_rad = 0.119, 0.11925, 0.1195, 0.11975, 0.1199, 0.11995, 0.11997, 0.11998, 0.12
```

It did not close the failed cell at the current gate:

```text
status = executed_unresolved
closure_passed = false
current_gate_rad = 0.119
current_gate_stitched_recovered = false
min_passing_orientation_gate_rad = 0.11998
max_failing_orientation_gate_rad = 0.11997
max_stage_b_orientation_error_rad = 0.1199788204275829
```

The v102 audit now reports:

```text
cell_count = 4
executed_cell_count = 3
closed_cell_count = 0
not_executed_cell_count = 1
all_failed_cells_closed = false
```

The remaining v99 planned cell is still `not_executed`:

```text
weighted_plus1mm_0p119_gate
```

## Claim Boundary

V102 is offline simulation execution plus bookkeeping for one additional
planned failed cell. The boundary run first passes at `0.11998 rad`, but that
is not an accepted replacement gate. V102 does not collect live measurements,
execute the read-only SOP, move the UR10e, write configuration,
zero/bias/filter the force sensor, run force control, reconcile force-source
frames, accept a replacement orientation gate, calibrate the contact model,
prove robustness, prove strict paper-equivalent feasibility, or make a
hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/audit_positive_orientation_gate_boundary.py scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
  passed.
- `scripts/run_tests.sh tests/test_positive_orientation_gate_boundary.py tests/test_failed_diagnostic_robustness_experiment_execution.py`
  passed with `6 passed in 0.48s`.
- The planned `positive_orientation_gate_0p119` command created
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119`.
- `python3 scripts/audit_failed_diagnostic_robustness_experiment_execution.py --run-id 20260525T060119`
  created the v102 execution audit.
- `rg -n "&id|\*id" runs/failed_diagnostic_robustness_experiment_audit/20260525T060119/metrics.yaml runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119/metrics.yaml`
  found no YAML anchors.
- `scripts/run_tests.sh` passed with `142 passed in 6.06s`.
- `git diff --check` passed after validation.
- Branch push was verified at
  `5f7b30e7009296ca8153a020bd1475fec0b6dabd`.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
The next offline step is either to run the remaining
`weighted_plus1mm_0p119_gate` planned command or design narrower diagnostic
probes for the unresolved `+1.0 mm` rows.
