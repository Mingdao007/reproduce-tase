# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_gate_time_matrix/20260524T232637/full_matrix/time0p01_gate0p11995/weighted_kp0_normal30/delta_0p050mm`

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
| `e1-cycloid` | `True` | `none` | `0.0006200308770840168` | `1.9211360684568762e-07` | `0.08381777201454771` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.000502724146612441` | `8.088965131755214e-05` | `0.0838937877737909` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0006200109751256688` | `5.424137569042532e-05` | `0.0838177263734309` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.00062002956679446` | `2.4014147313410625e-07` | `0.08381782306873975` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
