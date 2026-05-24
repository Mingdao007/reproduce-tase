# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/qdot012_stage_a_margin/20260524T194817/cases/stage_a_18p04s`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `18.04`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.11993578590413784`
- Stage A qdot saturation fraction: `0.00787139689578714`

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
