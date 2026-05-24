# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_planar_priority_matrix/20260524T225138/scenarios/planar_normal30_kp0p002/delta_0p500mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.11224745619902818`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.0235407293234409` | `3.1436704004288776e-06` | `0.1005622008886894` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.10937518068803388` | `6.4167274732017666e-06` | `0.10079789673218484` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.02351930179638847` | `3.1429093409873334e-06` | `0.10056220089046773` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.02357212995717955` | `3.144985475387989e-06` | `0.1005622008886894` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
