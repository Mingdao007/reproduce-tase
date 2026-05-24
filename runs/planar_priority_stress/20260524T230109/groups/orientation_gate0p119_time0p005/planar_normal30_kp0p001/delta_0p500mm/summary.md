# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/orientation_gate0p119_time0p005/planar_normal30_kp0p001/delta_0p500mm`

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
| `e1-cycloid` | `True` | `none` | `0.006012954008295997` | `1.6291439048962917e-06` | `0.10056237375954319` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.06861180342809926` | `5.15649215847018e-06` | `0.10086123577833858` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.005999622282799501` | `1.6282355904392483e-06` | `0.10056237376423345` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.006030590704245875` | `1.6306555436166467e-06` | `0.10056237375954319` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
