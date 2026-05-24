# Timing Feasibility Sweep Summary

Run root: `runs/tilted_orientation_gain_timing_sweep/20260524T091826/kp0p25`

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
| e1-cycloid | `0.05` | `False` | `max_orientation_error_rad` | `0.0021338787423030637` | `1.0` | `4.1259201741487435e-06` | `5.532570007126561e-10` | `1.0803327840197248e-11` | `0.0` | `0.24531098707176816` | `0.1744456588511598` | `3.551370008415211e-06` |
| e1-cycloid | `0.075` | `False` | `max_orientation_error_rad` | `0.002134130648298882` | `1.0` | `4.126062695144927e-06` | `5.535173510795954e-10` | `1.0803679707847933e-11` | `0.0` | `0.24531120157979486` | `0.1744456588511598` | `7.987443653810365e-06` |
| e1-cycloid | `0.1` | `False` | `max_orientation_error_rad` | `0.002134621303736162` | `1.0` | `4.126340646160246e-06` | `5.542060264088609e-10` | `1.0804366001046853e-11` | `0.0` | `0.24531161979307198` | `0.1744456588511598` | `1.4178358880774764e-05` |
