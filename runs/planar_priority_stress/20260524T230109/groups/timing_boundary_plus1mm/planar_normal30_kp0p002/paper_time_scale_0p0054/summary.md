# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/timing_boundary_plus1mm/planar_normal30_kp0p002/paper_time_scale_0p0054`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.10018584837167505`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.051964527271203514` | `4.459617291056824e-06` | `0.1194852328478791` | `0.001` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.20339197931454436` | `8.36622575496634e-06` | `0.11963323452155597` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.05193129306778195` | `4.458818919252038e-06` | `0.11948523284646298` | `0.001` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.05202435789536255` | `4.461248667962832e-06` | `0.1194852328478791` | `0.001` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
