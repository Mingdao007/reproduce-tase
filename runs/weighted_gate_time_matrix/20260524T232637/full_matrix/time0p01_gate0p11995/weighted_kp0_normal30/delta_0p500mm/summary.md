# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_gate_time_matrix/20260524T232637/full_matrix/time0p01_gate0p11995/weighted_kp0_normal30/delta_0p500mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.11224745619902818`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.0008333969860971236` | `2.349294640508939e-07` | `0.10056273705771425` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007330140843433996` | `8.137332108234978e-05` | `0.1006398987314298` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0008333925888398141` | `5.4229210498650735e-05` | `0.100562688532793` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0008333962161270226` | `2.817441159700434e-07` | `0.1005627889141167` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
