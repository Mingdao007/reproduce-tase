# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_full_stitched_recovery/20260524T195501/cases/delta_p0p750mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `18.035`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.08623070567481625`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `4.730703616113718e-05` | `4.73019508609837e-09` | `0.11002343447771253` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.000580186041220081` | `4.87328753716922e-07` | `0.11048096113317912` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `4.7306096024843924e-05` | `3.036769008415607e-08` | `0.11002341568611611` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `4.730696636110476e-05` | `4.730114125904572e-09` | `0.11002360486022282` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
