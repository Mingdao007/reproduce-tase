# Git State

- Branch: `exp/tase-ur10e-v35-two-phase-approach-recenter`
- Commit: `aa9ba76c3ef6e5119efaddb0cdbce87d955879af`
- Dirty tree: `True`
- Status:

```text
M scripts/run_staged_orientation_force_motion.py
 M src/tase_repro/force_feedback.py
 M src/tase_repro/staged_force_motion.py
 M tests/test_force_motion.py
 M tests/test_staged_force_motion.py
?? runs/staged_orientation_two_phase_recenter/
```

- Command:

```bash
/usr/bin/python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --approach-duration-s 4.0 --trajectory-duration-s 8.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --approach-qdot-limit-rad-s 0.25 --trajectory-qdot-limit-rad-s 0.15 --trajectory e2-figure-eight --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode weighted --approach-orientation-kp 2.0 --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.10 --angular-axis-weight 1.0 --angular-slack-weight 1.0 --trajectory-posture-target-q 0,-0.1,0.15,-0.05,0,0 --trajectory-posture-kp 1.0 --trajectory-posture-weight 0.001 --trajectory-max-posture-velocity-rad-s 0.05 --approach-orientation-threshold-rad 0.03 --setup-max-final-tangential-error-m 0.002 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03 --output-dir runs/staged_orientation_two_phase_recenter/20260524T104957/lp_recenter_0p4s --recenter-duration-s 0.4 --recenter-qdot-limit-rad-s 0.15 --recenter-planar-kp 0.5 --recenter-orientation-priority-mode linear-primary --recenter-orientation-kp 2.0
```
