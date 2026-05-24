# Weighted +1.0 mm Gate Failed-Cell Execution Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v103-weighted-plus1mm-gate-execution`

## Objective

Execute the v99 planned `weighted_plus1mm_0p119_gate` offline experiment and
audit its output against the failed-cell closure criteria without changing the
claim boundary.

## Artifacts

- Executed experiment output:
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate`
- Updated weighted helper scripts:
  `scripts/audit_stage_b_priority_recovery.py`
  `scripts/audit_positive_stitched_sensitivity.py`
  `scripts/audit_weighted_timing_recovery.py`
- Updated execution-audit script:
  `scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
- New execution-audit run:
  `runs/failed_diagnostic_robustness_experiment_audit/20260525T061328`
- Updated tests:
  `tests/test_failed_diagnostic_robustness_experiment_execution.py`
  `tests/test_weighted_gate_time_matrix.py`

## Result

The exact planned `weighted_plus1mm_0p119_gate` command ran with:

```text
base_z_deltas_mm = 1.0
boundary_base_z_delta_mm = 1.0
orientation_gates_rad = 0.119, 0.11925, 0.1195, 0.11955, 0.1196, 0.1197, 0.11995
```

It did not close the failed cell at the current gate:

```text
status = executed_unresolved
closure_passed = false
current_gate_rad = 0.119
current_gate_weighted_case_count = 4
current_gate_failed_case_count = 4
min_passing_gate_time_0p0075_rad = 0.11955
min_passing_gate_time_0p01_rad = 0.1196
gate_relaxation_accepted = false
```

The v103 audit now reports:

```text
cell_count = 4
executed_cell_count = 4
closed_cell_count = 0
not_executed_cell_count = 0
all_failed_cells_closed = false
```

All v99 planned commands have now been executed and audited, but none of the
four failed cells is closed.

## Claim Boundary

V103 is offline simulation execution plus bookkeeping for the last planned
failed cell. The weighted diagnostic boundary first passes above the current
`0.119 rad` gate, and neither boundary is an accepted replacement gate. V103
does not collect live measurements, execute the read-only SOP, move the UR10e,
write configuration, zero/bias/filter the force sensor, run force control,
reconcile force-source frames, accept a replacement orientation gate, calibrate
the contact model, prove robustness, prove strict paper-equivalent feasibility,
or make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/audit_weighted_gate_time_matrix.py scripts/audit_weighted_timing_recovery.py scripts/audit_stage_b_priority_recovery.py scripts/audit_positive_stitched_sensitivity.py scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
  passed.
- `scripts/run_tests.sh tests/test_weighted_gate_time_matrix.py tests/test_failed_diagnostic_robustness_experiment_execution.py`
  passed with `6 passed in 0.96s`.
- The planned `weighted_plus1mm_0p119_gate` command created
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate`.
- `python3 scripts/audit_failed_diagnostic_robustness_experiment_execution.py --run-id 20260525T061328`
  created the v103 execution audit.
- `rg -n "&id|\*id" runs/failed_diagnostic_robustness_experiment_audit/20260525T061328/metrics.yaml runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate/metrics.yaml`
  found no YAML anchors.
- `scripts/run_tests.sh` passed with `144 passed in 6.60s`.
- `git diff --check` passed after validation.
- Branch push was verified at
  `ce266165b9ec3e47dbe6fdcce3cb0c717b8dda15`.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
All v99 planned commands have now been executed; the next offline step is to
design narrower diagnostic probes for the unresolved `+1.0 mm` rows, or use
explicitly approved read-only SOP evidence before changing contact or gate
interpretations.
