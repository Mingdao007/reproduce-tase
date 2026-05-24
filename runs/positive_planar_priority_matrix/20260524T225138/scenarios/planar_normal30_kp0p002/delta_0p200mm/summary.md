# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_planar_priority_matrix/20260524T225138/scenarios/planar_normal30_kp0p002/delta_0p200mm`

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
| `e1-cycloid` | `True` | `none` | `0.014546648863019339` | `2.515498569955275e-06` | `0.08934325925156714` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.07775059752571094` | `5.531066736120481e-06` | `0.08960894307851132` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.01453050986890593` | `2.514791432052883e-06` | `0.08934325925303144` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.014569377400466906` | `2.516732424237729e-06` | `0.08934325925156714` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
