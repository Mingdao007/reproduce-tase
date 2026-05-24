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
/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_stage_a_contact_path.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml --setup-metrics runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml --stage-a-target-config /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/relaxed_stage_a_target_config.yaml --output-dir /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p750mm/path --initial-q=0,-0.066500000000000004,0.11049999999999999,-0.050000000000000003,0,0 --initial-label delta_p0p750mm_perturbed_start_contact --target-q=3.1858879625468529e-08,-0.016163143450381771,-0.00038596476219299994,0.000176506211527681,-2.0597171121503152e-10,0.080883879871815986 --target-label delta_p0p750mm_perturbed_terminal_target --base-z-offset-delta-m=0.00075 --knot-count 128 --max-nfev 200 --qdot-limit-rad-s 0.15 --continuity-weight 0.02 --linear-posture-weight 0.002
```
