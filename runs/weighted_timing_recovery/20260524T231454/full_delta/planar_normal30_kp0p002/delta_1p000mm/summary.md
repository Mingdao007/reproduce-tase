# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/planar_normal30_kp0p002/delta_1p000mm`

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
| `e1-cycloid` | `True` | `none` | `0.05196454675268662` | `4.459617721349568e-06` | `0.1194852328478791` | `0.001` | `1.0` |
| `e2-figure-eight` | `False` | `tail_mean_abs_force_error_N` | `0.275874931458737` | `9.637538484994748e-06` | `0.11972166555008389` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.05190042316760454` | `4.4580710234783815e-06` | `0.11948523284514975` | `0.001` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.052079783329288226` | `4.462763309362982e-06` | `0.1194852328478791` | `0.001` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
