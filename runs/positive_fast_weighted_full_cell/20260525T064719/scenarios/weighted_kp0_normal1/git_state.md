# Git State

- Branch: `exp/tase-ur10e-v107-positive-fast-weighted-full-cell`
- Commit: `7fb1f482c23de0ba02131f668ea6374fbdbe9ac0`
- Dirty tree: `True`
- Status:

```text
?? runs/positive_fast_weighted_full_cell/
?? scripts/audit_positive_fast_weighted_full_cell.py
?? tests/test_positive_fast_weighted_full_cell.py
```

- Command:

```bash
/usr/bin/python3 /home/andy/reproduce-tase/scripts/evaluate_stitched_stage_a_handoff.py --output-dir runs/positive_fast_weighted_full_cell/20260525T064719/scenarios/weighted_kp0_normal1 --stage-a-target-config /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/relaxed_stage_a_target_config.yaml --source-path-csv /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p1p000mm/path/path.csv --base-z-offset-delta-m 0.001 --stage-a-duration-s 15 --paper-time-scale 0.0074999999999999997 --qdot-limit-rad-s 0.14999999999999999 --max-orientation-error-rad 0.12 --orientation-priority-mode weighted --orientation-kp 0 --normal-axis-weight 1 --trajectories e1-cycloid,e2-figure-eight,e3-circle,e4-cardioid
```
