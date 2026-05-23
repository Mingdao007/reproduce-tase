# Timing Feasibility Sweep Summary

Run root: `runs/orientation_hold_matrix/20260524T030000`

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

## Fastest Passing Scale

- `e1-cycloid`: none
- `e2-figure-eight`: none
- `e3-circle`: none
- `e4-cardioid`: none

## Cases

| trajectory | scale | pass | failed criteria | force error N | contact | max pos err m | max planar slack m/s | max normal slack m/s | qdot sat frac | tail qdot util | max orient err rad | max angular slack rad/s |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e1-cycloid | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s` | `0.00023345708686040357` | `1.0` | `0.003184744896662225` | `0.0023655651362415155` | `2.5700554600126784e-10` | `0.0` | `0.19765985534798058` | `0.005136871635287625` | `0.006274316963057496` |
| e2-figure-eight | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s` | `0.0002160326762435305` | `1.0` | `0.007298434567067694` | `0.003929059585831822` | `8.91315230495758e-09` | `0.0` | `0.1299873376961688` | `0.010260627469780797` | `0.010467138725926963` |
| e3-circle | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s` | `0.0002862430359814949` | `1.0` | `0.015476725649078916` | `0.009324376968676102` | `3.2042642749295684e-09` | `0.0` | `0.026477315569359533` | `0.022792200960046364` | `0.024703715417836912` |
| e4-cardioid | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s` | `0.0003562830612294643` | `1.0` | `0.004494395723717899` | `0.003780887157776594` | `1.3289805594237356e-09` | `0.0` | `0.38557402962949205` | `0.007633905650640362` | `0.010045349955744527` |
