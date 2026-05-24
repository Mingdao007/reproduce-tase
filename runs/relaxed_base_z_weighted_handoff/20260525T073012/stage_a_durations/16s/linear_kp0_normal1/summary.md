# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `runs/relaxed_base_z_weighted_handoff/20260525T073012/stage_a_durations/16s/linear_kp0_normal1`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `16.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.09392423284836762`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `5.669959765360222e-05` | `5.140973800015056e-09` | `0.11948787583359269` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad` | `0.014411641468066758` | `2.6550961724412553e-06` | `0.12043140848858806` | `0.997` | `1.0` |
| `e3-circle` | `True` | `none` | `5.671250341303669e-05` | `6.03974586869268e-08` | `0.11948840647715146` | `0.001` | `1.0` |
| `e4-cardioid` | `True` | `none` | `5.669709288266489e-05` | `5.140647007031984e-09` | `0.11948860657458475` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
