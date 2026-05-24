# Git State

- Branch: `exp/tase-ur10e-v31-e2-short-approach-bracket`
- Commit: `63a7910bd10d43e55ed2ecf05137745f8245e53f`
- Dirty tree: `True`
- Status:

```text
?? runs/staged_orientation_e2_short_approach_bracket/
```

- Command:

```bash
/usr/bin/python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/staged_orientation_e2_short_approach_bracket/20260524T101113/approach0p94 --approach-duration-s 0.94 --trajectory-duration-s 8.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --approach-qdot-limit-rad-s 0.25 --trajectory-qdot-limit-rad-s 0.15 --trajectory e2-figure-eight --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode weighted --approach-orientation-kp 2.0 --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.10 --angular-axis-weight 1.0 --angular-slack-weight 1.0 --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03
```
