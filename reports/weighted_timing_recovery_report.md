# Weighted Timing Recovery Report

## Summary

v82 tests a weighted zero-angular-command Stage B priority candidate surfaced by
the v82 throwaway probe. The target is the v81 faster-timing failure face:
`paper_time_scale = 0.0075`, `orientation_gate = 0.11995 rad`, positive base-z
deltas through `+1.0 mm`, and the v70 run-local relaxed terminal/path setup.

The formal run is:

- `runs/weighted_timing_recovery/20260524T231454`
- command: `scripts/audit_weighted_timing_recovery.py`
- parent commit before v82 changes: `8f4a94ca9729a5eb626b0e73960a1e14f9dea608`

## Metrics

From `runs/weighted_timing_recovery/20260524T231454/metrics.yaml`:

- full-delta scenario count: `5`
- full-delta stitched pass count: `23 / 40`
- all-pass full-delta scenarios: `weighted_kp0_normal1`, `weighted_kp0_normal30`
- focused `+1.0 mm` timing sweep pass count: `10 / 10`
- focused timing sweep max passing `paper_time_scale`: `0.01`
- focused timing sweep min failing `paper_time_scale`: `none`

Full positive-delta stress at `paper_time_scale = 0.0075`:

| scenario | priority | normal weight | pass count | max pass delta mm | max orientation | max qdot sat | max tail qdot | max force err N |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `linear_kp0_normal1` | `linear_primary` | `1.0` | `7 / 8` | `0.75` | `0.12020305872871904` | `0.999` | `1.0` | `0.006603888075066666` |
| `planar_normal30_kp0p001` | `planar_primary` | `30.0` | `0 / 8` | `none` | `0.11983992753823672` | `0.143` | `1.0` | `0.20098660314203312` |
| `planar_normal30_kp0p002` | `planar_primary` | `30.0` | `0 / 8` | `none` | `0.11972166555008389` | `0.234` | `1.0` | `0.275874931458737` |
| `weighted_kp0_normal1` | `weighted` | `1.0` | `8 / 8` | `1.0` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0009911909058976187` |
| `weighted_kp0_normal30` | `weighted` | `30.0` | `8 / 8` | `1.0` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0009911909058976187` |

Focused `+1.0 mm` timing sweep for `weighted_kp0_normal1`:

- `paper_time_scale = 0.005` through `0.01` all pass.
- max Stage B orientation over the sweep: `0.11956645203696047 rad`
- max qdot saturation fraction over the sweep: `0.0`
- max tail qdot utilization over the sweep: `0.5278218979712962`
- max tail force error over the sweep: `0.0008424456782388923 N`

## Interpretation

The v81 faster-timing failure was not a hard timing infeasibility of the path
and qdot limits. It was a priority-formulation artifact: planar-primary
priority at the tested gains drives E2 qdot/tail utilization and force tradeoffs
at `paper_time_scale = 0.0075`, while weighted zero-angular-command priority
keeps the same diagnostic gate inside margin with no qdot saturation.

The normal-axis weight does not change this candidate in the tested matrix:
`weighted_kp0_normal1` and `weighted_kp0_normal30` have identical aggregate
metrics in the formal run.

## Claim Boundary

This is diagnostic-label faster-timing recovery evidence only. It is not:

- a canonical controller default
- a recovery of the `0.119 rad` tightened orientation gate
- a proof that `paper_time_scale = 0.01` passes the full positive-delta matrix
- a robustness proof
- strict paper-equivalent feasibility
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

## Validation

- `python3 -m py_compile scripts/audit_weighted_timing_recovery.py`
- `scripts/run_tests.sh`: `115 passed in 2.66s`
- `git diff --check`
- Artifact audit: `355` files, `5.4M`, no `.npz/.npy/.mat/.tar/.gz/.zip`
  payloads under `runs/weighted_timing_recovery/20260524T231454`

## Next Step

Stress the weighted zero-angular-command candidate against the `0.119 rad`
orientation gate and, separately, decide whether a full positive-delta matrix at
`paper_time_scale = 0.01` is a meaningful diagnostic target before treating the
faster-timing face as closed.
