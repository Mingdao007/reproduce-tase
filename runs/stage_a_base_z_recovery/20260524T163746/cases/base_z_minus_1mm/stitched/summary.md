# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stage_a_base_z_recovery/20260524T163746/cases/base_z_minus_1mm/stitched`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `False`
- Stage B handoff passes: `0 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.15`
- Stage A qdot saturation fraction: `0.007866666666666666`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `False` | `qdot_saturation_fraction` | `5.050672205155315e-05` | `1.2137531313782481e-05` | `0.04639437236625568` | `0.014` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction` | `0.0046733874043616815` | `1.1690613312230666e-05` | `0.046394483821095595` | `0.014` | `1.0` |
| `e3-circle` | `False` | `qdot_saturation_fraction` | `5.2092251948772096e-05` | `1.2137775951598139e-05` | `0.0463943723668235` | `0.014` | `1.0` |
| `e4-cardioid` | `False` | `qdot_saturation_fraction` | `4.9086953922352626e-05` | `1.2137422633539882e-05` | `0.04639437236625568` | `0.014` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
