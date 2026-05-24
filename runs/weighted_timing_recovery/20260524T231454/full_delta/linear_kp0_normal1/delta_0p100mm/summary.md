# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/linear_kp0_normal1/delta_0p100mm`

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
| `e1-cycloid` | `True` | `none` | `3.36132259143751e-05` | `2.778624089051072e-09` | `0.08565343963786981` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0017399828996955647` | `8.541044000958523e-07` | `0.08624250943608604` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `3.361046387067024e-05` | `4.508186345081266e-08` | `0.08565344032346377` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.361120502908044e-05` | `2.77847101749773e-09` | `0.08565376960963392` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
