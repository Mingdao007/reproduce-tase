# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p150mm/stitched_15p0s`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.1421152405391769`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `3.434973074655456e-05` | `2.8348728075086892e-09` | `0.08749554383711862` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.010580673031376926` | `1.8971875248580711e-06` | `0.08827285798416469` | `0.541` | `1.0` |
| `e3-circle` | `True` | `none` | `3.4341169747493794e-05` | `6.006192773104121e-08` | `0.08749553740777573` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.434379467615045e-05` | `2.8346004926974033e-09` | `0.08749613648737793` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
