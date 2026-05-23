# Git State

- Run root: `runs/normal_guard_force_motion/20260524T015341`
- Branch: `exp/tase-ur10e-v9-normal-guard-force-motion`
- Starting commit: `3eac57b6ee49e55908641b62fc427575f27f39a7`
- Dirty state:
  v9 normal-guard source, tests, runner changes, and report were uncommitted at
  run time.
- Scope:
  Full-speed E2/E3 normal-guard probes and guarded E1-E4 matrix with
  `normal_axis_weight = 50`, `force_gain = 5e-4`, `--qdot-limit-rad-s 0.15`,
  and `normal_guard_force_fraction = 0.9`.
- Result:
  The guard did not solve the full-speed E2/E3 tradeoff. Contact could be
  preserved with weighting, but force regulation and planar tracking remained
  in conflict.
- Note:
  Raw `.npz` files are ignored by repo policy. Metrics and plots are tracked.
