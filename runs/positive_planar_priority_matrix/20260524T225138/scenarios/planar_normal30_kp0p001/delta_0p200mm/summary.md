# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_planar_priority_matrix/20260524T225138/scenarios/planar_normal30_kp0p001/delta_0p200mm`

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
| `e1-cycloid` | `True` | `none` | `0.003679615613127933` | `1.2876243537803108e-06` | `0.08934340603499012` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.04920581056799254` | `4.455193467496983e-06` | `0.0896520136255618` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.003670087782230538` | `1.2868760819218605e-06` | `0.0893434060391545` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0036918694876844514` | `1.2889826684859761e-06` | `0.08934340603499012` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
