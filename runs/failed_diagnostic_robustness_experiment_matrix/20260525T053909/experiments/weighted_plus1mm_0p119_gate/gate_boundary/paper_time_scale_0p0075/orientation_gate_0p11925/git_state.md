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
/usr/bin/python3 /home/andy/reproduce-tase/scripts/evaluate_stitched_stage_a_handoff.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate/gate_boundary/paper_time_scale_0p0075/orientation_gate_0p11925 --stage-a-target-config /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate/configs/orientation_gate_0p11925_stage_a_target_config.yaml --source-path-csv /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p1p000mm/path/path.csv --base-z-offset-delta-m 0.001 --stage-a-duration-s 15 --paper-time-scale 0.0074999999999999997 --qdot-limit-rad-s 0.14999999999999999 --max-orientation-error-rad 0.11924999999999999 --orientation-priority-mode weighted --orientation-kp 0 --normal-axis-weight 1
```
