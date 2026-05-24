# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_timing_boundary/20260524T200236/cases/paper_time_scale_0p007`

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
| `e1-cycloid` | `True` | `none` | `5.669959704915684e-05` | `5.140973796519997e-09` | `0.11948787567395135` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad` | `0.006253034586287889` | `1.7529416759374159e-06` | `0.12015423656433318` | `0.999` | `1.0` |
| `e3-circle` | `True` | `none` | `5.669705135509684e-05` | `4.230937179074022e-08` | `0.1194878466205428` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `5.669925831606637e-05` | `5.140813678396194e-09` | `0.11948823377401543` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
