# Git State

- Branch: `exp/tase-ur10e-v27-approach-rate-cap`
- Commit: `5bf5cb829744625a52905d82e996b20515049f84`
- Dirty tree: `True`
- Status:

```text
M scripts/run_staged_orientation_force_motion.py
 M src/tase_repro/force_feedback.py
 M src/tase_repro/staged_force_motion.py
 M tests/test_staged_force_motion.py
?? runs/staged_orientation_rate_cap_probe/
```

- Command:

```bash
/usr/bin/python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/staged_orientation_rate_cap_probe/20260524T094752/weighted_cap0p03_kp2_6s --approach-duration-s 6.0 --trajectory-duration-s 2.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --trajectory e1-cycloid --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode weighted --approach-orientation-kp 2.0 --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.1 --angular-axis-weight 1.0 --angular-slack-weight 1.0 --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03 --approach-max-angular-command-rad-s 0.03
```
