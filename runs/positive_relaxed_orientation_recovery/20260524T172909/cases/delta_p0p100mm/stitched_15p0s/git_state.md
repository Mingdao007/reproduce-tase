# Git State

- Branch: `exp/tase-ur10e-v70-positive-relaxed-orientation-recovery`
- Commit: `d8232b91a3c6e2a00c7e5a8432928f5ba3fc6d43`
- Dirty tree: `True`
- Status:

```text
?? runs/positive_relaxed_orientation_recovery/
?? scripts/audit_positive_relaxed_orientation_recovery.py
```

- Command:

```bash
/usr/bin/python3 /home/andy/reproduce-tase/scripts/evaluate_stitched_stage_a_handoff.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml --setup-metrics runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml --stage-a-target-config /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/relaxed_stage_a_target_config.yaml --source-path-csv /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p100mm/path/path.csv --output-dir /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p100mm/stitched_15p0s --base-z-offset-delta-m 0.0001 --stage-a-duration-s 15.0 --stage-b-duration-s 2.0 --target-force-N 5.0 --force-gain 0.0001 --r 0.5 --qdot-limit-rad-s 0.15 --planar-kp 0.5 --paper-time-scale 0.01 --orientation-kp 0.0 --max-orientation-error-rad 0.12 --max-angular-slack-rad-s 0.03
```
