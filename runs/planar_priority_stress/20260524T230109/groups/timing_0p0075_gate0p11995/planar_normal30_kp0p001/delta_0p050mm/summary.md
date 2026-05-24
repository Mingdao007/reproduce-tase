# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/timing_0p0075_gate0p11995/planar_normal30_kp0p001/delta_0p050mm`

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
| `e1-cycloid` | `True` | `none` | `0.0028867503457914666` | `1.1447907769478185e-06` | `0.08381749370531044` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `tail_max_qdot_utilization` | `0.07771952673139332` | `5.5311511768570106e-06` | `0.08427301402372706` | `0.003` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0028696118750842505` | `1.1434486461625086e-06` | `0.08381749371206577` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0029098899518415554` | `1.1476953351453224e-06` | `0.08381749370531044` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
