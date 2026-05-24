# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454/full_delta/linear_kp0_normal1/delta_0p150mm`

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
| `e1-cycloid` | `True` | `none` | `3.434972998716201e-05` | `2.8348728030453856e-09` | `0.08749554372308346` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.001708665485445997` | `8.459845609874768e-07` | `0.08809077813650315` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `3.4346980095665284e-05` | `4.508536665567123e-08` | `0.08749553943779005` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.4347747527938565e-05` | `2.834719594474455e-09` | `0.08749587711833287` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
