# Positive Relaxed Orientation Recovery Report

## Summary

v70 tests the executable consequence of v69: whether the current contact-point
model can recover positive base-z terminal, path, and stitched feasibility when
the diagnostic terminal orientation envelope is explicitly relaxed to
`0.12 rad`.

The formal run is:

- `runs/positive_relaxed_orientation_recovery/20260524T172909`
- command: `scripts/audit_positive_relaxed_orientation_recovery.py`
- parent commit before v70 changes: `d8232b91a3c6e2a00c7e5a8432928f5ba3fc6d43`

The audit writes a run-local copy of the Stage A target config with
`max_terminal_orientation_error_rad: 0.12`; it does not modify the canonical
`configs/ur10e_adapted_stage_a_target.yaml`. The terminal solver still uses
the stricter `0.08 rad` orientation normalization and then evaluates candidates
against the relaxed `0.12 rad` gate.

## Metrics

From `runs/positive_relaxed_orientation_recovery/20260524T172909/metrics.yaml`:

- start pass count: `8 / 8`
- terminal pass count under `0.12 rad`: `8 / 8`
- path geometry pass count under `0.12 rad`: `8 / 8`
- stitched recovery count: `0`
- max positive terminal-pass delta: `+1.0 mm`
- max positive recovered delta: `none`

| delta mm | terminal orientation rad | path pass | path min duration s | Stage B pass at 15 s | Stage B pass at 16 s |
| ---: | ---: | --- | ---: | ---: | ---: |
| `+0.05` | `0.0838175590896232` | `true` | `14.198707940657611` | `3 / 4` | `3 / 4` |
| `+0.10` | `0.08565245135290023` | `true` | `14.206784149197896` | `3 / 4` | `3 / 4` |
| `+0.15` | `0.0874945141256073` | `true` | `14.211524053903112` | `3 / 4` | `3 / 4` |
| `+0.20` | `0.08934348318237911` | `true` | `14.424277184724716` | `3 / 4` | `3 / 4` |
| `+0.25` | `0.09119904265401833` | `true` | `11.996410618897185` | `3 / 4` | `3 / 4` |
| `+0.50` | `0.10056247728510045` | `true` | `11.224745619891337` | `3 / 4` | `3 / 4` |
| `+0.75` | `0.11002164736335575` | `true` | `10.367805178961204` | `3 / 4` | `3 / 4` |
| `+1.00` | `0.11948560786548146` | `true` | `10.018584837157274` | `3 / 4` | `3 / 4` |

For sampled stitched rows, the failing Stage B trajectory is consistently
`e2-figure-eight`, with failed criteria `qdot_saturation_fraction` and
`tail_max_qdot_utilization`.

## Interpretation

The `0.12 rad` diagnostic terminal orientation envelope is sufficient to
recover positive-side start, terminal, and offline path feasibility through
`+1.0 mm` in the current contact-point model. It is not sufficient to recover
the full stitched diagnostic Stage A plus Stage B claim, because the direct
handoff still fails E2 on qdot saturation.

The remaining positive-side blocker has moved from Stage A endpoint/path
feasibility to Stage B handoff timing/qdot margin under the relaxed terminal
orientation setup.

## Claim Boundary

This is diagnostic-label simulation evidence only. It is not:

- strict paper-equivalent feasibility
- robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

The relaxed `0.12 rad` target config is a run artifact, not a canonical config
change.

## Next Step

Combine the v70 relaxed terminal/path setup with a Stage B E2 timing or qdot
margin audit. Keep the `0.12 rad` diagnostic label explicit, and keep strict
paper-equivalent setup, v38 relaxed trajectory-after-setup, and v63-v70
diagnostic staged labels separate.
