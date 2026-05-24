# Qdot012 Positive Stitched Matrix Report

## Summary

v75 folds the v74 `18.035 s` qdot012 Stage A duration margin back into the
full positive stitched matrix. The audit reuses the v70 run-local relaxed
terminal/path setup and evaluates all eight positive base-z deltas from
`+0.05 mm` through `+1.0 mm` with all E1-E4 Stage B trajectories.

The formal run is:

- `runs/positive_full_stitched_recovery/20260524T195501`
- command: `scripts/audit_positive_full_stitched_recovery.py --stage-a-duration-s 18.035 --qdot-limit-rad-s 0.12 --paper-time-scale 0.005 --max-orientation-error-rad 0.12`
- parent commit before v75 changes: `d904e0f2ec38d116f0a8103a9014d6283fde8a1e`

## Metrics

From `runs/positive_full_stitched_recovery/20260524T195501/metrics.yaml`:

- case count: `8`
- stitched pass count: `8 / 8`
- max positive stitched-pass delta: `+1.0 mm`
- Stage B handoff count: `4 / 4` for every positive delta
- max Stage B qdot saturation fraction: `0.001`
- max Stage B tail qdot utilization: `0.4474846584870986`
- max Stage B orientation error: `0.11997895388586574 rad`

| delta mm | stitched pass | Stage B pass | Stage A max qdot | Stage B qdot saturation | Stage B max orientation rad |
| ---: | --- | ---: | ---: | ---: | ---: |
| `+0.05` | `true` | `4 / 4` | `0.11809294100915854` | `0.0` | `0.08420730609192884` |
| `+0.10` | `true` | `4 / 4` | `0.11816011213646939` | `0.0` | `0.08604620949512072` |
| `+0.15` | `true` | `4 / 4` | `0.11819953468738618` | `0.0` | `0.0878924064819036` |
| `+0.20` | `true` | `4 / 4` | `0.1199690367457867` | `0.0` | `0.08974563803371456` |
| `+0.25` | `true` | `4 / 4` | `0.09977607944751221` | `0.0` | `0.0916056636457473` |
| `+0.50` | `true` | `4 / 4` | `0.09335801735430703` | `0.0` | `0.10099329829600373` |
| `+0.75` | `true` | `4 / 4` | `0.08623070567481625` | `0.0` | `0.11048096113317912` |
| `+1.00` | `true` | `4 / 4` | `0.08332618384112458` | `0.001` | `0.11997895388586574` |

## Interpretation

The v74 `18.035 s` Stage A duration is sufficient to recover the full positive
qdot012 stitched diagnostic matrix. This closes the specific v73
`qdot012_stage_a18s` sensitivity failure across all tested positive deltas.

This does not recover the other v73 failures: `paper_time_scale_0p0075` still
has a documented `+1.0 mm` E2 qdot/orientation boundary, and
`orientation_gate_0p119` still has a documented `+1.0 mm` orientation boundary.

## Claim Boundary

This is diagnostic-label simulation evidence only. It is not:

- a canonical config change
- strict paper-equivalent feasibility
- a robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

## Next Step

Move to the harder `+1.0 mm` faster-timing and tighter-orientation sensitivity
limits, unless the project chooses to stop the qdot012 branch at this recovered
diagnostic matrix.
