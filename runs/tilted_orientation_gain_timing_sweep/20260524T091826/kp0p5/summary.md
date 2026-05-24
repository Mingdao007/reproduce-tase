# Timing Feasibility Sweep Summary

Run root: `runs/tilted_orientation_gain_timing_sweep/20260524T091826/kp0p5`

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
| e1-cycloid | `0.05` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.001581200683072752` | `1.0` | `8.08398110996296e-06` | `1.1108882458766555e-09` | `2.1671026376125693e-11` | `0.229` | `1.0` | `0.17435839250232021` | `0.03769354013880992` |
| e1-cycloid | `0.075` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0015813218217458935` | `1.0` | `8.084067111631117e-06` | `1.1109227150980039e-09` | `2.167111066606834e-11` | `0.229` | `1.0` | `0.17435839250232021` | `0.0376959415297048` |
| e1-cycloid | `0.1` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.0015815317012663054` | `1.0` | `8.08423729217811e-06` | `1.1110126605313996e-09` | `2.1671274644870665e-11` | `0.229` | `1.0` | `0.17435839250232021` | `0.03769512024508997` |
