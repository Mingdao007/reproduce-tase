# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stitched_stage_a_handoff_sensitivity/20260524T161111/cases/base_z_plus_1mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `False`
- Stage B handoff passes: `0 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14332635022814824`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `False` | `contact_present_fraction;tail_mean_abs_force_error_N;qdot_saturation_fraction;tail_max_qdot_utilization` | `5.0` | `1.292956147785803e-07` | `0.027373602535981856` | `0.999` | `0.0` |
| `e2-figure-eight` | `False` | `contact_present_fraction;tail_mean_abs_force_error_N;qdot_saturation_fraction;tail_max_qdot_utilization` | `5.0` | `8.930348629499102e-08` | `0.02753419451554103` | `0.999` | `0.0` |
| `e3-circle` | `False` | `contact_present_fraction;tail_mean_abs_force_error_N;qdot_saturation_fraction;tail_max_qdot_utilization` | `5.0` | `1.4236330898076285e-07` | `0.02737496222919642` | `0.999` | `0.0` |
| `e4-cardioid` | `False` | `contact_present_fraction;tail_mean_abs_force_error_N;qdot_saturation_fraction;tail_max_qdot_utilization` | `5.0` | `1.292457611811586e-07` | `0.027373686167725345` | `0.999` | `0.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
