# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stage_a_base_z_bracket/20260524T165411/cases/delta_m0p500mm/stitched_15p0s`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14625580232403276`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `2.6908092283295382e-05` | `2.117782344207352e-09` | `0.06415913169955956` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.003686661891195886` | `1.247133849755196e-06` | `0.06486225548451124` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `2.68988951495297e-05` | `6.003392647799916e-08` | `0.06415926012285483` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `2.6900930834710123e-05` | `2.117611339752523e-09` | `0.06415965742433549` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
