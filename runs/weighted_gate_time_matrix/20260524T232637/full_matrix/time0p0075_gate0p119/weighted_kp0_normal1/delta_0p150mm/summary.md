# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_gate_time_matrix/20260524T232637/full_matrix/time0p0075_gate0p119/weighted_kp0_normal1/delta_0p150mm`

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
| `e1-cycloid` | `True` | `none` | `0.0006603427653510252` | `2.0014318912785477e-07` | `0.0874947358025105` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0006031509262816126` | `6.074305491269114e-05` | `0.08755183084576973` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0006603342600508499` | `4.067907737397648e-05` | `0.08749470861221263` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0006603421286590327` | `2.2391109313812293e-07` | `0.08749476459674635` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
