# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_timing_boundary/20260524T200236/cases/paper_time_scale_0p0052`

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
| `e1-cycloid` | `True` | `none` | `5.669959809103897e-05` | `5.140973795122876e-09` | `0.11948787562476806` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0005254797033216319` | `4.6704502234182257e-07` | `0.11999846384112321` | `0.006` | `1.0` |
| `e3-circle` | `True` | `none` | `5.669851811760829e-05` | `3.161769819889736e-08` | `0.11948785144053725` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `5.6699622878357834e-05` | `5.140885436967502e-09` | `0.1194880732496781` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
