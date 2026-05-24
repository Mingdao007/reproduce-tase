# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_timing_boundary/20260524T200236/cases/paper_time_scale_0p0065`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.10018584837167505`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `5.669959741116504e-05` | `5.140973795890907e-09` | `0.11948787565733601` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `max_orientation_error_rad` | `0.000819317068647094` | `5.878563461081095e-07` | `0.1201260838562` | `0.008` | `1.0` |
| `e3-circle` | `True` | `none` | `5.669757904328776e-05` | `3.9333582575558834e-08` | `0.11948784770464425` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `5.669940785558047e-05` | `5.140835743211447e-09` | `0.11948818443257977` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
