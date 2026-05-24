# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_stitched_sensitivity/20260524T193845/scenarios/orientation_gate_0p119/cases/delta_p0p100mm`

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
| `e1-cycloid` | `True` | `none` | `3.3613225513167146e-05` | `2.7786240875833686e-09` | `0.0856534395799172` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007746585656834082` | `5.695200944876192e-07` | `0.08604620949512072` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `3.3612535002518486e-05` | `3.012585037987589e-08` | `0.08565343989810298` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.361276557747761e-05` | `2.7785560770612894e-09` | `0.08565358624681357` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
