# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_gate_time_matrix/20260524T232637/full_matrix/time0p01_gate0p119/weighted_kp0_normal1/delta_0p250mm`

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
| `e1-cycloid` | `True` | `none` | `0.000704446912248411` | `2.089552890834741e-07` | `0.09119927392881623` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0005965470384528438` | `8.113775922621016e-05` | `0.09127573856281337` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0007044356047632627` | `5.423571400148992e-05` | `0.09119922706182647` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0007044458530377895` | `2.5638593220791757e-07` | `0.09119932526834863` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
