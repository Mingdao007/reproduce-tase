# Git State

- Run root: `runs/weighted_normal_force_motion/20260524T014811`
- Branch: `exp/tase-ur10e-v8-normal-weighted-force-motion`
- Starting commit: `1c1329ca32078f7822d426db6962521bcc714c88`
- Dirty state:
  v8 axis-weighted controller source, runner changes, tests, and report were
  uncommitted at run time.
- Scope:
  Full-speed E2/E3 weighted normal-force probes plus a complete E1-E4 weighted
  matrix with `axis_weights = [1, 1, 100]`, `force_gain = 5e-4`, and
  `--qdot-limit-rad-s 0.15`.
- Result:
  The weighted matrix recovered contact and force regulation but introduced
  large planar errors on E2/E3 and saturated the qdot cap.
- Note:
  Raw `.npz` files are ignored by repo policy. Metrics and plots are tracked.
