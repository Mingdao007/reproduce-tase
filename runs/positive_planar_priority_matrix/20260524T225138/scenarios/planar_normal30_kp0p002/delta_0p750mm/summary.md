# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_planar_priority_matrix/20260524T225138/scenarios/planar_normal30_kp0p002/delta_0p750mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.10367805178971796`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.03514968780828956` | `3.762369442776842e-06` | `0.11002132316210124` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.14519444906619758` | `7.240400767736994e-06` | `0.1102147893358667` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.03511949671726368` | `3.7616009547048042e-06` | `0.11002132316056462` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.03519032461011778` | `3.763738196021181e-06` | `0.11002132316210124` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
