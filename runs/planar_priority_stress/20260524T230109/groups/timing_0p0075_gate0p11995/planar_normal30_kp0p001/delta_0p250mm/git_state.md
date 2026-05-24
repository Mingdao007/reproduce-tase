# Git State

- Branch: `exp/tase-ur10e-v81-planar-priority-stress`
- Commit: `44a8c70c61e07dd5f3e48beb55fc0043032adca5`
- Dirty tree: `True`
- Status:

```text
?? runs/planar_priority_stress/
?? scripts/audit_planar_priority_stress.py
```

- Command:

```bash
/usr/bin/python3 /home/andy/reproduce-tase/scripts/evaluate_stitched_stage_a_handoff.py --output-dir /home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/timing_0p0075_gate0p11995/planar_normal30_kp0p001/delta_0p250mm --stage-a-target-config /home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/configs/orientation_gate_0p11995_stage_a_target_config.yaml --source-path-csv /home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p250mm/path/path.csv --base-z-offset-delta-m 0.00025000000000000001 --stage-a-duration-s 15 --paper-time-scale 0.0074999999999999997 --qdot-limit-rad-s 0.14999999999999999 --max-orientation-error-rad 0.11995 --orientation-priority-mode planar_primary --orientation-kp 0.001 --normal-axis-weight 30
```
