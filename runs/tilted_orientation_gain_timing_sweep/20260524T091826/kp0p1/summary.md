# Timing Feasibility Sweep Summary

Run root: `runs/tilted_orientation_gain_timing_sweep/20260524T091826/kp0p1`

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

- `e1-cycloid`: none

## Cases

| trajectory | scale | pass | failed criteria | force error N | contact | max pos err m | max planar slack m/s | max normal slack m/s | qdot sat frac | tail qdot util | max orient err rad | max angular slack rad/s |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e1-cycloid | `0.05` | `False` | `max_orientation_error_rad` | `0.00017021009960104026` | `1.0` | `1.1023112188650996e-06` | `2.0669234005567142e-10` | `6.883695456911306e-12` | `0.0` | `0.10864164340958926` | `0.1744980186604636` | `3.112113010491921e-06` |
| e1-cycloid | `0.075` | `False` | `max_orientation_error_rad` | `0.00017028171203874897` | `1.0` | `1.10245592973691e-06` | `2.067821966585339e-10` | `6.8836985028417844e-12` | `0.0` | `0.10864180071848975` | `0.1744980186604636` | `7.001930470953769e-06` |
| e1-cycloid | `0.1` | `False` | `max_orientation_error_rad` | `0.00017042122824620254` | `1.0` | `1.102739183989308e-06` | `2.0702849796448462e-10` | `6.883704948762513e-12` | `0.0` | `0.10864210734330415` | `0.1744980186604636` | `1.2447475324324366e-05` |
