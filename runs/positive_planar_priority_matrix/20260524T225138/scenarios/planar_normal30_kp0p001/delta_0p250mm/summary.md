# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_planar_priority_matrix/20260524T225138/scenarios/planar_normal30_kp0p001/delta_0p250mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.11996410618909473`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.0039907973184406306` | `1.3390503195258623e-06` | `0.0911989613750957` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.05192121718053611` | `4.563004319242272e-06` | `0.09150667512837204` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.003980659455380313` | `1.338265673364752e-06` | `0.09119896137948535` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.004003803530832921` | `1.3404324772040707e-06` | `0.0911989613750957` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
