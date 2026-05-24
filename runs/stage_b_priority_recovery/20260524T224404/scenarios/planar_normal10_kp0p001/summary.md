# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stage_b_priority_recovery/20260524T224404/scenarios/planar_normal10_kp0p001`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.10018584837167505`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.08908209716066544` | `5.26574599702416e-06` | `0.11948537885558683` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `tail_mean_abs_force_error_N` | `0.3544639543616428` | `1.0256611830077427e-05` | `0.11948537939100295` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.08903750729697041` | `5.264940228197991e-06` | `0.11948537885199313` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.08917310640736281` | `5.267613559969964e-06` | `0.11948537885558683` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
