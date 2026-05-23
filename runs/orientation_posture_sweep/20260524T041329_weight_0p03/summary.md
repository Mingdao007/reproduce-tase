# Posture Feasibility Sweep Summary

Run root: `runs/orientation_posture_sweep/20260524T041329_weight_0p03`

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

## Fastest Scale Passing All Requested Trajectories

- `bend_0p10`: none
- `bend_0p125`: none

## Posture Calibration

| posture | pass | base z offset m | initial force N | contact count | error |
| --- | --- | ---: | ---: | ---: | --- |
| bend_0p10 | `True` | `-0.0009710693359375` | `4.995281922830507` | `1` | `none` |
| bend_0p125 | `True` | `-0.0014990234375000001` | `5.005930952900419` | `1` | `none` |

## Cases

| posture | trajectory | scale | pass | failed criteria | base z offset m | force error N | max pos err m | max planar slack m/s | max orient err rad | max angular slack rad/s | qdot sat frac | tail qdot util |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bend_0p10 | e2-figure-eight | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s` | `-0.0009710693359375` | `0.00023130783945310096` | `0.004459991785956491` | `0.002404776958087202` | `0.02091735647789599` | `0.021336044103234347` | `0.0` | `0.15131119424268424` |
| bend_0p10 | e3-circle | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `-0.0009710693359375` | `0.00024109719467782064` | `0.009332409383380758` | `0.005677440020932266` | `0.0459954258417765` | `0.05008584241124015` | `0.0` | `0.034469522148710956` |
| bend_0p125 | e2-figure-eight | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s` | `-0.0014990234375000001` | `0.00019987023611298116` | `0.004444203132114216` | `0.002396555571995204` | `0.02090444848766268` | `0.021323517227569776` | `0.0` | `0.07150036421501886` |
| bend_0p125 | e3-circle | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `-0.0014990234375000001` | `0.00021087846981932446` | `0.009325255341298501` | `0.00567462691953639` | `0.04599374500396258` | `0.050085097845713716` | `0.0` | `0.03209498397341579` |
