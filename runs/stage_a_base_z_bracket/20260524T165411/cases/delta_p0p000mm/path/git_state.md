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
/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_stage_a_contact_path.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml --setup-metrics runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml --stage-a-target-config configs/ur10e_adapted_stage_a_target.yaml --output-dir /home/andy/reproduce-tase/runs/stage_a_base_z_bracket/20260524T165411/cases/delta_p0p000mm/path --initial-q=0,-0.10000000000000001,0.14999999999999999,-0.050000000000000003,0,0 --initial-label delta_p0p000mm_perturbed_start_contact --target-q=-1.1745579135426345e-08,-0.02440152369247043,-0.00048297839388595083,0.0002982283198967393,2.405416739224147e-10,0.12671314216940235 --target-label delta_p0p000mm_perturbed_terminal_target --base-z-offset-delta-m=0.0 --knot-count 128 --max-nfev 200 --qdot-limit-rad-s 0.15 --continuity-weight 0.02 --linear-posture-weight 0.002
```
