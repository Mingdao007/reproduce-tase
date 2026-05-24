# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/weighted_kp0_normal30/delta_0p500mm`

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
| `e1-cycloid` | `True` | `none` | `0.0008333969854379797` | `2.3492944084980108e-07` | `0.10056273704830987` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007805027935618858` | `6.10798819840664e-05` | `0.10062061091375274` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0008333945451549818` | `4.067218833299267e-05` | `0.10056270929429541` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0008333965767971874` | `2.576615036467709e-07` | `0.10056276621985454` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
