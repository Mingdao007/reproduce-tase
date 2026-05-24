# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stitched_stage_a_handoff_sensitivity/20260524T161111/cases/force_gain_2e-4`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14332635022814824`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.00011809853351512522` | `2.254899218719939e-08` | `0.07241201490811311` | `0.002` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.000865457999273005` | `1.2155721613956073e-06` | `0.07314804008539172` | `0.003` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0001180958566031709` | `6.40915281187594e-08` | `0.07241208926134908` | `0.002` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.000118097647698292` | `2.254868312900893e-08` | `0.07241256272984686` | `0.002` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
