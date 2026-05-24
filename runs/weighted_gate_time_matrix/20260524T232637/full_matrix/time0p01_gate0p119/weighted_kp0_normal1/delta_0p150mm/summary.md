# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_gate_time_matrix/20260524T232637/full_matrix/time0p01_gate0p119/weighted_kp0_normal1/delta_0p150mm`

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
| `e1-cycloid` | `True` | `none` | `0.0006603427662101114` | `2.0014391896835505e-07` | `0.0874947358117961` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.000548168589299114` | `8.101306768380041e-05` | `0.0875709596477439` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.000660327541454615` | `5.4238497122319605e-05` | `0.08749468957204844` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0006603415845955984` | `2.4785826050726885e-07` | `0.08749478699747962` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
