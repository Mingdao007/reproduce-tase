# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stage_b_priority_recovery/20260524T224404/scenarios/linear_kp0p003_posture0p001`

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
| `e1-cycloid` | `True` | `none` | `5.6702008834750294e-05` | `3.994387315931662e-09` | `0.11948782591732791` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `max_orientation_error_rad` | `0.0004862322920638773` | `4.451156403811503e-07` | `0.11997869470710999` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `5.670089027220104e-05` | `3.0240969544120174e-08` | `0.11948780401175653` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `5.670180019373916e-05` | `3.99447336579123e-09` | `0.11948800901781585` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
