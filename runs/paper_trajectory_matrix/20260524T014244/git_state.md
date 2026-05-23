# Git State

- Run root: `runs/paper_trajectory_matrix/20260524T014244`
- Branch: `exp/tase-ur10e-v7-paper-trajectory-matrix`
- Starting commit: `e89f3561d576c420374aebdb8f7fe85839b49674`
- Dirty state:
  v7 trajectory-family source, tests, and qdot-limit override were uncommitted
  at run time.
- Scope:
  Full-speed E1-E4 matrix with `--qdot-limit-rad-s 0.15`, plus E2/E3
  `force_gain = 5e-4` probes.
- Result:
  E2 and E3 still lost contact. Higher force gain saturated near the qdot cap
  and did not recover contact.
- Note:
  Raw `.npz` files are ignored by repo policy. Metrics and plots are tracked.
