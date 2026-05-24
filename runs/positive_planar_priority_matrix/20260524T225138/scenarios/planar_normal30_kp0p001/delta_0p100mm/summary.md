# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_planar_priority_matrix/20260524T225138/scenarios/planar_normal30_kp0p001/delta_0p100mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14206784149212412`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.0031296559111026936` | `1.1905849751398916e-06` | `0.08565238215222191` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.044296372376843605` | `4.250106640554722e-06` | `0.08596210811967063` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0031213248445427586` | `1.1899233600041948e-06` | `0.08565238215570553` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0031405473416380135` | `1.1918977737912857e-06` | `0.08565238215222191` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
