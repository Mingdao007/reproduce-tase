# Git State

- Branch: `exp/tase-ur10e-v78-stage-b-orientation-kp-probe`
- Commit: `31e3dfdcced6807232931d2e94e7a6383befac7a`
- Dirty tree: `True`
- Status:

```text
?? runs/stage_b_orientation_kp_probe/
?? scripts/audit_stage_b_orientation_kp_probe.py
```

- Command:

```bash
/usr/bin/python3 /home/andy/reproduce-tase/scripts/evaluate_stitched_stage_a_handoff.py --output-dir /home/andy/reproduce-tase/runs/stage_b_orientation_kp_probe/20260524T222953/cases/qdot_0p16/kp_0p002 --stage-a-target-config /home/andy/reproduce-tase/runs/stage_b_orientation_kp_probe/20260524T222953/configs/orientation_gate_0p11995_stage_a_target_config.yaml --source-path-csv /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p1p000mm/path/path.csv --base-z-offset-delta-m 0.001 --stage-a-duration-s 15 --paper-time-scale 0.0050000000000000001 --qdot-limit-rad-s 0.16 --orientation-kp 0.002 --max-orientation-error-rad 0.11995 --trajectories e2-figure-eight
```
