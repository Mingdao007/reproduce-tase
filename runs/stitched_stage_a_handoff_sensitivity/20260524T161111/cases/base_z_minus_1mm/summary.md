# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stitched_stage_a_handoff_sensitivity/20260524T161111/cases/base_z_minus_1mm`

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
| `e1-cycloid` | `False` | `tail_mean_abs_force_error_N;qdot_saturation_fraction;max_angular_velocity_slack_rad_s` | `4.808157710474882` | `9.581415611293761e-05` | `0.07230405414996799` | `0.136` | `1.0` |
| `e2-figure-eight` | `False` | `tail_mean_abs_force_error_N;qdot_saturation_fraction;max_angular_velocity_slack_rad_s` | `4.512265760185769` | `9.525854660903492e-05` | `0.07230416166445983` | `0.135` | `1.0` |
| `e3-circle` | `False` | `tail_mean_abs_force_error_N;qdot_saturation_fraction;max_angular_velocity_slack_rad_s` | `4.80843116250581` | `9.58144430554789e-05` | `0.07230405415033274` | `0.136` | `1.0` |
| `e4-cardioid` | `False` | `tail_mean_abs_force_error_N;qdot_saturation_fraction;max_angular_velocity_slack_rad_s` | `4.807909556320495` | `9.581392504345518e-05` | `0.07230405414996799` | `0.136` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
