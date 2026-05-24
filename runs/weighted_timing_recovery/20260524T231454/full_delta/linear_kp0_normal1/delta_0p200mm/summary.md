# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/linear_kp0_normal1/delta_0p200mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14424277184739456`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `3.512380336164966e-05` | `2.891107500475012e-09` | `0.08934455599049643` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0016767741145377046` | `8.376098360624269e-07` | `0.08994614817444518` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `3.512106006052562e-05` | `4.5088938839782776e-08` | `0.08934454832343498` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.51218584142865e-05` | `2.8909541739674527e-09` | `0.08934489291464949` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
