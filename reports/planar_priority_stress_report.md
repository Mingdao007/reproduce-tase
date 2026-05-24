# Planar-Priority Stress Report

## Summary

v81 stress-tests the v80 planar-primary Stage B priority recovery against the
two remaining v73/v76/v77 sensitivity faces: faster Stage B timing and the
tighter `0.119 rad` orientation gate. The audit keeps the v70 run-local
relaxed terminal/path setup, `stage_a_duration_s = 15.0`, and
`qdot_limit_rad_s = 0.15`, then evaluates both v80 passing candidates:

- `planar_normal30_kp0p001`
- `planar_normal30_kp0p002`

The formal run is:

- `runs/planar_priority_stress/20260524T230109`
- command: `scripts/audit_planar_priority_stress.py`
- parent commit before v81 changes: `44a8c70c61e07dd5f3e48beb55fc0043032adca5`

## Metrics

From `runs/planar_priority_stress/20260524T230109/metrics.yaml`:

- group count: `8`
- total case count: `66`
- total stitched pass count: `35 / 66`
- all groups pass all cases: `false`

Focused `+1.0 mm` boundary sweeps:

| scenario | timing pass | max passing time scale | min failing time scale | gate pass | min passing gate | max failing gate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `planar_normal30_kp0p001` | `7 / 9` | `0.0065` | `0.007` | `3 / 8` | `0.1198` | `0.1197` |
| `planar_normal30_kp0p002` | `7 / 9` | `0.0065` | `0.007` | `4 / 8` | `0.1197` | `0.1196` |

Full positive-delta stress rows:

| stress | scenario | stitched pass | main failure |
| --- | --- | ---: | --- |
| `paper_time_scale = 0.0075`, `gate = 0.11995` | `planar_normal30_kp0p001` | `0 / 8` | E2 qdot saturation and tail qdot utilization |
| `paper_time_scale = 0.0075`, `gate = 0.11995` | `planar_normal30_kp0p002` | `0 / 8` | E2 qdot saturation/tail qdot utilization; `+1.0 mm` also fails E2 tail force |
| `paper_time_scale = 0.005`, `gate = 0.119` | `planar_normal30_kp0p001` | `7 / 8` | `+1.0 mm` Stage A gate and all Stage B rows fail orientation |
| `paper_time_scale = 0.005`, `gate = 0.119` | `planar_normal30_kp0p002` | `7 / 8` | `+1.0 mm` Stage A gate and all Stage B rows fail orientation |

## Interpretation

Planar-primary priority improves the focused `+1.0 mm` timing boundary relative
to the earlier linear-primary v76 boundary: both candidates now pass through
`paper_time_scale = 0.0065` before first failing at `0.007`. It also improves
the focused tightened-gate boundary relative to v77: the `orientation_kp =
0.001` candidate first passes at `0.1198 rad`, and the `orientation_kp =
0.002` candidate first passes at `0.1197 rad`.

Those improvements are not enough for the unresolved v73 stress faces. At
`paper_time_scale = 0.0075`, both candidates fail every positive delta through
`+1.0 mm`. At the `0.119 rad` gate, both candidates pass through `+0.75 mm`
but still fail at `+1.0 mm`.

## Claim Boundary

This is diagnostic-label simulation evidence for the planar-primary Stage B
priority formulation under timing and orientation stress. It is not:

- a canonical config change
- a recovery of `paper_time_scale = 0.0075`
- a recovery of the `+1.0 mm`, `0.119 rad` gate
- a robustness proof
- strict paper-equivalent feasibility
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

## Validation

- `python3 -m py_compile scripts/audit_planar_priority_stress.py`
- `scripts/run_tests.sh`: `115 passed in 2.60s`
- `git diff --check`
- Artifact audit: `474` files, `7.2M`, no `.npz/.npy/.mat/.tar/.gz/.zip`
  payloads under `runs/planar_priority_stress/20260524T230109`

## Next Step

Choose the next diagnostic branch based on the failure mode: either redesign
the faster-timing E2 qdot/tail-utilization behavior at `paper_time_scale =
0.0075`, or revisit the terminal/contact model and orientation gate before
trying to force the `+1.0 mm`, `0.119 rad` case through Stage B tuning.
