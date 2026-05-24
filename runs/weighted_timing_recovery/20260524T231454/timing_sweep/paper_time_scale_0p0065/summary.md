# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/timing_sweep/paper_time_scale_0p0065`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.10018584837167505`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.0008419471534720824` | `3.0694440375271223e-07` | `0.11948583686175358` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007381564171879917` | `5.333957439022009e-05` | `0.11953815417606216` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0008421577981090867` | `3.524233505003547e-05` | `0.11948583087538597` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.000841727919433315` | `3.0694614151262356e-07` | `0.11948585954178399` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
