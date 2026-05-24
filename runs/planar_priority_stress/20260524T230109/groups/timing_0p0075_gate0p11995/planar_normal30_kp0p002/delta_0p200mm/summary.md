# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/timing_0p0075_gate0p11995/planar_normal30_kp0p002/delta_0p200mm`

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
| `e1-cycloid` | `True` | `none` | `0.014546659753286471` | `2.515499042821649e-06` | `0.08934325925156714` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.13526588741098888` | `7.024053167643999e-06` | `0.0897266919070735` | `0.231` | `1.0` |
| `e3-circle` | `True` | `none` | `0.014510427568955748` | `2.513911234594534e-06` | `0.08934325925485942` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.01459781363548033` | `2.518274716378952e-06` | `0.08934325925156714` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
