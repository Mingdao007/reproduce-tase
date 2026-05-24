# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/timing_sweep/paper_time_scale_0p006`

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
| `e1-cycloid` | `True` | `none` | `0.0008419471656173583` | `3.0694440449498293e-07` | `0.11948583686076865` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007653276857842162` | `4.926176050580663e-05` | `0.11953415992450067` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0008421266450678332` | `3.253151899910401e-05` | `0.11948583087559193` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0008417603548377617` | `3.069458840987417e-07` | `0.11948585618607141` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
