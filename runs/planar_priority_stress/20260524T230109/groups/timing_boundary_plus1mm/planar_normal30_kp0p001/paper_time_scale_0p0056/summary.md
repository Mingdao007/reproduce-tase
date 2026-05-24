# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/timing_boundary_plus1mm/planar_normal30_kp0p001/paper_time_scale_0p0056`

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
| `e1-cycloid` | `True` | `none` | `0.014048524196022703` | `2.4124194761482053e-06` | `0.11948545227775914` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.1399232690649097` | `7.015754772741531e-06` | `0.11976068917934418` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.014027193760289406` | `2.411527336350398e-06` | `0.1194854522739689` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.014089955569826293` | `2.4146673245654606e-06` | `0.11948545227775914` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
