# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stitched_stage_a_handoff_timing_margin/20260524T162005/cases/qdot012_stage_a_18p0_recovery`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `18.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.1194386251900526`
- Stage A qdot saturation fraction: `0.0077777777777777776`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `2.9518820398761747e-05` | `1.861383876553019e-08` | `0.07241130795799401` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.003460893452988381` | `1.212220768302331e-06` | `0.0731453878884208` | `0.002` | `1.0` |
| `e3-circle` | `True` | `none` | `2.950975921846677e-05` | `6.28103669350004e-08` | `0.07241138231384438` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `2.9512246949807698e-05` | `1.8613358680752423e-08` | `0.07241185573280741` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
