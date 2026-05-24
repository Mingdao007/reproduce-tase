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
/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_stage_a_contact_path.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml --setup-metrics runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml --stage-a-target-config configs/ur10e_adapted_stage_a_target.yaml --output-dir /home/andy/reproduce-tase/runs/stage_a_base_z_bracket/20260524T165411/cases/delta_m0p500mm/path --initial-q=0.0049469284713406182,-0.11893277014464315,0.16270755989239577,-0.041368273216526183,-9.664799752078914e-05,0.02159401929203307 --initial-label delta_m0p500mm_perturbed_start_contact --target-q=-1.8668857768558399e-08,-0.028472628565137964,-0.00049972734012209774,0.00035240521388580482,1.4410062710253726e-10,0.13899435081826075 --target-label delta_m0p500mm_perturbed_terminal_target --base-z-offset-delta-m=-0.0005 --knot-count 128 --max-nfev 200 --qdot-limit-rad-s 0.15 --continuity-weight 0.02 --linear-posture-weight 0.002
```
