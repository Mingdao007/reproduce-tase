# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stitched_stage_a_handoff_sensitivity/20260524T161111/cases/paper_time_scale_0p02`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14332635022814824`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `2.9518821156750975e-05` | `1.8613838793254903e-08` | `0.0724113092341065` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.037200872609881336` | `3.940146505268642e-06` | `0.07383706545641958` | `0.833` | `1.0` |
| `e3-circle` | `True` | `none` | `2.9369368589722278e-05` | `1.2141309644311727e-07` | `0.07241160574147412` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `2.9416908280981423e-05` | `1.8611917547081694e-08` | `0.07241349952274446` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
