# Strict Feasibility Blockers Audit

Run root: `/home/andy/reproduce-tase/runs/strict_feasibility_blockers/20260525T051640`

- Strict paper-equivalent achieved: `False`
- Strict setup gate complete: `False`
- Trajectory gate often passes: `True`
- Completion claim allowed: `False`
- Offline-actionable from v95: `True`
- Strict full staged pass count: `0 / 4`
- Three-phase setup pass count: `0 / 10`
- Three-phase trajectory pass count: `8 / 10`
- Primary blocker: `strict_setup_terminal_tradeoff`
- Blocker IDs: `['strict_setup_terminal_tradeoff', 'strict_setup_terminal_tangential_error', 'settle_qdot_saturation']`

## Observed Tradeoff

Rows that reduce tangential error either fail orientation or qdot/force criteria; rows that preserve trajectory feasibility still fail strict setup.

## Claim Boundary

- This audit is offline simulation bookkeeping only.
- It does not prove strict paper-equivalent feasibility, robustness,
  contact calibration, or hardware readiness.
