# Git State

- Branch: `exp/tase-ur10e-v105-positive-fast-e2-qdot-isolation`
- Commit: `712df389363bdbeeab9c3d1383f62cd03db8aa78`
- Dirty tree: `True`
- Status:

```text
M scripts/audit_positive_stage_b_e2_margin.py
?? runs/positive_fast_timing_e2_qdot_isolation/
?? tests/test_positive_stage_b_e2_margin.py
```

- Command:

```bash
/usr/bin/python3 /home/andy/reproduce-tase/scripts/evaluate_stitched_stage_a_handoff.py --output-dir runs/positive_fast_timing_e2_qdot_isolation/20260525T063019/cases/delta_p1p000mm/timing_scale_0p0075 --stage-a-target-config /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/relaxed_stage_a_target_config.yaml --source-path-csv /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p1p000mm/path/path.csv --base-z-offset-delta-m 0.001 --stage-a-duration-s 15 --paper-time-scale 0.0074999999999999997 --qdot-limit-rad-s 0.14999999999999999 --max-orientation-error-rad 0.12 --trajectories e2-figure-eight
```
