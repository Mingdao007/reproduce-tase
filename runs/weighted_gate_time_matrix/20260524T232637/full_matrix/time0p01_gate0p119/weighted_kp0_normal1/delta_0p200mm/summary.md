# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_gate_time_matrix/20260524T232637/full_matrix/time0p01_gate0p119/weighted_kp0_normal1/delta_0p200mm`

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
| `e1-cycloid` | `True` | `none` | `0.0006818996514241693` | `2.044472960928352e-07` | `0.08934370955314273` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0005719631821970905` | `8.107527600566414e-05` | `0.08942004927709385` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.000681886476128879` | `5.423709328920094e-05` | `0.0893436630030844` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0006818985369666164` | `2.520159764763218e-07` | `0.08934376081269145` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
