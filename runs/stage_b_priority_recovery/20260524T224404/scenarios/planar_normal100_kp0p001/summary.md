# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stage_b_priority_recovery/20260524T224404/scenarios/planar_normal100_kp0p001`

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
| `e1-cycloid` | `True` | `none` | `0.00014387356048829682` | `2.6472125215204325e-07` | `0.11948747054118133` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad` | `0.009768843872853603` | `1.5165665016434015e-06` | `0.11995127502040462` | `0.188` | `1.0` |
| `e3-circle` | `True` | `none` | `0.00014345988275243026` | `2.662056045291732e-07` | `0.11948747082161118` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.00014462901900668345` | `2.651439979465418e-07` | `0.1194874705899453` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
