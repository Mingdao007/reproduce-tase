# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stitched_stage_a_handoff_timing_margin/20260524T162005/cases/stage_a_14s_reference_fail`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `False`
- Stage B handoff passes: `0 / 4`
- Stage A duration: `14.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.15`
- Stage A qdot saturation fraction: `0.007857142857142858`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `False` | `qdot_saturation_fraction` | `1.1171949911261692e-05` | `6.470520315760666e-06` | `0.0719995984096914` | `0.011` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction` | `0.005164775788000147` | `6.128959902857476e-06` | `0.071999704472154` | `0.011` | `1.0` |
| `e3-circle` | `False` | `qdot_saturation_fraction` | `1.1919573552434671e-05` | `6.4708453060925745e-06` | `0.07199959841005779` | `0.011` | `1.0` |
| `e4-cardioid` | `False` | `qdot_saturation_fraction` | `1.0512019753994295e-05` | `6.470455871267558e-06` | `0.0719995984096914` | `0.011` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
