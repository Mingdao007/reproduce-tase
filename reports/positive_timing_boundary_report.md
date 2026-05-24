# Positive Timing Boundary Report

## Summary

v76 isolates the v73 `paper_time_scale_0p0075` `+1.0 mm` failure. The audit
holds the v70 run-local relaxed terminal/path setup, `stage_a_duration_s =
15.0`, `qdot_limit_rad_s = 0.15`, and the `0.12 rad` diagnostic orientation
gate fixed, then sweeps Stage B `paper_time_scale` for the single hardest
positive cell.

The formal run is:

- `runs/positive_timing_boundary/20260524T200236`
- command: `scripts/audit_positive_timing_boundary.py`
- parent commit before v76 changes: `ee8a5199e22b009c1e8d82901444cb22c148e692`

## Metrics

From `runs/positive_timing_boundary/20260524T200236/metrics.yaml`:

- case count: `9`
- stitched pass count: `2 / 9`
- max passing `paper_time_scale`: `0.0052`
- min failing `paper_time_scale`: `0.0054`
- Stage A pass count: `9 / 9`
- max E2 orientation error: `0.12020305872871904 rad`
- max E2 qdot saturation fraction: `0.999`

| paper_time_scale | stitched pass | Stage B pass | E2 pass | E2 orientation rad | E2 qdot saturation | E2 tail qdot | E2 failed criteria |
| ---: | --- | ---: | --- | ---: | ---: | ---: | --- |
| `0.0050` | `true` | `4 / 4` | `true` | `0.1199788204275829` | `0.006` | `0.0014580486861575888` | none |
| `0.0052` | `true` | `4 / 4` | `true` | `0.11999846384112321` | `0.006` | `0.0015159989338741078` | none |
| `0.0054` | `false` | `3 / 4` | `false` | `0.12001811086329595` | `0.006` | `0.0015739339697212471` | `max_orientation_error_rad` |
| `0.0056` | `false` | `3 / 4` | `false` | `0.12003776159897517` | `0.006` | `0.0016318411885509457` | `max_orientation_error_rad` |
| `0.0058` | `false` | `3 / 4` | `false` | `0.12005741611102583` | `0.006` | `0.001840488196324605` | `max_orientation_error_rad` |
| `0.0060` | `false` | `3 / 4` | `false` | `0.12007703866232994` | `0.007` | `0.001750886518560959` | `max_orientation_error_rad` |
| `0.0065` | `false` | `3 / 4` | `false` | `0.1201260838562` | `0.008` | `0.001898776739473921` | `max_orientation_error_rad` |
| `0.0070` | `false` | `3 / 4` | `false` | `0.12015423656433318` | `0.999` | `1.0` | `qdot_saturation_fraction`, `tail_max_qdot_utilization`, `max_orientation_error_rad` |
| `0.0075` | `false` | `3 / 4` | `false` | `0.12020305872871904` | `0.999` | `1.0` | `qdot_saturation_fraction`, `tail_max_qdot_utilization`, `max_orientation_error_rad` |

## Interpretation

The `+1.0 mm` faster-timing boundary is primarily an E2 orientation margin
immediately above `paper_time_scale = 0.0052`. At `0.0054`, E2 orientation is
already `0.12001811086329595 rad`, just above the diagnostic `0.12 rad` gate,
while qdot saturation remains low. At `0.0070` and `0.0075`, the same E2 row
also saturates qdot heavily.

This does not change the v75 qdot012 recovery and does not recover the separate
v73 `orientation_gate_0p119` tightened-orientation `+1.0 mm` limit.

## Claim Boundary

This is diagnostic-label timing-boundary evidence only. It is not:

- a canonical config change
- strict paper-equivalent feasibility
- a robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

## Next Step

Move to the remaining tightened-orientation `+1.0 mm` boundary, or test whether
a targeted Stage B orientation-margin/control change can recover the
`paper_time_scale >= 0.0054` E2 row without relaxing the diagnostic gate.
