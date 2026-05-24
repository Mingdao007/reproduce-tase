# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/linear_kp0_normal1/delta_0p050mm`

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
| `e1-cycloid` | `True` | `none` | `3.2911511277031736e-05` | `2.722405773484633e-09` | `0.08381850784863316` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.001770776274717636` | `8.620440467902947e-07` | `0.08440159625182213` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `3.2908741857093914e-05` | `4.50784319834239e-08` | `0.08381851363975665` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.290945666948098e-05` | `2.7222528372131127e-09` | `0.08381883449807685` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
