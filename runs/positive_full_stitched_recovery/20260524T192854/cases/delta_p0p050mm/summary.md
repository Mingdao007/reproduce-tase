# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_full_stitched_recovery/20260524T192854/cases/delta_p0p050mm`

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
| `e1-cycloid` | `True` | `none` | `3.291151129361847e-05` | `2.722405771995576e-09` | `0.0838185077912618` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007883124401614117` | `5.747786051125612e-07` | `0.08420730609192884` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `3.291081868239232e-05` | `3.012071621387099e-08` | `0.08381851037856232` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.2911043221481865e-05` | `2.722337817846754e-09` | `0.08381865298145363` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
