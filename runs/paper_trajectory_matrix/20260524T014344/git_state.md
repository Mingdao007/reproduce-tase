# Git State

- Run root: `runs/paper_trajectory_matrix/20260524T014344`
- Branch: `exp/tase-ur10e-v7-paper-trajectory-matrix`
- Starting commit: `e89f3561d576c420374aebdb8f7fe85839b49674`
- Dirty state:
  v7 trajectory-family source, tests, report, and qdot-limit override were
  uncommitted at run time.
- Scope:
  Low-speed E1-E4 matrix with `--paper-time-scale 0.25` and the config default
  `0.05 rad/s` qdot cap.
- Result:
  All four trajectories maintained contact, solver success, and hard-limit
  compliance.
- Note:
  Raw `.npz` files are ignored by repo policy. Metrics and plots are tracked.
