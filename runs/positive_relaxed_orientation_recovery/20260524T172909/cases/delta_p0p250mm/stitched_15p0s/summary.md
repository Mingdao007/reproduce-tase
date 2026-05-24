# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p250mm/stitched_15p0s`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.11996410618909473`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `3.5938502954699915e-05` | `2.9472796516057438e-09` | `0.0912001608081172` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `tail_max_qdot_utilization` | `0.0030095675542515686` | `1.1173443466622813e-06` | `0.09201059129093692` | `0.006` | `1.0` |
| `e3-circle` | `True` | `none` | `3.5930046088381575e-05` | `6.006722338217966e-08` | `0.09120014867997103` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.593279383924397e-05` | `2.9470068269379923e-09` | `0.09120076619996503` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
