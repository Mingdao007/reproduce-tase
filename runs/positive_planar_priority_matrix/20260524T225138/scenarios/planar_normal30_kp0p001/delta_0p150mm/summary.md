# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_planar_priority_matrix/20260524T225138/scenarios/planar_normal30_kp0p001/delta_0p150mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.1421152405391769`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.0033932920577538052` | `1.23816676378194e-06` | `0.08749444100412965` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.04666814024306122` | `4.350915127499543e-06` | `0.08780371166094508` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0033843664349243728` | `1.237459416327822e-06` | `0.08749444100798992` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0034048421880683443` | `1.2395019591991342e-06` | `0.08749444100412965` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
