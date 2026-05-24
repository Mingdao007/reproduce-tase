# Git State

- Branch: `exp/tase-ur10e-v34-planar-primary-approach`
- Commit: `9973dd16cfb445487c02d843854e40fb3892af42`
- Dirty tree: `True`
- Status:

```text
M scripts/run_staged_orientation_force_motion.py
 M src/tase_repro/constraints.py
 M src/tase_repro/controller.py
 M src/tase_repro/force_feedback.py
 M tests/test_constraints.py
 M tests/test_controller.py
 M tests/test_force_motion.py
?? runs/staged_orientation_planar_primary_approach/
```

- Command:

```bash
/usr/bin/python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --trajectory-duration-s 2.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --trajectory-qdot-limit-rad-s 0.15 --trajectory e1-cycloid --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.10 --angular-axis-weight 1.0 --angular-slack-weight 1.0 --trajectory-posture-target-q 0,-0.1,0.15,-0.05,0,0 --trajectory-posture-kp 1.0 --trajectory-posture-weight 0.001 --trajectory-max-posture-velocity-rad-s 0.05 --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03 --output-dir /home/andy/reproduce-tase/runs/staged_orientation_planar_primary_approach/20260524T103539/planar_primary_kp1_a0p25_8s --approach-duration-s 8.0 --approach-qdot-limit-rad-s 0.25 --approach-orientation-priority-mode planar-primary --approach-orientation-kp 1.0
```
