# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_gate_time_matrix/20260524T232637/full_matrix/time0p0075_gate0p119/weighted_kp0_normal30/delta_0p250mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.11996410618909473`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.0007044469121450847` | `2.0895501421142036e-07` | `0.09119927391950348` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0006488066012492765` | `6.08384724070923e-05` | `0.09125654943196479` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0007044405976841483` | `4.0677007969594714e-05` | `0.09119924658433096` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.000704446339731315` | `2.3239985930148204e-07` | `0.0911993028002866` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
