# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/orientation_gate0p119_time0p005/planar_normal30_kp0p001/delta_0p750mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.10367805178971796`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.009145785109179001` | `1.9835017692918627e-06` | `0.11002151899410738` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.09167439127198303` | `5.838771989531707e-06` | `0.110301295362831` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.009133793009778537` | `1.9829440346042915e-06` | `0.11002151899010892` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.009169919117555722` | `1.985155210494985e-06` | `0.11002151899410738` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
