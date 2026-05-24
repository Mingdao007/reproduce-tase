# Qdot012 Stage A Margin Report

## Summary

v74 isolates the v73 `qdot012_stage_a18s` `+0.2 mm` failure. The audit holds
the v70 run-local relaxed terminal/path setup, `qdot_limit_rad_s = 0.12`,
`paper_time_scale = 0.005`, and the `0.12 rad` orientation gate fixed, then
sweeps only the Stage A replay duration for the single failing positive cell.

The formal run is:

- `runs/qdot012_stage_a_margin/20260524T194817`
- command: `scripts/audit_qdot012_stage_a_margin.py`
- parent commit before v74 changes: `b0da94bddc277914dd4f7d58639327522ae6bfa5`

## Metrics

From `runs/qdot012_stage_a_margin/20260524T194817/metrics.yaml`:

- case count: `7`
- stitched pass count: `3 / 7`
- last failing Stage A duration: `18.03 s`
- first passing Stage A duration: `18.035 s`
- Stage B pass count: `4 / 4` for every duration

| Stage A duration s | stitched pass | Stage A pass | Stage B pass | Stage A max qdot | final tracking error |
| ---: | --- | --- | ---: | ---: | ---: |
| `18.0` | `false` | `false` | `4 / 4` | `0.12` | `2.8323382178791726e-05` |
| `18.01` | `false` | `false` | `4 / 4` | `0.12` | `1.8979504676181077e-05` |
| `18.02` | `false` | `false` | `4 / 4` | `0.12` | `9.645997736770176e-06` |
| `18.03` | `false` | `false` | `4 / 4` | `0.12` | `3.2284410533080015e-07` |
| `18.035` | `true` | `true` | `4 / 4` | `0.1199690367457867` | `0.0` |
| `18.04` | `true` | `true` | `4 / 4` | `0.11993578590413784` | `0.0` |
| `18.05` | `true` | `true` | `4 / 4` | `0.11986933948543452` | `0.0` |

## Interpretation

The v73 `qdot012_stage_a18s` `+0.2 mm` failure is a narrow Stage A replay
duration margin. Stage B already passes `4 / 4` at every duration in this
sweep; only Stage A final tracking blocks stitched success through `18.03 s`.
Adding `0.035 s` over the v73 `18.0 s` setting recovers the cell.

This does not recover or weaken the v73 `paper_time_scale_0p0075` and
`orientation_gate_0p119` `+1.0 mm` sensitivity failures.

## Claim Boundary

This is diagnostic-label simulation margin evidence only. It is not:

- a canonical config change
- strict paper-equivalent feasibility
- a robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

## Next Step

Decide whether to fold the `18.035 s` qdot012 duration margin into a compact
positive stitched recovery matrix, or leave it as a narrow margin note and move
to the harder `+1.0 mm` timing/orientation sensitivity limits.
