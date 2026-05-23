# Timing Feasibility Sweep Summary

Run root: `runs/orientation_hold_matrix/20260524T023404`

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
- `e2-figure-eight`: none
- `e3-circle`: `1.0`
- `e4-cardioid`: `1.0`

## Cases

| trajectory | scale | pass | failed criteria | force error N | contact | max pos err m | max planar slack m/s | max normal slack m/s | qdot sat frac | tail qdot util | max orient err rad | max angular slack rad/s |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e1-cycloid | `1.0` | `True` | `none` | `0.0002708270903703058` | `1.0` | `0.00010136691740339613` | `7.820850438776733e-05` | `3.114292312609352e-11` | `0.0` | `0.026378459173936466` | `0.016772995249312396` | `0.020723367155237336` |
| e2-figure-eight | `1.0` | `False` | `tail_max_qdot_utilization` | `0.0005134566894483306` | `1.0` | `0.0002657755099582494` | `0.00028049017609834445` | `2.910164911601926e-07` | `0.00275` | `0.9999999999999739` | `0.03667002065926858` | `0.04141134595474439` |
| e3-circle | `1.0` | `True` | `none` | `0.0006555234577822844` | `1.0` | `0.0005297974306642689` | `0.00032966241701242236` | `7.543038268856287e-10` | `0.0` | `0.24629749248149754` | `0.0792791337407633` | `0.0869211753487964` |
| e4-cardioid | `1.0` | `True` | `none` | `0.00017613695005304299` | `1.0` | `0.0001374949822338604` | `0.00012105256232393342` | `1.0365010731389932e-10` | `0.0` | `0.07796198949547566` | `0.024079555351106275` | `0.032079155772562755` |
