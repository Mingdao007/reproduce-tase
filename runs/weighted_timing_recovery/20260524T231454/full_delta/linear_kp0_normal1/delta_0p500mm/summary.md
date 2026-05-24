# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/linear_kp0_normal1/delta_0p500mm`

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
| `e1-cycloid` | `True` | `none` | `4.0758724279084114e-05` | `4.3197125211708574e-09` | `0.10056390297530858` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.001473599880542089` | `7.824943763867202e-07` | `0.10120806136325323` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `4.075546688454335e-05` | `4.5202418170623224e-08` | `0.10056388368761979` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `4.0757561872935e-05` | `4.319531734034432e-09` | `0.10056426283653497` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
