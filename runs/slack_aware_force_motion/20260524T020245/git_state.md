# Git State

- Run root: `runs/slack_aware_force_motion/20260524T020245`
- Branch: `exp/tase-ur10e-v11-slack-aware-solve`
- Starting commit: `de6296836f05bcb95bd855fc8eb9f5cab33c8730`
- Dirty state:
  v11 slack-aware solver source, tests, runner changes, and report were
  uncommitted at run time.
- Scope:
  Full-speed E2/E3 slack-aware probes with normal slack weights `100`, `400`,
  and `10000`, planar slack weight `1`, and qdot cap `0.15 rad/s`.
- Result:
  Slack variables expose the same tradeoff as the weighted/residual probes:
  reducing normal slack recovers force but increases planar slack and
  centimeter-scale path error.
- Note:
  Raw `.npz` files are ignored by repo policy. Metrics and plots are tracked.
