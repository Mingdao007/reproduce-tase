# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_stitched_sensitivity/20260524T193845/scenarios/paper_time_scale_0p0075/cases/delta_p0p250mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.11996410618909473`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `3.593850373266427e-05` | `2.947279650715954e-09` | `0.0912001606916159` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.001644348608983055` | `8.290458017477336e-07` | `0.09180830757938373` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `3.59357684771977e-05` | `4.509257677270251e-08` | `0.09120015087818795` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.593659763581059e-05` | `2.947126194127736e-09` | `0.09120050125459178` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
