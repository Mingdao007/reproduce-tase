# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/timing_boundary_plus1mm/planar_normal30_kp0p001/paper_time_scale_0p0052`

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
| `e1-cycloid` | `True` | `none` | `0.014048522414211293` | `2.4124193980579115e-06` | `0.11948545227775914` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.12813122685892228` | `6.735686812339685e-06` | `0.11974121946548555` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.014030132849506067` | `2.4116503020907156e-06` | `0.11948545227449062` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.014084244536813052` | `2.4143576777069593e-06` | `0.11948545227775914` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
