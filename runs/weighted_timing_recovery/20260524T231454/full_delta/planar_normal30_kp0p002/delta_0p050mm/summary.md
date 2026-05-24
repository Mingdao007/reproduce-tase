# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/planar_normal30_kp0p002/delta_0p050mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.1419870794067211`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.011442885420934225` | `2.2456062867057973e-06` | `0.08381735922558041` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.1171631077222241` | `6.588040463409523e-06` | `0.08421322077190706` | `0.214` | `1.0` |
| `e3-circle` | `True` | `none` | `0.01141228064722633` | `2.244151892639387e-06` | `0.08381735922787908` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.011486369145117732` | `2.248286908413529e-06` | `0.08381735922558041` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
