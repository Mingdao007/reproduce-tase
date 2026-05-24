# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_orientation_gate_boundary/20260524T221842/cases/orientation_gate_0p1199`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.10018584837167505`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `5.669959640426825e-05` | `5.140973794872344e-09` | `0.11948787562097642` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `max_orientation_error_rad` | `0.0004859525136908127` | `4.492792485707658e-07` | `0.1199788204275829` | `0.006` | `1.0` |
| `e3-circle` | `True` | `none` | `5.669861558827094e-05` | `3.043440279076355e-08` | `0.11948785215835259` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `5.6699638877333314e-05` | `5.140892109581352e-09` | `0.11948805833755421` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
