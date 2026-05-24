# Stage A Base-Z Bracket Report

## Summary

v67 refines the v66 base-z recovery result with a compact perturbation bracket.
It keeps the v66 diagnostic setup label, adds the v58 selected Stage A target
as an explicit terminal seed, and stores compact terminal evidence so the run
does not duplicate full candidate dumps for every bracket point.

The formal run is:

- `runs/stage_a_base_z_bracket/20260524T165411`
- command: `scripts/audit_stage_a_base_z_bracket.py`
- parent commit before v67 changes: `3f280e2d35ea2d87abc9769a81c1ff0cf377415e`

The bracket evaluates `13` base-z deltas from `-1.0 mm` to `+1.0 mm` and tests
Stage A durations `15.0 s` and `16.0 s` when start, terminal, and path geometry
are feasible.

## Metrics

From `runs/stage_a_base_z_bracket/20260524T165411/metrics.yaml`:

- start pass count: `5 / 13`
- terminal pass count: `5 / 13`
- path geometry pass count: `4 / 13`
- duration recovered count: `7`
- max positive terminal-pass delta: `none`
- max positive recovered delta: `none`

| delta mm | status | recovered durations | path min duration s | key result |
| ---: | --- | --- | ---: | --- |
| `-1.0` | `recovered_at_tested_duration` | `16.0` | `15.652271522331025` | Confirms v66: 15 s misses qdot budget, 16 s passes. |
| `-0.75` | `path_geometry_failed` | `none` | `138.0288650739265` | Start and terminal pass, but path has max scheduled orientation error `0.09627510687282123 rad`, above the `0.08 rad` gate. |
| `-0.5` | `recovered_at_tested_duration` | `15.0`, `16.0` | `14.625580232388335` | Recovered at both tested durations. |
| `-0.25` | `recovered_at_tested_duration` | `15.0`, `16.0` | `14.37320363810477` | Recovered at both tested durations. |
| `0.0` | `recovered_at_tested_duration` | `15.0`, `16.0` | `14.332635022800167` | Nominal selected target is preserved by the explicit v58 seed. |
| `+0.05` | `start_and_terminal_not_found` | `none` | `none` | Start loses target contact and terminal orientation is `0.0838175590896232 rad`, already above the `0.08 rad` gate. |
| `+0.10` | `start_and_terminal_not_found` | `none` | `none` | Same positive-side failure class. |
| `+0.15` | `start_and_terminal_not_found` | `none` | `none` | Same positive-side failure class. |
| `+0.20` | `start_and_terminal_not_found` | `none` | `none` | Same positive-side failure class. |
| `+0.25` | `start_and_terminal_not_found` | `none` | `none` | Same positive-side failure class. |
| `+0.50` | `start_and_terminal_not_found` | `none` | `none` | Same positive-side failure class. |
| `+0.75` | `start_and_terminal_not_found` | `none` | `none` | Same positive-side failure class. |
| `+1.00` | `start_and_terminal_not_found` | `none` | `none` | Same positive-side failure class; this is the v64 `base_z_plus_1mm` side. |

## Claim Boundary

This is diagnostic-label simulation bracket evidence only. It is not:

- strict paper-equivalent feasibility
- a robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

The useful claim is narrower than robustness: under the current diagnostic
model, no tested positive base-z perturbation from `+0.05 mm` through `+1.0 mm`
has both a passing start contact and a passing terminal target. The negative
side has recoverable pockets, but `-0.75 mm` exposes a path-optimization
failure and `-1.0 mm` still needs the `16.0 s` Stage A margin.

## Next Step

Stop treating positive base-z recovery as a mere Stage A timing issue. The next
branch should investigate the positive-side contact-model/start-contact
definition: why `+0.05 mm` already loses the start contact and pushes terminal
orientation over the diagnostic gate. The separate `-0.75 mm` path anomaly is
also worth a path-seeding or knot-continuity audit, but it does not unblock the
`+1 mm` sensitivity failure.
