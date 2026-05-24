# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/linear_kp0_normal1/delta_1p000mm`

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
| `e1-cycloid` | `True` | `none` | `5.6699596666884846e-05` | `5.140973796978911e-09` | `0.11948787569311954` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad` | `0.006603888075066666` | `1.7967958428040668e-06` | `0.12020305872871904` | `0.999` | `1.0` |
| `e3-circle` | `True` | `none` | `5.6696404176612704e-05` | `4.52883163875912e-08` | `0.11948784568213706` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `5.6699063554281894e-05` | `5.140789981206151e-09` | `0.11948828677032426` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
