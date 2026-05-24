# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_timing_boundary/20260524T200236/cases/paper_time_scale_0p0054`

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
| `e1-cycloid` | `True` | `none` | `5.669959719785567e-05` | `5.1409737951606694e-09` | `0.11948787562885478` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `max_orientation_error_rad` | `0.0005665444643839868` | `4.848112491332548e-07` | `0.12001811086329595` | `0.006` | `1.0` |
| `e3-circle` | `True` | `none` | `5.669840898491429e-05` | `3.280218635801189e-08` | `0.1194878507571513` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `5.669960349994785e-05` | `5.140878505012492e-09` | `0.11948808874657667` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
