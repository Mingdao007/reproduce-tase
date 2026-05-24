# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/planar_normal30_kp0p002/delta_0p750mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.10367805178971796`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.03514970587736581` | `3.76236993563446e-06` | `0.11002132316210124` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.22045774099898488` | `8.765210729745804e-06` | `0.11032227907958207` | `0.13` | `1.0` |
| `e3-circle` | `True` | `none` | `0.03508330359610378` | `3.760517332974367e-06` | `0.11002132315864833` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.035241149347905384` | `3.765448982750477e-06` | `0.11002132316210124` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
