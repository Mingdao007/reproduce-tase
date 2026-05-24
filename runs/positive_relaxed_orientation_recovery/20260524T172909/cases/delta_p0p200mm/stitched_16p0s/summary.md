# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p200mm/stitched_16p0s`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `16.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.1352275986068202`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `3.512380295846551e-05` | `2.8911075048852414e-09` | `0.08934455610574711` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `tail_max_qdot_utilization` | `0.0031148181393145877` | `1.1338497896879487e-06` | `0.09014617602004879` | `0.005` | `1.0` |
| `e3-circle` | `True` | `none` | `3.511529080034492e-05` | `6.006449168905585e-08` | `0.08934454608799451` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.511797761530211e-05` | `2.89083494208614e-09` | `0.08934515502907699` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
