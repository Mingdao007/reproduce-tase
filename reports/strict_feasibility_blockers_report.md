# Strict Feasibility Blockers Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v96-strict-feasibility-blockers`

## Objective

Quantify the strict paper-equivalent staged-feasibility blocker using existing
offline summaries and the current strict acceptance thresholds. This is the
v95 offline-actionable strict-feasibility item only; it is not a completion
claim.

## Artifacts

- New audit script:
  `scripts/audit_strict_feasibility_blockers.py`
- New audit run:
  `runs/strict_feasibility_blockers/20260525T051640`
- New tests:
  `tests/test_strict_feasibility_blockers.py`

## Result

The audit reads:

- `configs/ur10e_adapted_acceptance.yaml`
- `runs/staged_orientation_e1e4_posture_regularized/20260524T102747/summary.yaml`
- `runs/staged_orientation_three_phase_settle/20260524T110039/summary.yaml`
- `runs/offline_completion_blockers/20260525T020734/metrics.yaml`

It reports:

```text
overall_goal_complete = false
strict_feasibility_complete = false
strict_setup_gate_complete = false
strict_full_staged_feasibility_pass_count = 0 / 4
three_phase_setup_terminal_state_pass_count = 0 / 10
three_phase_trajectory_feasibility_pass_count = 8 / 10
primary_blocker = strict_setup_terminal_tradeoff
do_not_mark_goal_complete = true
```

The posture-regularized strict staged rows have terminal orientation within
the `0.03 rad` strict gate for all `4 / 4` rows, but all `4 / 4` rows fail
the strict tangential setup threshold. The three-phase settle matrix keeps
trajectory feasibility at `8 / 10`, but no row satisfies the strict setup
terminal state. The best tangential and force rows are `lp4_settle_lp4`, which
still fails orientation; the best orientation row is `baseline_no_recenter`,
which still fails tangential position. All settled rows with a recorded settle
qdot saturation fraction exceed the `0.01` strict threshold.

## Claim Boundary

V96 is offline simulation bookkeeping only. It does not collect live
measurements, execute the read-only SOP, move the UR10e, write configuration,
zero/bias/filter the force sensor, run force control, reconcile force-source
frames, accept a replacement orientation gate, calibrate the contact model,
prove robustness, prove strict paper-equivalent feasibility, or make a
hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/audit_strict_feasibility_blockers.py`
  passed.
- `scripts/run_tests.sh tests/test_strict_feasibility_blockers.py`
  passed with `2 passed in 0.18s`.
- `python3 scripts/audit_strict_feasibility_blockers.py --run-id 20260525T051640`
  created the v96 blocker audit.
- `scripts/run_tests.sh` passed with `130 passed in 5.04s`.
- `git diff --check` passed after full-test validation.
- Branch push was verified at
  `31bcca912b2623bd4f29850077ab86a76ec1ec4e`.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
The next offline target can either search for a strict setup terminal policy
that satisfies tangential, orientation, force, and qdot gates simultaneously,
or shift to the separate robustness blocker from the v95 audit. The
calibration, gate acceptance, and hardware-readiness chain remains blocked
until approved read-only measurement evidence exists.
