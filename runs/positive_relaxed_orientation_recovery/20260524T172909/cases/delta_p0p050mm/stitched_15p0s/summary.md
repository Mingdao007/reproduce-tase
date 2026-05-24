# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p050mm/stitched_15p0s`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.1419870794067211`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `3.291151038923967e-05` | `2.722405780662743e-09` | `0.0838185079603628` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.010775134389222191` | `1.8856307770199048e-06` | `0.08458026026618173` | `0.51` | `1.0` |
| `e3-circle` | `True` | `none` | `3.29028505021034e-05` | `6.005715777325849e-08` | `0.08381851820103116` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.2905364113413605e-05` | `2.7221338594687894e-09` | `0.0838190886190053` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
