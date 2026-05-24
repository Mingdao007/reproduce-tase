# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/timing_boundary_plus1mm/planar_normal30_kp0p001/paper_time_scale_0p0065`

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
| `e1-cycloid` | `True` | `none` | `0.01404852923700575` | `2.4124196970691066e-06` | `0.11948545227775914` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.16753608433284334` | `7.626151045435333e-06` | `0.11980310843603297` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.014019782122926303` | `2.411217189544199e-06` | `0.11948545227265396` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.014104355561142264` | `2.415447808147738e-06` | `0.11948545227775914` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
