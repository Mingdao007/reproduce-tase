# Strict Feasibility Policy Probe Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v113-strict-feasibility-policy-probe`

Implementation commit: `IMPLEMENTATION_COMMIT_PENDING`

## Objective

Run the highest-priority offline-actionable v112 blocker as a compact,
non-final simulation probe: test whether a small set of Stage A priority
policies can satisfy the strict setup terminal gate before the E2 Stage B
trajectory.

No hardware command, live read, TCP/payload/configuration write, force-control
step, gate acceptance, contact calibration, or robustness claim is performed.

## Artifacts

- New audit script:
  `scripts/audit_strict_feasibility_policy_probe.py`
- New run:
  `runs/strict_feasibility_policy_probe/20260525T073519`
- New test:
  `tests/test_strict_feasibility_policy_probe.py`

## Result

The v113 probe reports:

```text
case_count = 8
setup_terminal_state_pass_count = 0 / 8
trajectory_feasibility_pass_count = 4 / 8
planned_setup_then_trajectory_pass_count = 0 / 8
full_staged_feasibility_pass_count = 0 / 8
strict_policy_probe_complete = false
strict_paper_equivalent_feasibility = false
do_not_mark_goal_complete = true
```

Failure counts across the eight setup policies:

```text
final_orientation_error_rad = 3
final_tangential_position_error_m = 6
tail_mean_abs_force_error_N = 2
qdot_saturation_fraction = 8
tail_max_qdot_utilization = 8
```

Best observed rows:

| metric | best case | value |
| --- | --- | ---: |
| setup violation score | `linear_recenter_4_no_settle` | `100.06894073213962` |
| setup x/y error | `linear_recenter_4_linear_settle_4` | `0.0001777515283299582 m` |
| setup orientation error | `weighted_recenter_4_weighted_settle_2` | `0.0019220380036386873 rad` |

Interpretation:

- No tested Stage A policy satisfies the strict setup terminal-state gate.
- Weighted settling preserves force-normal orientation and following E2
  trajectory feasibility in several rows, but gives back x/y recentering.
- Linear-primary settling preserves x/y, but fails orientation and the
  following E2 trajectory.
- Aggressive planar retention reduces x/y drift but reintroduces orientation,
  force, and qdot pressure.
- Every tested row violates qdot saturation and tail qdot utilization in the
  setup phase, so strict paper-equivalent feasibility remains blocked even
  before robustness/contact/hardware evidence.

## Claim Boundary

V113 is offline simulation only. It does not prove strict paper-equivalent
feasibility, make a canonical controller change, accept a replacement
orientation gate, close failed cells, prove robustness, calibrate contact
geometry, establish hardware readiness, or authorize hardware
motion/configuration.

## Validation

- `python3 -m py_compile scripts/audit_strict_feasibility_policy_probe.py`
  passed.
- `scripts/run_tests.sh tests/test_strict_feasibility_policy_probe.py`
  passed with `3 passed in 0.12s`.
- `python3 scripts/audit_strict_feasibility_policy_probe.py --output-dir runs/strict_feasibility_policy_probe/20260525T073519`
  created the v113 run.
- `rg -n "&id|\*id" runs/strict_feasibility_policy_probe/20260525T073519/metrics.yaml`
  found no YAML anchors in the root summary metrics.
- `find runs/strict_feasibility_policy_probe/20260525T073519 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `168 passed in 7.11s`.
- `git diff --check`
  passed.
- Branch push was verified at
  `BRANCH_PUSH_PENDING`.

## Next Step

Without explicit live bench approval, continue only non-final offline work. The
next strict-feasibility probe should change the Stage A formulation beyond the
current instantaneous weighted or two-level velocity allocation, specifically
to constrain x/y recentering while restoring force-normal orientation without
setup qdot saturation.
