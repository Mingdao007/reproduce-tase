# Timing Feasibility Sweep Summary

Run root: `runs/tilted_orientation_gain_timing_sweep/20260524T091826/kp1p0`

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
| e1-cycloid | `0.05` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005552897717242855` | `1.0` | `9.279285217515003e-06` | `2.3112769028160265e-09` | `4.110386153893895e-11` | `1.0` | `1.0` | `0.17418386008451897` | `0.07466032247827491` |
| e1-cycloid | `0.075` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005552990351419318` | `1.0` | `9.279301428345605e-06` | `2.311281100889557e-09` | `4.1103875755539934e-11` | `1.0` | `1.0` | `0.17418386008451897` | `0.07466040890291388` |
| e1-cycloid | `0.1` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005553170726111966` | `1.0` | `9.279333133892646e-06` | `2.311291698008317e-09` | `4.1103901437578895e-11` | `1.0` | `1.0` | `0.17418386008451897` | `0.07466057862274032` |
