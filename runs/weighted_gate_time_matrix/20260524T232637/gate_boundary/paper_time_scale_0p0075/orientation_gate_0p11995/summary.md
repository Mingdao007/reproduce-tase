# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_gate_time_matrix/20260524T232637/gate_boundary/paper_time_scale_0p0075/orientation_gate_0p11995`

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
| `e1-cycloid` | `True` | `none` | `0.0008419471222529707` | `3.069444040301147e-07` | `0.11948583686422706` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0008094383419582085` | `6.156641559731311e-05` | `0.11954627160547111` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0008422275835027282` | `4.066399426577663e-05` | `0.1194858308749259` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0008416552676152867` | `3.0694671715372084e-07` | `0.11948586705858555` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
