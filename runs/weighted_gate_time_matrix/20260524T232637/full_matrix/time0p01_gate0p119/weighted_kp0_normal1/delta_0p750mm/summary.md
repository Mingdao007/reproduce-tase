# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_gate_time_matrix/20260524T232637/full_matrix/time0p01_gate0p119/weighted_kp0_normal1/delta_0p750mm`

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
| `e1-cycloid` | `True` | `none` | `0.000991190904368784` | `2.6747187932584805e-07` | `0.11002194424582099` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.000712601036519449` | `8.167334092437876e-05` | `0.11010029061375315` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0009911901707909587` | `5.4223430208369226e-05` | `0.1100218940344795` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0009911903769686693` | `3.1371257074915546e-07` | `0.11002199691477109` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
