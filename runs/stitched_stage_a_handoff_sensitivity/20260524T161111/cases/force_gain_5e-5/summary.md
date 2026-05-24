# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stitched_stage_a_handoff_sensitivity/20260524T161111/cases/force_gain_5e-5`

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
| `e1-cycloid` | `True` | `none` | `7.3785615082000434e-06` | `1.605539250506407e-08` | `0.07241117393872581` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.013843278429059795` | `1.19963375395386e-06` | `0.07313492778035031` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `7.343978005938112e-06` | `6.209144426178227e-08` | `0.0724112482784928` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `7.350733936402065e-06` | `1.6054614790372845e-08` | `0.07241172161166783` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
