# Positive Stitched Sensitivity Report

## Summary

v73 stress-tests the v72 recovered positive stitched diagnostic policy under a
compact five-scenario sensitivity matrix. Each scenario evaluates the same
eight positive base-z deltas from `+0.05 mm` through `+1.0 mm` and all E1-E4
Stage B trajectories.

The formal run is:

- `runs/positive_stitched_sensitivity/20260524T193845`
- command: `scripts/audit_positive_stitched_sensitivity.py`
- parent commit before v73 changes: `02a2e7ebd473cb05e0fd960df7bb38783e78b11a`

The audit reuses the v70 run-local relaxed terminal/path setup and per-delta
path CSV artifacts. The tightened-orientation scenario writes a run-local copy
of the relaxed Stage A target config inside the v73 run directory; it does not
modify the canonical config.

## Metrics

From `runs/positive_stitched_sensitivity/20260524T193845/metrics.yaml`:

- scenario count: `5`
- matrix stitched pass count: `37 / 40`
- all-pass scenarios: `2 / 5`
- failing scenarios: `qdot012_stage_a18s`, `paper_time_scale_0p0075`,
  `orientation_gate_0p119`

| scenario | stitched pass | Stage A pass | max stitched-pass delta | failure boundary |
| --- | ---: | ---: | ---: | --- |
| `nominal_v72` | `8 / 8` | `8 / 8` | `+1.0 mm` | none |
| `stage_a_14p5s` | `8 / 8` | `8 / 8` | `+1.0 mm` | none |
| `qdot012_stage_a18s` | `7 / 8` | `7 / 8` | `+1.0 mm` | `+0.2 mm` Stage A final tracking error |
| `paper_time_scale_0p0075` | `7 / 8` | `8 / 8` | `+0.75 mm` | `+1.0 mm` E2 qdot/orientation |
| `orientation_gate_0p119` | `7 / 8` | `7 / 8` | `+0.75 mm` | `+1.0 mm` Stage A terminal and Stage B orientation |

Failure details:

- `qdot012_stage_a18s`, `+0.2 mm`: Stage B remains `4 / 4`, but Stage A fails
  `final_tracking_error_norm_rad` with `2.8323382178791726e-05 rad`.
- `paper_time_scale_0p0075`, `+1.0 mm`: Stage A passes, but Stage B is `3 / 4`;
  E2 fails `qdot_saturation_fraction`, `tail_max_qdot_utilization`, and
  `max_orientation_error_rad`.
- `orientation_gate_0p119`, `+1.0 mm`: Stage A fails the tightened terminal
  orientation gate, and all four Stage B rows exceed the tightened orientation
  threshold.

## Interpretation

The v72 nominal result reproduces inside the sensitivity harness, and shortening
Stage A from `15.0 s` to `14.5 s` still preserves all eight positive stitched
passes. The broader matrix does not support a robustness claim: three nearby
perturbations each expose a boundary.

The most recoverable-looking boundary is the `qdot012_stage_a18s` `+0.2 mm`
Stage A replay miss, because Stage B still passes `4 / 4` and the failure is a
small final tracking residual rather than a Stage B handoff collapse. The
`paper_time_scale_0p0075` and `orientation_gate_0p119` `+1.0 mm` failures
preserve the timing and orientation sensitivity already visible in v71-v72.

## Claim Boundary

This is diagnostic-label simulation sensitivity evidence only. It is not:

- a canonical config change
- strict paper-equivalent feasibility
- a robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

## Next Step

Isolate the v73 `qdot012_stage_a18s` `+0.2 mm` Stage A final-tracking boundary
with a small Stage A duration/path-retiming margin audit, while keeping the
`paper_time_scale_0p0075` and `orientation_gate_0p119` `+1.0 mm` failures as
explicit sensitivity limits unless a separate model/control change is made.
