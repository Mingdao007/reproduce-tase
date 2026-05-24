# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stitched_stage_a_handoff_timing_margin/20260524T162005/cases/paper_time_scale_0p012_recovery`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14332635022814824`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `2.9518821021912166e-05` | `1.861383876844748e-08` | `0.07241130809063519` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.004977812422968393` | `1.453794801989588e-06` | `0.07329179294859031` | `0.002` | `1.0` |
| `e3-circle` | `True` | `none` | `2.9499856374664013e-05` | `7.435425478722023e-08` | `0.07241141509956696` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `2.950538290924065e-05` | `1.861314739143305e-08` | `0.07241209682920849` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
