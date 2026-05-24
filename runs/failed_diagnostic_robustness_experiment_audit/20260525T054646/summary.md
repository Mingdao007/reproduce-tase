# Failed Diagnostic Robustness Experiment Execution Audit

Run root: `/home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_audit/20260525T054646`

- Status: `completed`
- Executed cell count: `1`
- Closed cell count: `0`
- Not-executed cell count: `3`
- All failed cells closed: `False`

| cell | status | closure passed | metrics |
| --- | --- | --- | --- |
| `base_z_plus1mm` | `executed_unresolved` | `False` | `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm/metrics.yaml` |
| `positive_fast_timing_0p0075` | `not_executed` | `False` | `None` |
| `positive_orientation_gate_0p119` | `not_executed` | `False` | `None` |
| `weighted_plus1mm_0p119_gate` | `not_executed` | `False` | `None` |

## Claim Boundary

- This audit compares offline experiment output to the v99 failed-cell closure criteria.
- It does not prove robustness, accept a gate, calibrate contact geometry,
  authorize hardware, or mark the goal complete.
