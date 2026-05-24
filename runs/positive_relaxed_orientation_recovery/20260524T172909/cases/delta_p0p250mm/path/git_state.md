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
/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_stage_a_contact_path.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml --setup-metrics runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml --stage-a-target-config /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/relaxed_stage_a_target_config.yaml --output-dir /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p250mm/path --initial-q=0,-0.078000000000000014,0.1215,-0.050000000000000003,0,0 --initial-label delta_p0p250mm_perturbed_start_contact --target-q=-7.4776577586746085e-09,-0.021399661058702602,-0.00043282523430505221,0.00025142197988962343,2.0296168521061363e-10,0.10491494689322009 --target-label delta_p0p250mm_perturbed_terminal_target --base-z-offset-delta-m=0.00025 --knot-count 128 --max-nfev 200 --qdot-limit-rad-s 0.15 --continuity-weight 0.02 --linear-posture-weight 0.002
```
