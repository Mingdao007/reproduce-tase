# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_stitched_sensitivity/20260524T193845/scenarios/stage_a_14p5s/cases/delta_p0p500mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `14.5`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.11611805813694963`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `4.075872428417337e-05` | `4.319712521513223e-09` | `0.10056390291216237` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.000656466576185748` | `5.223253046544641e-07` | `0.10099329829600373` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `4.075780259046535e-05` | `3.030646068193738e-08` | `0.10056388920819218` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `4.0758576632811126e-05` | `4.3196321693195205e-09` | `0.10056406286429907` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
