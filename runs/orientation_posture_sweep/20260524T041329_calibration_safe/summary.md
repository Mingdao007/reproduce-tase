# Posture Feasibility Sweep Summary

Run root: `runs/orientation_posture_sweep/20260524T041329_calibration_safe`

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
| bend_0p15 | `False` | `None` | `None` | `None` | `could not calibrate initial posture to target force: best force 0 N, target 5 N, tolerance 0.01 N` |
| bend_0p20 | `False` | `None` | `None` | `None` | `could not calibrate initial posture to target force: best force 10.404 N, target 5 N, tolerance 0.01 N` |

## Cases

| posture | trajectory | scale | pass | failed criteria | base z offset m | force error N | max pos err m | max planar slack m/s | max orient err rad | max angular slack rad/s | qdot sat frac | tail qdot util |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bend_0p10 | e2-figure-eight | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s` | `-0.0009710693359375` | `0.0002160326762435305` | `0.007298434567067694` | `0.003929059585831822` | `0.010260627469780797` | `0.010467138725926963` | `0.0` | `0.1299873376961688` |
| bend_0p10 | e3-circle | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s` | `-0.0009710693359375` | `0.0002862430359814949` | `0.015476725649078916` | `0.009324376968676102` | `0.022792200960046364` | `0.024703715417836912` | `0.0` | `0.026477315569359533` |
| bend_0p125 | e2-figure-eight | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s` | `-0.0014990234375000001` | `0.00019339910009364748` | `0.007286412725588208` | `0.003922910008048283` | `0.010270627122803135` | `0.01047734112092219` | `0.0` | `0.069661239122212` |
| bend_0p125 | e3-circle | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s` | `-0.0014990234375000001` | `0.0002577797133068904` | `0.015470348110780442` | `0.00932163031725057` | `0.02280085805300149` | `0.024712402242088063` | `0.0` | `0.02474131146878367` |
