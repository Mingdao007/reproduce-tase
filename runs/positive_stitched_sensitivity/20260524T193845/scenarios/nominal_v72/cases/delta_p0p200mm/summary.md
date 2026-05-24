# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_stitched_sensitivity/20260524T193845/scenarios/nominal_v72/cases/delta_p0p200mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14424277184739456`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `3.512380168251284e-05` | `2.8911074990475387e-09` | `0.08934455593133465` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007466282486472631` | `5.585740178871728e-07` | `0.08974563803371456` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `3.51230968102012e-05` | `3.013643558471786e-08` | `0.08934455184958484` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.512336102643676e-05` | `2.8910393749109753e-09` | `0.08934470568841647` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
