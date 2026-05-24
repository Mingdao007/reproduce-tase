# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/timing_sweep/paper_time_scale_0p009`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.10018584837167505`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.0008419470577913701` | `3.0694440338610155e-07` | `0.11948583686938469` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007908673750422501` | `7.378954891546828e-05` | `0.11955829106493644` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0008423509601625279` | `4.879652779341447e-05` | `0.11948583087411127` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0008415268488509664` | `3.0918646707398497e-07` | `0.11948588034720217` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
