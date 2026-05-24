# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/orientation_gate0p119_time0p005/planar_normal30_kp0p002/delta_0p100mm`

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
| `e1-cycloid` | `True` | `none` | `0.01239588607140672` | `2.33252736450094e-06` | `0.0856522436299176` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.06953852895642919` | `5.264323774414021e-06` | `0.08592425000269677` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.012381425722311273` | `2.331856804618238e-06` | `0.08565224363111276` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.012416280106938174` | `2.333732992647678e-06` | `0.0856522436299176` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
