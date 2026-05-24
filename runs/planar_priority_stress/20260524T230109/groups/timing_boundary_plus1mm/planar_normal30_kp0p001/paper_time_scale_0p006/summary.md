# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/timing_boundary_plus1mm/planar_normal30_kp0p001/paper_time_scale_0p006`

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
| `e1-cycloid` | `True` | `none` | `0.014048526252209727` | `2.4124195662637182e-06` | `0.11948545227775914` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.1520181757160038` | `7.290312256038369e-06` | `0.11977977026750646` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.014024036285654734` | `2.411395219119225e-06` | `0.1194854522734086` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.01409609050352476` | `2.414999886990975e-06` | `0.11948545227775914` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
