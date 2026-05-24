# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_planar_priority_matrix/20260524T225138/scenarios/planar_normal30_kp0p002/delta_0p050mm`

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
| `e1-cycloid` | `True` | `none` | `0.011442876021358694` | `2.2456058241093554e-06` | `0.08381735922558041` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0658051040988823` | `5.136409236741556e-06` | `0.08409199042866077` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.01142923966674564` | `2.244957816786246e-06` | `0.08381735922660309` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.011462195545898148` | `2.2467974128796697e-06` | `0.08381735922558041` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
