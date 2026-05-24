# Stage B Orientation Kp Probe Report

## Summary

v78 tests whether the v77 tightened-orientation boundary can be removed by
adding Stage B force-normal orientation feedback. The audit holds the v70
run-local relaxed terminal/path setup, the `+1.0 mm` positive base-z cell,
`stage_a_duration_s = 15.0`, `paper_time_scale = 0.005`, and a tightened
`0.11995 rad` Stage A/Stage B orientation gate fixed. It then sweeps E2-only
Stage B rows across `orientation_kp` and qdot limits.

The formal run is:

- `runs/stage_b_orientation_kp_probe/20260524T222953`
- command: `scripts/audit_stage_b_orientation_kp_probe.py`
- parent commit before v78 changes: `31e3dfdcced6807232931d2e94e7a6383befac7a`

## Metrics

From `runs/stage_b_orientation_kp_probe/20260524T222953/metrics.yaml`:

- case count: `30`
- stitched pass count: `0 / 30`
- Stage A pass count: `30 / 30`
- E2 orientation-ok cases: `13 / 30`
- E2 orientation gate: `0.11995 rad`
- min E2 orientation error: `0.11990689588867036 rad`
- min E2 qdot saturation fraction: `0.0`
- min E2 tail qdot utilization: `0.000874717789387994`

Representative rows:

| qdot limit | orientation_kp | E2 orientation rad | E2 qdot sat | E2 tail qdot | failed criteria |
| ---: | ---: | ---: | ---: | ---: | --- |
| `0.15` | `0.0` | `0.1199788204275829` | `0.006` | `0.0014580486861575888` | `max_orientation_error_rad` |
| `0.15` | `0.003` | `0.11994467909936898` | `1.0` | `1.0` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.2` | `0.0` | `0.11997883364101876` | `0.0` | `0.0010947845693568656` | `max_orientation_error_rad` |
| `0.2` | `0.01` | `0.11990689588867036` | `0.999` | `1.0` | `qdot_saturation_fraction,tail_max_qdot_utilization` |
| `0.25` | `0.001` | `0.11997875722613961` | `0.0` | `0.000874717789387994` | `max_orientation_error_rad` |
| `0.25` | `0.003` | `0.11992270620345662` | `0.477` | `1.0` | `qdot_saturation_fraction,tail_max_qdot_utilization` |

## Interpretation

The targeted Stage B orientation feedback does not produce a feasible E2 row
under the audited gate. Low gains preserve the qdot budget but leave E2
orientation just above `0.11995 rad`. Gains large enough to reduce E2
orientation below the gate consume the qdot budget and fail qdot saturation
and/or tail qdot utilization, even when the tested qdot limit is relaxed to
`0.25 rad/s`.

The result is therefore a negative diagnostic control probe: the v77
tightened-orientation boundary is not removed by simply enabling the existing
Stage B `orientation_kp` feedback in the current linear-primary formulation.

## Claim Boundary

This is diagnostic-label E2 Stage B probe evidence only. It is not:

- a canonical controller/config change
- a full E1-E4 stitched recovery
- strict paper-equivalent feasibility
- a robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

## Next Step

Move away from single-gain Stage B orientation feedback as the fix for the
v77 boundary. The next branch should revisit the terminal/contact model or test
a redesigned Stage B priority/posture formulation that can create orientation
margin without driving qdot saturation.
