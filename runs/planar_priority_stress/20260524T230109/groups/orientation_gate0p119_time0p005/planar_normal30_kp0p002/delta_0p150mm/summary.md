# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/orientation_gate0p119_time0p005/planar_normal30_kp0p002/delta_0p150mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.1421152405391769`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.013428135794677644` | `2.422458610381732e-06` | `0.08749429838024252` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.07351555182402864` | `5.395872183672624e-06` | `0.08776333251291144` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0134128413920855` | `2.4217684077627207e-06` | `0.08749429838157946` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.01344966518332099` | `2.4236783443586443e-06` | `0.08749429838024252` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
