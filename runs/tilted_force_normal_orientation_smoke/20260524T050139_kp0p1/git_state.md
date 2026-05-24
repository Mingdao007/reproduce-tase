# Git State

- Branch: `exp/tase-ur10e-v22-tilted-force-normal`
- Commit: `8745c0d284058a2c42185d17d25276c449d405c9`
- Dirty tree: `True`
- Status:

```text
M scripts/run_paper_trajectory_force_motion.py
 M scripts/run_posture_feasibility_sweep.py
 M scripts/run_timing_feasibility_sweep.py
 M src/tase_repro/force_feedback.py
 M tests/test_force_motion.py
?? assets/mjcf/ur10e_tilted_plane_10deg.xml
?? configs/mujoco_ur10e_tilted_plane.yaml
?? runs/tilted_force_normal_orientation_smoke/
```

- Command:

```bash
/usr/bin/python3 scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/tilted_force_normal_orientation_smoke/20260524T050139_kp0p1 --duration-s 2.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --trajectory e1-cycloid --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --use-slack-solve --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --orientation-mode force-normal --orientation-priority-mode linear-primary --orientation-kp 0.1 --angular-axis-weight 1.0 --angular-slack-weight 1.0
```
