# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/weighted_kp0_normal30/delta_0p200mm`

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
| `e1-cycloid` | `True` | `none` | `0.0006818996513860842` | `2.0444683634992206e-07` | `0.08934370954384353` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0006255133032998606` | `6.079063990311016e-05` | `0.08940089143213763` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0006818922916079906` | `4.0678033145180244e-05` | `0.08934368228225227` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0006818990452930551` | `2.2804935793439622e-07` | `0.08934373837963218` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
