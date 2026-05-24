# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p750mm/stitched_15p0s`

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
| `e1-cycloid` | `True` | `none` | `4.730703629241884e-05` | `4.730195089764649e-09` | `0.11002343467596933` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.009200389724337055` | `1.984022215106407e-06` | `0.11091835714279596` | `0.825` | `1.0` |
| `e3-circle` | `True` | `none` | `4.7297991283938856e-05` | `6.018026022530688e-08` | `0.11002340682047726` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `4.7303623011250016e-05` | `4.729871219515125e-09` | `0.11002411608826458` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
