# Posture Feasibility Sweep Summary

Run root: `runs/orientation_posture_sweep/20260524T041329_weight_0p01`

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
| bend_0p10 | e2-figure-eight | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;max_angular_velocity_slack_rad_s` | `-0.0009710693359375` | `0.0002682015112313996` | `0.0021081773121512716` | `0.0011401155164503574` | `0.029713309003769003` | `0.030301564155539605` | `0.0` | `0.21998062669368101` |
| bend_0p10 | e3-circle | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `-0.0009710693359375` | `0.0001662665701877697` | `0.004366371262656862` | `0.0026790837997653326` | `0.06477119695525288` | `0.07081559362643841` | `0.0` | `0.0665436945734184` |
| bend_0p125 | e2-figure-eight | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;max_angular_velocity_slack_rad_s` | `-0.0014990234375000001` | `0.00021567373884567086` | `0.0020962958053321783` | `0.0011338654290518283` | `0.029647662885572135` | `0.030238356115096055` | `0.0` | `0.07530907522421867` |
| bend_0p125 | e3-circle | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `-0.0014990234375000001` | `0.00016318918244615066` | `0.004362421708908419` | `0.00267814048188025` | `0.06475140615024173` | `0.07080130976446315` | `0.0` | `0.0469515728848963` |
