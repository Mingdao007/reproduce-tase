# Positive Planar-Priority Matrix Report

## Summary

v80 tests whether the v79 planar-primary Stage B priority recovery generalizes
from the localized `+1.0 mm` tightened-gate row to the full positive-delta
matrix. The audit holds the v70 run-local relaxed terminal/path setup,
`stage_a_duration_s = 15.0`, `paper_time_scale = 0.005`,
`qdot_limit_rad_s = 0.15`, and a run-local `0.11995 rad` Stage A/Stage B
orientation gate fixed. It evaluates both v79 passing candidates across all
eight positive base-z deltas and all E1-E4 Stage B trajectories.

The formal run is:

- `runs/positive_planar_priority_matrix/20260524T225138`
- command: `scripts/audit_positive_planar_priority_matrix.py`
- parent commit before v80 changes: `5a11a2505a2d864abbf6db8e2ded33c0c921a12b`

## Metrics

From `runs/positive_planar_priority_matrix/20260524T225138/metrics.yaml`:

- scenario count: `2`
- total case count: `16`
- total stitched pass count: `16 / 16`
- all scenarios pass all cases: `true`
- passing scenarios: `planar_normal30_kp0p001`, `planar_normal30_kp0p002`

Scenario aggregates:

| scenario | stitched pass | max positive pass delta mm | max Stage B orientation rad | max Stage B qdot sat | max Stage B tail qdot | max Stage B force err N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `planar_normal30_kp0p001` | `8 / 8` | `1.0` | `0.11973133163816624` | `0.001` | `0.0010837631758864566` | `0.1223546677432889` |
| `planar_normal30_kp0p002` | `8 / 8` | `1.0` | `0.11961552028823065` | `0.001` | `0.0009960728846485063` | `0.1902561439715911` |

## Interpretation

Both v79 passing candidates generalize across the full positive-delta matrix
under the tested diagnostic gates. Compared with the v72/v75 linear-primary
diagnostic recovery, v80 keeps the tightened `0.11995 rad` orientation gate and
recovers all eight positive deltas through `+1.0 mm` at `qdot_limit_rad_s =
0.15`.

The two passing scenarios show the expected gain tradeoff:

- `orientation_kp = 0.001` leaves more orientation error but lower force error.
- `orientation_kp = 0.002` reduces maximum orientation error but increases the
  worst E2 tail force error while staying within the `0.25 N` gate.

## Claim Boundary

This is diagnostic-label full positive-delta matrix evidence for the
planar-primary Stage B priority formulation. It is not:

- a canonical config change
- a faster-timing recovery
- a qdot012 recovery under the tightened gate
- strict paper-equivalent feasibility
- a robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

## Next Step

Stress the recovered planar-primary formulation against the unresolved v73/v76
faster-timing boundary and the tighter `0.119 rad` orientation gate before
claiming anything stronger than diagnostic recovery.
