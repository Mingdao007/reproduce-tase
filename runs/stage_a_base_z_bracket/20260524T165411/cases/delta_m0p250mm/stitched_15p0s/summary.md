# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stage_a_base_z_bracket/20260524T165411/cases/delta_m0p250mm/stitched_15p0s`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.1437320363811954`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `2.9306010161254115e-05` | `2.387551361879427e-09` | `0.07297122128023693` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.003452607800959293` | `1.2056270411758664e-06` | `0.07370517757279291` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `2.9297057158088613e-05` | `6.004390318712195e-08` | `0.07297129098304002` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `2.9299284737507313e-05` | `2.3872807168590082e-09` | `0.07297176990129865` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
