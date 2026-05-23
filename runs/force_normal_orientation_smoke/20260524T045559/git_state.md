# Git State

- Branch: `exp/tase-ur10e-v21-force-normal-orientation`
- Commit: `e1063f53aebb4e7904d1f0c4cc19725dc3bb0224`
- Dirty tree: `True`
- Status:

```text
M scripts/run_paper_trajectory_force_motion.py
 M scripts/run_posture_feasibility_sweep.py
 M scripts/run_timing_feasibility_sweep.py
 M src/tase_repro/contact_ladder.py
 M src/tase_repro/force_feedback.py
 M tests/test_force_motion.py
?? runs/force_normal_orientation_smoke/
?? src/tase_repro/orientation.py
?? tests/test_orientation.py
```

- Command:

```bash
/usr/bin/python3 scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e.yaml --output-dir runs/force_normal_orientation_smoke/20260524T045559 --duration-s 1.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0009710693359375 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --trajectory e1-cycloid --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --use-slack-solve --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --orientation-mode force-normal --orientation-priority-mode linear-primary --orientation-kp 5.0 --angular-axis-weight 1.0 --angular-slack-weight 1.0
```
