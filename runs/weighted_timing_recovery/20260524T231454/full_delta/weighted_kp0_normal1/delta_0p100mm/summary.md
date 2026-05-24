# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/weighted_kp0_normal1/delta_0p100mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14206784149212412`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.0006397340166476306` | `1.9603490771100332e-07` | `0.08565266855351242` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0005815527112354202` | `6.075446192415983e-05` | `0.08570975751005047` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0006397242569734907` | `4.068014008413673e-05` | `0.0856526414324457` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0006397333381505233` | `2.1997530760718756e-07` | `0.08565269730932937` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
