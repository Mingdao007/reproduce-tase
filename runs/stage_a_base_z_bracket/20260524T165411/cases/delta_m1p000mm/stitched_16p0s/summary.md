# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stage_a_base_z_bracket/20260524T165411/cases/delta_m1p000mm/stitched_16p0s`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `16.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14674004552188208`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `2.319874258660981e-05` | `1.5848303938839098e-09` | `0.047179607626229504` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.004105017150872387` | `1.3188644470283016e-06` | `0.04783154728957144` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `2.3188017475432867e-05` | `6.00169338539057e-08` | `0.04717989830396977` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `2.3191771048542975e-05` | `1.7878708933217555e-09` | `0.04718009452867578` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
