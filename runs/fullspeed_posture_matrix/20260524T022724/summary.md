# Timing Feasibility Sweep Summary

Run root: `runs/fullspeed_posture_matrix/20260524T022724`

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

- `e1-cycloid`: `1.0`
- `e2-figure-eight`: `1.0`
- `e3-circle`: `1.0`
- `e4-cardioid`: `1.0`

## Cases

| trajectory | scale | pass | failed criteria | force error N | contact | max pos err m | max planar slack m/s | max normal slack m/s | qdot sat frac | tail qdot util |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e1-cycloid | `1.0` | `True` | `none` | `0.00027102719026141477` | `1.0` | `2.0289880039871015e-06` | `1.897200973171906e-08` | `2.4887024409519794e-11` | `0.0` | `0.0270511666757969` |
| e2-figure-eight | `1.0` | `True` | `none` | `0.0004002236522971103` | `1.0` | `8.944242301072789e-06` | `3.4331973232314785e-07` | `6.468019924450903e-10` | `0.0` | `0.15222223080960362` |
| e3-circle | `1.0` | `True` | `none` | `0.000821132687569398` | `1.0` | `5.999914591097446e-06` | `1.1696023075496035e-06` | `1.3933000621302316e-09` | `0.0` | `0.27981610187783346` |
| e4-cardioid | `1.0` | `True` | `none` | `0.00017724280364998736` | `1.0` | `4.011419213392556e-06` | `4.479704402857127e-08` | `5.559575949227471e-11` | `0.0` | `0.054634419431542555` |
