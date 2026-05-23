# Timing Feasibility Sweep Summary

Run root: `runs/orientation_gate_timing_sweep/20260524T024000_e3_slowest`

## Gates

- `solver_success_fraction_min`: `1.0`
- `contact_present_fraction_min`: `1.0`
- `tail_mean_abs_force_error_N_max`: `0.25`
- `max_tangential_position_error_m_max`: `0.002`
- `max_planar_velocity_slack_m_s_max`: `0.001`
- `max_abs_normal_velocity_slack_m_s_max`: `0.0002`
- `max_qdot_violation_rad_s_max`: `1e-09`
- `max_joint_limit_violation_rad_max`: `1e-09`
- `qdot_saturation_fraction_max`: `0.01`
- `tail_max_qdot_utilization_max`: `0.98`
- `max_orientation_error_rad_max`: `0.03`
- `max_angular_velocity_slack_rad_s_max`: `0.03`

## Fastest Passing Scale

- `e3-circle`: `0.075`

## Cases

| trajectory | scale | pass | failed criteria | force error N | contact | max pos err m | max planar slack m/s | max normal slack m/s | qdot sat frac | tail qdot util | max orient err rad | max angular slack rad/s |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e3-circle | `0.075` | `True` | `none` | `0.0002767261880519001` | `1.0` | `0.0012876485738243357` | `0.0008100249550457771` | `2.5141812546734537e-11` | `0.0` | `0.02105363299341864` | `0.0019271205686722252` | `0.0021471302908745147` |
| e3-circle | `0.05` | `True` | `none` | `0.0002763905219137308` | `1.0` | `0.0008587271350232869` | `0.0005402789889422763` | `2.514181271420438e-11` | `0.0` | `0.009334589514752622` | `0.0012852078534766902` | `0.0014320441645986678` |
