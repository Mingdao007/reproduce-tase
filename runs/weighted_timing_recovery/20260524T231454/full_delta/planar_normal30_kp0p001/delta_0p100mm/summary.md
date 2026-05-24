# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/planar_normal30_kp0p001/delta_0p100mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14206784149212412`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.0031296614114859843` | `1.1905855028748552e-06` | `0.08565238215222191` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `tail_max_qdot_utilization` | `0.08145273181501882` | `5.646106319562936e-06` | `0.08610724680672958` | `0.003` | `1.0` |
| `e3-circle` | `True` | `none` | `0.003111232259906447` | `1.1891308118713494e-06` | `0.08565238216004585` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0031541895874540728` | `1.1935388076001304e-06` | `0.08565238215222191` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
