# Git State

- Branch: `exp/tase-ur10e-v103-weighted-plus1mm-gate-execution`
- Commit: `9c563d7ac5aec215e02a88dfe3c99faaaa2c018d`
- Dirty tree: `True`
- Status:

```text
M scripts/audit_failed_diagnostic_robustness_experiment_execution.py
 M scripts/audit_positive_stitched_sensitivity.py
 M scripts/audit_stage_b_priority_recovery.py
 M scripts/audit_weighted_timing_recovery.py
 M tests/test_failed_diagnostic_robustness_experiment_execution.py
?? runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate/
?? tests/test_weighted_gate_time_matrix.py
```

- Command:

```bash
/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_weighted_gate_time_matrix.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate --base-z-deltas-mm 1.0 --boundary-base-z-delta-mm 1.0 --orientation-gates 0.119,0.11925,0.1195,0.11955,0.1196,0.1197,0.11995
```
