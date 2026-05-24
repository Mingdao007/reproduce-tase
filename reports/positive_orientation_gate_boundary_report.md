# Positive Orientation Gate Boundary Report

## Summary

v77 isolates the v73 `orientation_gate_0p119` `+1.0 mm` failure. The audit
holds the v70 run-local relaxed terminal/path setup, `stage_a_duration_s =
15.0`, `paper_time_scale = 0.005`, and `qdot_limit_rad_s = 0.15` fixed, then
sweeps both the run-local Stage A terminal orientation gate and the Stage B
`max_orientation_error_rad` gate for the single hardest positive cell.

The formal run is:

- `runs/positive_orientation_gate_boundary/20260524T221842`
- command: `scripts/audit_positive_orientation_gate_boundary.py`
- parent commit before v77 changes: `05a84809099e6a526d52e89c939a79b587ca9503`

## Metrics

From `runs/positive_orientation_gate_boundary/20260524T221842/metrics.yaml`:

- case count: `9`
- stitched pass count: `2 / 9`
- max failing orientation gate: `0.11997`
- min passing orientation gate: `0.11998`
- max Stage A terminal orientation error: `0.11948560786547915 rad`
- max Stage B orientation error: `0.1199788204275829 rad`

| orientation gate | stitched pass | Stage A pass | Stage B pass | Stage A orientation rad | max Stage B orientation rad | failed rows |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| `0.11900` | `false` | `false` | `0 / 4` | `0.11948560786547915` | `0.1199788204275829` | E1/E2/E3/E4 orientation |
| `0.11925` | `false` | `false` | `0 / 4` | `0.11948560786547915` | `0.1199788204275829` | E1/E2/E3/E4 orientation |
| `0.11950` | `false` | `true` | `3 / 4` | `0.11948560786547915` | `0.1199788204275829` | E2 orientation |
| `0.11975` | `false` | `true` | `3 / 4` | `0.11948560786547915` | `0.1199788204275829` | E2 orientation |
| `0.11990` | `false` | `true` | `3 / 4` | `0.11948560786547915` | `0.1199788204275829` | E2 orientation |
| `0.11995` | `false` | `true` | `3 / 4` | `0.11948560786547915` | `0.1199788204275829` | E2 orientation |
| `0.11997` | `false` | `true` | `3 / 4` | `0.11948560786547915` | `0.1199788204275829` | E2 orientation |
| `0.11998` | `true` | `true` | `4 / 4` | `0.11948560786547915` | `0.1199788204275829` | none |
| `0.12000` | `true` | `true` | `4 / 4` | `0.11948560786547915` | `0.1199788204275829` | none |

## Interpretation

The `+1.0 mm` tightened-orientation boundary has two levels:

- Stage A terminal orientation passes once the gate is at least `0.1195 rad`.
- Full stitched recovery still fails until the gate reaches `0.11998 rad`
  because E2 has the largest Stage B orientation error
  (`0.1199788204275829 rad`).

This explains why v73 `orientation_gate_0p119` failed all Stage B rows at the
tightened gate and why the v72/v75 `0.12 rad` diagnostic gate passes. It does
not change the v75 qdot012 recovery or the v76 faster-timing boundary.

## Claim Boundary

This is diagnostic-label orientation-boundary evidence only. It is not:

- a canonical config change
- strict paper-equivalent feasibility
- a robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

## Next Step

The remaining positive-side boundary is no longer an unlocalized gate setting:
under the current target/path/timing setup, the hardest E2 row needs almost the
full `0.12 rad` orientation allowance. A next branch should test a Stage B
orientation-margin/control change or revisit the terminal/contact model before
claiming anything stronger than diagnostic recovery.
