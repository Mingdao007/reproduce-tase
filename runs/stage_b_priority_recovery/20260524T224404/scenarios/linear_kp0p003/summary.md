# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stage_b_priority_recovery/20260524T224404/scenarios/linear_kp0p003`

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
| `e1-cycloid` | `True` | `none` | `5.670731217903846e-05` | `1.195825222890876e-08` | `0.11948807166364375` | `0.004` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.009642392425932473` | `2.2240508896863157e-06` | `0.11994467909936898` | `1.0` | `1.0` |
| `e3-circle` | `True` | `none` | `5.6707064768186654e-05` | `3.22916057597653e-08` | `0.11948803729888204` | `0.004` | `1.0` |
| `e4-cardioid` | `True` | `none` | `5.6707053025615295e-05` | `1.1958142216890455e-08` | `0.11948825475291852` | `0.004` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
