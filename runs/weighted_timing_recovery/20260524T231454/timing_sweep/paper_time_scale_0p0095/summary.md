# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/timing_sweep/paper_time_scale_0p0095`

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
| `e1-cycloid` | `True` | `none` | `0.0008419470304537491` | `3.069444040858592e-07` | `0.11948583687153953` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007834322084013489` | `7.785353426523945e-05` | `0.11956229681499174` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0008423970715720941` | `5.150738032154213e-05` | `0.11948583087380703` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0008414788596251066` | `3.1428690111625053e-07` | `0.11948588531365549` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
