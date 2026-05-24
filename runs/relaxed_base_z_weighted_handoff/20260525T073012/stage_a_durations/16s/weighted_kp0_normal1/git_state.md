# Git State

- Branch: `exp/tase-ur10e-v109-relaxed-base-z-weighted-handoff`
- Commit: `9dde7737ea5043910f394ece14d63ba4d7e6dc8b`
- Dirty tree: `True`
- Status:

```text
?? runs/relaxed_base_z_weighted_handoff/
?? scripts/audit_relaxed_base_z_weighted_handoff.py
?? tests/test_relaxed_base_z_weighted_handoff.py
```

- Command:

```bash
/usr/bin/python3 /home/andy/reproduce-tase/scripts/evaluate_stitched_stage_a_handoff.py --output-dir runs/relaxed_base_z_weighted_handoff/20260525T073012/stage_a_durations/16s/weighted_kp0_normal1 --stage-a-target-config /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/relaxed_stage_a_target_config.yaml --source-path-csv /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p1p000mm/path/path.csv --base-z-offset-delta-m 0.001 --stage-a-duration-s 16 --paper-time-scale 0.01 --qdot-limit-rad-s 0.14999999999999999 --max-orientation-error-rad 0.12 --orientation-priority-mode weighted --orientation-kp 0 --normal-axis-weight 1 --trajectories e1-cycloid,e2-figure-eight,e3-circle,e4-cardioid
```
