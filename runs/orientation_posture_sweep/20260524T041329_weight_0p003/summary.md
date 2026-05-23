# Posture Feasibility Sweep Summary

Run root: `runs/orientation_posture_sweep/20260524T041329_weight_0p003`

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
| bend_0p10 | e2-figure-eight | `1.0` | `False` | `max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `-0.0009710693359375` | `0.00034256910407192586` | `0.000741141725155931` | `0.00040161631181505575` | `0.034844387332592645` | `0.035522015552872495` | `0.0` | `0.5450930674263775` |
| bend_0p10 | e3-circle | `1.0` | `False` | `max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `-0.0009710693359375` | `0.00036768889207703824` | `0.0015226098148179506` | `0.0009402057846871742` | `0.0755330904105644` | `0.08277608853859442` | `0.0` | `0.14405709134758415` |
| bend_0p125 | e2-figure-eight | `1.0` | `False` | `max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `-0.0014990234375000001` | `0.0002814820824072184` | `0.0007351978234364795` | `0.0003986359302790356` | `0.03472088057428398` | `0.03540700853906509` | `0.0` | `0.17765631947961025` |
| bend_0p125 | e3-circle | `1.0` | `False` | `max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `-0.0014990234375000001` | `0.00039336744607612937` | `0.001521386915630163` | `0.0009402743814415168` | `0.07550444953824784` | `0.08276242773052735` | `0.0` | `0.18087249410796769` |
