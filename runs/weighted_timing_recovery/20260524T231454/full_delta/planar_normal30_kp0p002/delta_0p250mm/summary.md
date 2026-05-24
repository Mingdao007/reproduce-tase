# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/planar_normal30_kp0p002/delta_0p250mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.11996410618909473`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.015759074236078908` | `2.611742413064289e-06` | `0.09119881037545309` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.14176642995009214` | `7.173785928662996e-06` | `0.09157731566302724` | `0.234` | `1.0` |
| `e3-circle` | `True` | `none` | `0.015720914019721012` | `2.610121896515046e-06` | `0.09119881037896857` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.015813076102501843` | `2.6145497448656924e-06` | `0.09119881037545309` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
