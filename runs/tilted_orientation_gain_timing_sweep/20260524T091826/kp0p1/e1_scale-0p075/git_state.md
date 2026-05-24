# Git State

- Branch: `exp/tase-ur10e-v23-tilted-gain-timing`
- Commit: `e37a5545af1cb9d406848180a7ef5d772df7f4e8`
- Dirty tree: `True`
- Status:

```text
?? runs/tilted_orientation_gain_timing_sweep/
```

- Command:

```bash
/usr/bin/python3 /home/andy/reproduce-tase/scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir /home/andy/reproduce-tase/runs/tilted_orientation_gain_timing_sweep/20260524T091826/kp0p1/e1_scale-0p075 --duration-s 2.0 --target-force-N 5.0 --force-gain 0.0005 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --trajectory e1-cycloid --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --use-slack-solve --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --orientation-mode force-normal --orientation-priority-mode linear-primary --orientation-kp 0.1 --angular-axis-weight 1.0 --angular-slack-weight 1.0
```
