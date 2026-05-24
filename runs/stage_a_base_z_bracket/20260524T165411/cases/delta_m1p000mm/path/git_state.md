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
/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_stage_a_contact_path.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml --setup-metrics runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml --stage-a-target-config configs/ur10e_adapted_stage_a_target.yaml --output-dir /home/andy/reproduce-tase/runs/stage_a_base_z_bracket/20260524T165411/cases/delta_m1p000mm/path --initial-q=-0.0038299507948583301,-0.12042642914233553,0.16239548809635068,-0.043896998239112778,0.00012907750842018877,0.016521133761834318 --initial-label delta_m1p000mm_perturbed_start_contact --target-q=-7.6910068223168909e-09,-0.032733515989918971,-0.00054243037686819333,0.00041347733758968368,1.9081212402948586e-10,0.16021618155854966 --target-label delta_m1p000mm_perturbed_terminal_target --base-z-offset-delta-m=-0.001 --knot-count 128 --max-nfev 200 --qdot-limit-rad-s 0.15 --continuity-weight 0.02 --linear-posture-weight 0.002
```
