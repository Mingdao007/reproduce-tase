# Git State

- Run: `runs/paper_trajectory_force_motion/20260524T013829`
- Command:
  `python3 scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e.yaml --duration-s 8.0 --target-force-N 5.0 --force-gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5 --trajectory e1-cycloid --amplitude-m 0.015 --omega-rad-s 0.1 --paper-time-scale 1.0 --planar-kp 0.5`
- Branch: `exp/tase-ur10e-v6-paper-trajectory-force-motion`
- Starting commit: `e47c2fe6d3ec1b17904623dcab1d787441d0183b`
- Dirty state:
  v6 paper trajectory force-motion source, tests, and report were uncommitted
  at run time.
- Note:
  The raw `.npz` output is ignored by repo policy. Metrics and plots are
  tracked.
