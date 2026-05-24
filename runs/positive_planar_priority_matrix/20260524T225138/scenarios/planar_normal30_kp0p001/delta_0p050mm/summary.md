# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_planar_priority_matrix/20260524T225138/scenarios/planar_normal30_kp0p001/delta_0p050mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.1419870794067211`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.002886745141381866` | `1.1447902565115834e-06` | `0.08381749370531044` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.04207915062507256` | `4.152687357770083e-06` | `0.08412748751352093` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.002879001018636669` | `1.144179459074772e-06` | `0.08381749370831915` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.002897019643075951` | `1.1460813773341715e-06` | `0.08381749370531044` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
