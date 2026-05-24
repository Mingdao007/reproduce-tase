# Git State

- Branch: `exp/tase-ur10e-v67-base-z-bracket`
- Commit: `3f280e2d35ea2d87abc9769a81c1ff0cf377415e`
- Dirty tree: `True`
- Status:

```text
M scripts/audit_stage_a_base_z_recovery.py
 M src/tase_repro/base_z_recovery.py
 M src/tase_repro/setup_terminal_ik.py
 M tests/test_base_z_recovery.py
 M tests/test_setup_terminal_ik.py
?? runs/stage_a_base_z_bracket/
?? scripts/audit_stage_a_base_z_bracket.py
```

- Command:

```bash
/usr/bin/python3 /home/andy/reproduce-tase/scripts/evaluate_stitched_stage_a_handoff.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml --setup-metrics runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml --stage-a-target-config configs/ur10e_adapted_stage_a_target.yaml --source-path-csv /home/andy/reproduce-tase/runs/stage_a_base_z_bracket/20260524T165411/cases/delta_p0p000mm/path/path.csv --output-dir /home/andy/reproduce-tase/runs/stage_a_base_z_bracket/20260524T165411/cases/delta_p0p000mm/stitched_16p0s --base-z-offset-delta-m 0.0 --stage-a-duration-s 16.0 --stage-b-duration-s 2.0 --target-force-N 5.0 --force-gain 0.0001 --r 0.5 --qdot-limit-rad-s 0.15 --planar-kp 0.5 --paper-time-scale 0.01 --orientation-kp 0.0 --max-orientation-error-rad 0.08 --max-angular-slack-rad-s 0.03
```
