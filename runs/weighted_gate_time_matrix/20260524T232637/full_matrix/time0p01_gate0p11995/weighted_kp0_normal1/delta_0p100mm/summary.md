# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_gate_time_matrix/20260524T232637/full_matrix/time0p01_gate0p11995/weighted_kp0_normal1/delta_0p100mm`

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
| `e1-cycloid` | `True` | `none` | `0.000639734016332496` | `1.9603601556236812e-07` | `0.08565266856278692` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0005251087344018934` | `8.095118010545803e-05` | `0.08572878466462444` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0006397165521656189` | `5.423992480529215e-05` | `0.08565262262614853` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0006397327773802441` | `2.439030430069658e-07` | `0.08565271968017263` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
