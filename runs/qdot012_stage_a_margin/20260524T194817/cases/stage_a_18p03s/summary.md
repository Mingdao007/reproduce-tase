# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/qdot012_stage_a_margin/20260524T194817/cases/stage_a_18p03s`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `False`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `18.03`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.12`
- Stage A qdot saturation fraction: `0.007875762617859123`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `3.512296364588163e-05` | `2.2767699781549713e-09` | `0.08934281571420387` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007465689650082252` | `5.567013988641912e-07` | `0.08974346690040184` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `3.5121882058946064e-05` | `3.0084404521447925e-08` | `0.08934281571603131` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.5122815411292585e-05` | `2.2768381936766335e-09` | `0.08934281571420387` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
