# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stitched_stage_a_handoff_sensitivity/20260524T161111/cases/qdot_limit_0p12`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `False`
- Stage B handoff passes: `0 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.12`
- Stage A qdot saturation fraction: `0.007866666666666666`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `False` | `qdot_saturation_fraction` | `0.003568340214454935` | `3.594722271629485e-05` | `0.06961495275010633` | `0.039` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction` | `0.002230166573816357` | `3.5379701878431434e-05` | `0.06961504852018745` | `0.039` | `1.0` |
| `e3-circle` | `False` | `qdot_saturation_fraction` | `0.0035858309824553956` | `3.594750388367622e-05` | `0.06961495275048542` | `0.039` | `1.0` |
| `e4-cardioid` | `False` | `qdot_saturation_fraction` | `0.003553400230742425` | `3.594702165206354e-05` | `0.06961495275010633` | `0.039` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
