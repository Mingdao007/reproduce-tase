# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/qdot012_stage_a_margin/20260524T194817/cases/stage_a_18p01s`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `False`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `18.01`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.12`
- Stage A qdot saturation fraction: `0.007773459189339256`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `1.8917946730447888e-05` | `3.797428146465342e-07` | `0.08932125105148857` | `0.007` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007434306385233391` | `4.583762103059539e-07` | `0.08961814490742943` | `0.006` | `1.0` |
| `e3-circle` | `True` | `none` | `1.891139099761574e-05` | `3.8091920787791014e-07` | `0.08932125105156341` | `0.007` | `1.0` |
| `e4-cardioid` | `True` | `none` | `1.8926785834016967e-05` | `3.79742014936478e-07` | `0.08932125105148857` | `0.007` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
