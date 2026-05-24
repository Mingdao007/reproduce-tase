# Timing Feasibility Sweep Summary

Run root: `runs/tilted_orientation_gain_timing_sweep/20260524T091826/kp5p0`

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
| e1-cycloid | `0.05` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005500972850374586` | `1.0` | `9.543404143597923e-06` | `2.8224877156694035e-09` | `4.8531400686363524e-11` | `1.0` | `1.0` | `0.17416151436895033` | `0.6869592104751856` |
| e1-cycloid | `0.075` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005501050439880206` | `1.0` | `9.543415791277527e-06` | `2.8224893043827156e-09` | `4.8531406879868434e-11` | `1.0` | `1.0` | `0.17416151436895033` | `0.6869592104751856` |
| e1-cycloid | `0.1` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0005501200319756405` | `1.0` | `9.543438497833359e-06` | `2.822493353784906e-09` | `4.853141839951652e-11` | `1.0` | `1.0` | `0.17416151436895033` | `0.6869592104751856` |
