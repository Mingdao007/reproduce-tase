# Stage B Priority Recovery Report

## Summary

v79 tests a redesigned Stage B priority formulation for the v77/v78
tightened-orientation boundary. The audit holds the v70 run-local relaxed
terminal/path setup, the `+1.0 mm` positive base-z cell,
`stage_a_duration_s = 15.0`, `paper_time_scale = 0.005`,
`qdot_limit_rad_s = 0.15`, and a tightened `0.11995 rad` Stage A/Stage B
orientation gate fixed. It then compares linear-primary controls against
planar-primary controls with different normal-force secondary weights.

The formal run is:

- `runs/stage_b_priority_recovery/20260524T224404`
- command: `scripts/audit_stage_b_priority_recovery.py`
- parent commit before v79 changes: `de2c2a8d024458a50099cc6fdc4024ed97a229fe`

## Metrics

From `runs/stage_b_priority_recovery/20260524T224404/metrics.yaml`:

- scenario count: `7`
- stitched pass count: `2 / 7`
- Stage A passed every scenario: `true`
- passing scenarios: `planar_normal30_kp0p001`, `planar_normal30_kp0p002`
- max Stage B orientation error across all scenarios: `0.1199788204275829 rad`
- max Stage B qdot saturation fraction across all scenarios: `1.0`
- max Stage B tail force error across all scenarios: `0.3544639543616428 N`

| scenario | priority | normal weight | orientation_kp | stitched | Stage B pass | max orientation rad | max qdot sat | max tail force err N | failed rows |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |
| `linear_kp0` | `linear_primary` | `1.0` | `0.0` | `false` | `3 / 4` | `0.1199788204275829` | `0.006` | `0.0004859525136908127` | E2 orientation |
| `linear_kp0p003` | `linear_primary` | `1.0` | `0.003` | `false` | `3 / 4` | `0.11994467909936898` | `1.0` | `0.009642392425932473` | E2 qdot |
| `linear_kp0p003_posture0p001` | `linear_primary` | `1.0` | `0.003` | `false` | `3 / 4` | `0.11997869470710999` | `0.0` | `0.0004862322920638773` | E2 orientation |
| `planar_normal10_kp0p001` | `planar_primary` | `10.0` | `0.001` | `false` | `3 / 4` | `0.11948537939100295` | `0.0` | `0.3544639543616428` | E2 force |
| `planar_normal30_kp0p001` | `planar_primary` | `30.0` | `0.001` | `true` | `4 / 4` | `0.11973133163816624` | `0.001` | `0.1223546677432889` | none |
| `planar_normal30_kp0p002` | `planar_primary` | `30.0` | `0.002` | `true` | `4 / 4` | `0.11961552028823065` | `0.001` | `0.1902561439715911` | none |
| `planar_normal100_kp0p001` | `planar_primary` | `100.0` | `0.001` | `false` | `3 / 4` | `0.11995127502040462` | `0.188` | `0.009768843872853603` | E2 qdot/orientation |

## Interpretation

The v79 audit recovers the localized `+1.0 mm` tightened-gate diagnostic row
without relaxing the `0.11995 rad` orientation gate or the `0.15 rad/s` qdot
limit. The recovery is not from the v78 single-gain linear-primary orientation
feedback. It comes from changing the Stage B priority split:

- `linear_primary` with no orientation feedback preserves qdot but misses E2
  orientation.
- `linear_primary` with enough orientation feedback fixes E2 orientation but
  saturates qdot.
- `linear_primary` plus handoff-posture regularization preserves qdot by
  giving up the orientation correction.
- `planar_primary` with low normal secondary weighting fixes orientation/qdot
  but gives up E2 force tracking.
- `planar_primary` with normal-axis weight `30` keeps E1-E4 force, x/y,
  orientation, angular slack, qdot saturation, and tail qdot utilization
  within the diagnostic gates for the hardest `+1.0 mm` row.

## Claim Boundary

This is a targeted diagnostic Stage B priority-formulation recovery. It is not:

- a canonical config change
- a full positive-delta matrix recovery
- strict paper-equivalent feasibility
- a robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

## Next Step

Run the recovered planar-primary formulation across the full positive-delta
matrix, or stress it against the v73 faster-timing and tighter-gate sensitivity
cases, before claiming anything stronger than a localized Stage B diagnostic
recovery.
