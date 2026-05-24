# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/qdot012_stage_a_margin/20260524T194817/cases/stage_a_18p02s`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `False`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `18.02`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.12`
- Stage A qdot saturation fraction: `0.00776914539400666`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `1.8361406829674464e-05` | `1.9952336430037565e-07` | `0.0893317469336974` | `0.004` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007449692392259388` | `5.080641178120853e-07` | `0.0896809372713314` | `0.004` | `1.0` |
| `e3-circle` | `True` | `none` | `1.816995368857377e-05` | `2.0176439009956953e-07` | `0.08933174693377226` | `0.004` | `1.0` |
| `e4-cardioid` | `True` | `none` | `1.851368596456293e-05` | `1.9952312250645643e-07` | `0.0893317469336974` | `0.004` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
