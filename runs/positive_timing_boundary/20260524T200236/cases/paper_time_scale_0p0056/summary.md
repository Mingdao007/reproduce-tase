# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_timing_boundary/20260524T200236/cases/paper_time_scale_0p0056`

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
| `e1-cycloid` | `True` | `none` | `5.669959813717096e-05` | `5.140973795202917e-09` | `0.11948787563328164` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `max_orientation_error_rad` | `0.000609145089495522` | `5.025763964147301e-07` | `0.12003776159897517` | `0.006` | `1.0` |
| `e3-circle` | `True` | `none` | `5.669828889189432e-05` | `3.3987759651701696e-08` | `0.11948785012080178` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `5.669957876901943e-05` | `5.140871325859386e-09` | `0.11948810482826874` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
