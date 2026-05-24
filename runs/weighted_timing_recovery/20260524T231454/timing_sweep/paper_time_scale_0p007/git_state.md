# Git State

- Branch: `exp/tase-ur10e-v82-weighted-timing-recovery`
- Commit: `8f4a94ca9729a5eb626b0e73960a1e14f9dea608`
- Dirty tree: `True`
- Status:

```text
?? runs/weighted_timing_recovery/
?? scripts/audit_weighted_timing_recovery.py
```

- Command:

```bash
/usr/bin/python3 /home/andy/reproduce-tase/scripts/evaluate_stitched_stage_a_handoff.py --output-dir /home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/timing_sweep/paper_time_scale_0p007 --stage-a-target-config /home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/configs/orientation_gate_0p11995_stage_a_target_config.yaml --source-path-csv /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p1p000mm/path/path.csv --base-z-offset-delta-m 0.001 --stage-a-duration-s 15 --paper-time-scale 0.0070000000000000001 --qdot-limit-rad-s 0.14999999999999999 --max-orientation-error-rad 0.11995 --orientation-priority-mode weighted --orientation-kp 0 --normal-axis-weight 1
```
