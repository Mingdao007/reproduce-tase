# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/linear_kp0_normal1/delta_0p750mm`

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
| `e1-cycloid` | `True` | `none` | `4.7307035530281814e-05` | `4.730195088274888e-09` | `0.11002343454497882` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0012881217631867514` | `7.287530548687153e-07` | `0.11071000688096547` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `4.730383600774601e-05` | `4.5243735654043316e-08` | `0.1100234100260343` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `4.730614405989542e-05` | `4.73001291519809e-09` | `0.11002381787270024` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
