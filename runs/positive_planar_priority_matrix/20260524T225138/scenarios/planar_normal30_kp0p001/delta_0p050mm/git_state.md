# Git State

- Branch: `exp/tase-ur10e-v80-planar-priority-positive-matrix`
- Commit: `5a11a2505a2d864abbf6db8e2ded33c0c921a12b`
- Dirty tree: `True`
- Status:

```text
?? runs/positive_planar_priority_matrix/
?? scripts/audit_positive_planar_priority_matrix.py
```

- Command:

```bash
/usr/bin/python3 /home/andy/reproduce-tase/scripts/evaluate_stitched_stage_a_handoff.py --output-dir /home/andy/reproduce-tase/runs/positive_planar_priority_matrix/20260524T225138/scenarios/planar_normal30_kp0p001/delta_0p050mm --stage-a-target-config /home/andy/reproduce-tase/runs/positive_planar_priority_matrix/20260524T225138/configs/orientation_gate_0p11995_stage_a_target_config.yaml --source-path-csv /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p050mm/path/path.csv --base-z-offset-delta-m 5.0000000000000002e-05 --stage-a-duration-s 15 --paper-time-scale 0.0050000000000000001 --qdot-limit-rad-s 0.14999999999999999 --max-orientation-error-rad 0.11995 --orientation-priority-mode planar_primary --orientation-kp 0.001 --normal-axis-weight 30
```
