# Git State

- Branch: `exp/tase-ur10e-v32-posture-regularization`
- Commit: `e1af9174121dedb56af4489dcffbe06f3ef8cb9b`
- Dirty tree: `True`
- Status:

```text
M scripts/run_staged_orientation_force_motion.py
 M src/tase_repro/constraints.py
 M src/tase_repro/controller.py
 M src/tase_repro/force_feedback.py
 M src/tase_repro/staged_force_motion.py
 M tests/test_constraints.py
 M tests/test_controller.py
 M tests/test_force_motion.py
?? runs/staged_orientation_e2_posture_regularization/
```

- Command:

```bash
/usr/bin/python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --approach-duration-s 4.0 --trajectory-duration-s 8.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --approach-qdot-limit-rad-s 0.25 --trajectory-qdot-limit-rad-s 0.15 --trajectory e2-figure-eight --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode weighted --approach-orientation-kp 2.0 --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.10 --angular-axis-weight 1.0 --angular-slack-weight 1.0 --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03 --output-dir /home/andy/reproduce-tase/runs/staged_orientation_e2_posture_regularization/20260524T102224/approach_w0p001 --approach-posture-target-q 0,-0.1,0.15,-0.05,0,0 --approach-posture-kp 1.0 --approach-posture-weight 0.001 --approach-max-posture-velocity-rad-s 0.05
```
