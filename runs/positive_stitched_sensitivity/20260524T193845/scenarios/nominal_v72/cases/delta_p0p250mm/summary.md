# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_stitched_sensitivity/20260524T193845/scenarios/nominal_v72/cases/delta_p0p250mm`

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
| `e1-cycloid` | `True` | `none` | `3.5938505009918134e-05` | `2.947279649307421e-09` | `0.09120016063181398` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007322094730452777` | `5.532845424026685e-07` | `0.0916056636457473` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `3.593778591868713e-05` | `3.0141877204798356e-08` | `0.09120015457030327` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.593807068334343e-05` | `2.9472114445108777e-09` | `0.09120031200628362` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
