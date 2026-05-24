# Git State

- Branch: `exp/tase-ur10e-v102-positive-orientation-gate-execution`
- Commit: `409ca56411c2a6478a317dcfe7d16d64929c7b8f`
- Dirty tree: `True`
- Status:

```text
M scripts/audit_positive_orientation_gate_boundary.py
?? runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119/
?? tests/test_positive_orientation_gate_boundary.py
```

- Command:

```bash
/usr/bin/python3 /home/andy/reproduce-tase/scripts/evaluate_stitched_stage_a_handoff.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119/cases/orientation_gate_0p11975 --stage-a-target-config /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119/configs/orientation_gate_0p11975_stage_a_target_config.yaml --source-path-csv /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p1p000mm/path/path.csv --base-z-offset-delta-m 0.001 --stage-a-duration-s 15 --paper-time-scale 0.0050000000000000001 --qdot-limit-rad-s 0.14999999999999999 --max-orientation-error-rad 0.11975
```
