# Git State

- Branch: `exp/tase-ur10e-v83-weighted-gate-time-matrix`
- Commit: `b72ecec06468cf527889d176fc553be764206307`
- Dirty tree: `True`
- Status:

```text
?? runs/weighted_gate_time_matrix/
?? scripts/audit_weighted_gate_time_matrix.py
```

- Command:

```bash
/usr/bin/python3 /home/andy/reproduce-tase/scripts/evaluate_stitched_stage_a_handoff.py --output-dir /home/andy/reproduce-tase/runs/weighted_gate_time_matrix/20260524T232637/gate_boundary/paper_time_scale_0p0075/orientation_gate_0p11995 --stage-a-target-config /home/andy/reproduce-tase/runs/weighted_gate_time_matrix/20260524T232637/configs/orientation_gate_0p11995_stage_a_target_config.yaml --source-path-csv /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p1p000mm/path/path.csv --base-z-offset-delta-m 0.001 --stage-a-duration-s 15 --paper-time-scale 0.0074999999999999997 --qdot-limit-rad-s 0.14999999999999999 --max-orientation-error-rad 0.11995 --orientation-priority-mode weighted --orientation-kp 0 --normal-axis-weight 1
```
