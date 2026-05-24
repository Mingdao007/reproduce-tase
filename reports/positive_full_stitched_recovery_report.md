# Positive Full Stitched Recovery Report

## Summary

v72 tests the executable consequence of v71: whether the v70 positive
relaxed terminal/path setup can recover the full E1-E4 stitched Stage A plus
Stage B diagnostic matrix when Stage B uses the E2-safe timing
`paper_time_scale = 0.005`.

The formal run is:

- `runs/positive_full_stitched_recovery/20260524T192854`
- command: `scripts/audit_positive_full_stitched_recovery.py`
- parent commit before v72 changes: `121ad38c0268faeafe8e1daded8015de8f25639c`

The audit reuses the v70 run-local relaxed target config and per-delta path CSV
artifacts. It evaluates all E1-E4 trajectories for each positive base-z delta
from `+0.05 mm` through `+1.0 mm`.

## Metrics

From `runs/positive_full_stitched_recovery/20260524T192854/metrics.yaml`:

- positive case count: `8`
- stitched pass count: `8 / 8`
- max positive stitched-pass delta: `+1.0 mm`
- Stage B trajectories per row: `4 / 4`
- max Stage B qdot saturation fraction: `0.006`
- max Stage B tail qdot utilization: `0.3579877267896789`
- max Stage B orientation error: `0.1199788204275829 rad`

| delta mm | stitched pass | Stage B pass count | Stage B qdot saturation | Stage B max orientation rad |
| ---: | --- | ---: | ---: | ---: |
| `+0.05` | `true` | `4 / 4` | `0.0` | `0.08420730609192884` |
| `+0.10` | `true` | `4 / 4` | `0.0` | `0.08604620949512072` |
| `+0.15` | `true` | `4 / 4` | `0.0` | `0.0878924064819036` |
| `+0.20` | `true` | `4 / 4` | `0.0` | `0.08974563803371456` |
| `+0.25` | `true` | `4 / 4` | `0.0` | `0.0916056636457473` |
| `+0.50` | `true` | `4 / 4` | `0.0` | `0.10099329829600373` |
| `+0.75` | `true` | `4 / 4` | `0.0` | `0.11048096113317912` |
| `+1.00` | `true` | `4 / 4` | `0.006` | `0.1199788204275829` |

## Interpretation

The v70 relaxed positive terminal/path setup plus v71's E2-safe timing recovers
the full positive E1-E4 stitched diagnostic matrix for all tested positive
deltas through `+1.0 mm`.

This closes the specific positive-side stitched gap found in v70. It does not
make the result robust or paper-equivalent: the recovery still depends on a
run-local `0.12 rad` diagnostic terminal orientation gate and slowed
`paper_time_scale = 0.005`.

## Claim Boundary

This is diagnostic-label simulation evidence only. It is not:

- a canonical config change
- strict paper-equivalent feasibility
- robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

## Next Step

Stress-test the v72 recovered positive stitched policy under a compact
sensitivity matrix, keeping the `0.12 rad` relaxed orientation gate and
`paper_time_scale = 0.005` label explicit.
