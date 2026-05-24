# Positive Stage B E2 Margin Report

## Summary

v71 tests the remaining v70 blocker: E2 Stage B handoff qdot/timing margin
after positive-side start, terminal, and path feasibility have been recovered
with the run-local `0.12 rad` diagnostic orientation gate.

The formal run is:

- `runs/positive_stage_b_e2_margin/20260524T192129`
- command: `scripts/audit_positive_stage_b_e2_margin.py`
- parent commit before v71 changes: `0c03cf3ff25c7945efff2ad2d74a0b3d3967ad74`

The audit reuses the v70 run-local relaxed target config and per-delta path CSV
artifacts. It evaluates only `e2-figure-eight` for the timing sweep, then runs a
qdot-limit-only probe on the hardest `+1.0 mm` row at the original
`paper_time_scale = 0.01`.

## Metrics

From `runs/positive_stage_b_e2_margin/20260524T192129/metrics.yaml`:

- timing rows: `32`
- qdot-only probe rows: `4`
- E2 pass count at `paper_time_scale = 0.01`: `0 / 8`
- E2 pass count at `paper_time_scale = 0.0075`: `7 / 8`
- E2 pass count at `paper_time_scale = 0.005`: `8 / 8`
- E2 pass count at `paper_time_scale = 0.0025`: `8 / 8`
- fastest all-positive E2 pass scale tested: `0.005`

| paper_time_scale | E2 pass count | max recovered positive delta mm |
| ---: | ---: | ---: |
| `0.01` | `0 / 8` | `none` |
| `0.0075` | `7 / 8` | `+0.75` |
| `0.005` | `8 / 8` | `+1.0` |
| `0.0025` | `8 / 8` | `+1.0` |

Per-delta maximum passing scale:

| delta mm | max passing paper_time_scale |
| ---: | ---: |
| `+0.05` | `0.0075` |
| `+0.10` | `0.0075` |
| `+0.15` | `0.0075` |
| `+0.20` | `0.0075` |
| `+0.25` | `0.0075` |
| `+0.50` | `0.0075` |
| `+0.75` | `0.0075` |
| `+1.00` | `0.005` |

At the original `paper_time_scale = 0.01`, the `+1.0 mm` qdot-limit-only probe
does not recover E2:

| qdot limit rad/s | E2 pass | failed criteria | max orientation rad |
| ---: | --- | --- | ---: |
| `0.15` | `false` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad` | `0.12043140848858806` |
| `0.18` | `false` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad` | `0.12046981651469077` |
| `0.20` | `false` | `max_orientation_error_rad` | `0.12046964616379696` |
| `0.25` | `false` | `max_orientation_error_rad` | `0.12046974135448098` |

## Interpretation

The positive-side Stage B blocker is recoverable by slowing the E2 timing to
`paper_time_scale = 0.005` under the v70 run-local relaxed terminal/path setup.
For the hardest tested `+1.0 mm` row, increasing qdot limit alone at the
original `paper_time_scale = 0.01` removes most qdot pressure but still does not
pass because the Stage B max orientation error remains just above `0.12 rad`.

The remaining executable question is whether the full E1-E4 stitched positive
matrix passes when the v70 relaxed terminal/path setup is combined with
`paper_time_scale = 0.005`.

## Claim Boundary

This is diagnostic-label simulation evidence only. It is not:

- a canonical config change
- strict paper-equivalent feasibility
- robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e
