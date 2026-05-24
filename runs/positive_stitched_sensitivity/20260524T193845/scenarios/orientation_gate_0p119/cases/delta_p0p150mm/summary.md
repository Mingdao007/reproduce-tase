# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_stitched_sensitivity/20260524T193845/scenarios/orientation_gate_0p119/cases/delta_p0p150mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.1421152405391769`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `3.434972950258075e-05` | `2.8348728007308362e-09` | `0.08749554366453485` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007607652612832804` | `5.641204343504017e-07` | `0.0878924064819036` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `3.434902689116281e-05` | `3.013109141863684e-08` | `0.08749554175701985` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.4349278497214364e-05` | `2.834804735570018e-09` | `0.08749569185309268` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
