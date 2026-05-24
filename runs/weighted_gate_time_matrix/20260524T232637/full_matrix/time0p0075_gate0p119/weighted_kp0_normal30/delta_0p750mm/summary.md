# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_gate_time_matrix/20260524T232637/full_matrix/time0p0075_gate0p119/weighted_kp0_normal30/delta_0p750mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.10367805178971796`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.0009911909058976187` | `2.674718781159268e-07` | `0.11002194423627122` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007414939256771814` | `6.130383120481383e-05` | `0.11008068830491685` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.000991190520105003` | `4.066793614028803e-05` | `0.11002191591890591` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.000991190630951344` | `2.8953777843763707e-07` | `0.11002197386491006` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
