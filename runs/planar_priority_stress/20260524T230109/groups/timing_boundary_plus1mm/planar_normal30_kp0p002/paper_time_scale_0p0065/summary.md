# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/timing_boundary_plus1mm/planar_normal30_kp0p002/paper_time_scale_0p0065`

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
| `e1-cycloid` | `True` | `none` | `0.05196453597626123` | `4.45961748700837e-06` | `0.1194852328478791` | `0.001` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.2406656371386823` | `9.045182512378194e-06` | `0.11968045791521362` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.05191647013238889` | `4.458458317998906e-06` | `0.11948523284582836` | `0.001` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.05205122323289654` | `4.461980745890625e-06` | `0.1194852328478791` | `0.001` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
