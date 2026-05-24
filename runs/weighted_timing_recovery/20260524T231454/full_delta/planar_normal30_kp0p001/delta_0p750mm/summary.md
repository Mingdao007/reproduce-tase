# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/planar_normal30_kp0p001/delta_0p750mm`

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
| `e1-cycloid` | `True` | `none` | `0.009145796587832718` | `1.983502400453564e-06` | `0.11002151899410738` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.1607079708293093` | `7.527332641488597e-06` | `0.11041305737921629` | `0.143` | `1.0` |
| `e3-circle` | `True` | `none` | `0.009118702381159624` | `1.98224040973546e-06` | `0.11002151898511872` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.009200127096432689` | `1.9872216705761635e-06` | `0.11002151899410738` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
