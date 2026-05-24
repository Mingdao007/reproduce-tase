# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/timing_0p0075_gate0p11995/planar_normal30_kp0p001/delta_0p200mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14424277184739456`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.003679621763005909` | `1.2876248967978985e-06` | `0.08934340603499012` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `tail_max_qdot_utilization` | `0.08961867494459198` | `5.886494562460963e-06` | `0.08979608301951979` | `0.003` | `1.0` |
| `e3-circle` | `True` | `none` | `0.003658524349907397` | `1.2859745033030648e-06` | `0.08934340604434636` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0037072164443516663` | `1.2906805525103282e-06` | `0.08934340603499012` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
