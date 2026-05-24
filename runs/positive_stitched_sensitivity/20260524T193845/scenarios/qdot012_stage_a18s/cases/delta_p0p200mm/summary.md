# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_stitched_sensitivity/20260524T193845/scenarios/qdot012_stage_a18s/cases/delta_p0p200mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `False`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `18.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.12`
- Stage A qdot saturation fraction: `0.0077777777777777776`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `1.9170642950889772e-05` | `5.558902001207658e-07` | `0.0893110103933015` | `0.008` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007419587859130061` | `5.201745384946615e-07` | `0.08955538795286133` | `0.009` | `1.0` |
| `e3-circle` | `True` | `none` | `1.9156964186959336e-05` | `5.566933692575228e-07` | `0.08931101039337638` | `0.008` | `1.0` |
| `e4-cardioid` | `True` | `none` | `1.9183063025174363e-05` | `5.558873770131895e-07` | `0.0893110103933015` | `0.008` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
