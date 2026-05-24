# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/weighted_kp0_normal1/delta_0p050mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.1419870794067211`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.0006200308758736561` | `1.9211184235517333e-07` | `0.08381777200528513` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0005609332554522517` | `6.0707412547732284e-05` | `0.08387478561016432` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0006200197528054563` | `4.068122074826851e-05` | `0.08381774495182587` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0006200301680576281` | `2.1623313591919048e-07` | `0.08381780072555196` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
