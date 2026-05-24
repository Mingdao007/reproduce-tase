# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/orientation_gate_boundary_plus1mm/planar_normal30_kp0p001/orientation_gate_0p1195`

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
| `e1-cycloid` | `True` | `none` | `0.014048521619363515` | `2.412419363211914e-06` | `0.11948545227775914` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `max_orientation_error_rad` | `0.1223546677432889` | `6.593492789727326e-06` | `0.11973133163816624` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.014031520541206878` | `2.411708355776875e-06` | `0.11948545227473706` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.014081547928564824` | `2.4142114489356797e-06` | `0.11948545227775914` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
