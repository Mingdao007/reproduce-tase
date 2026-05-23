# Timing Feasibility Sweep Summary

Run root: `runs/nullspace_orientation_timing_sweep/20260524T042206_common_0p075`

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

- `e1-cycloid`: `0.075`
- `e2-figure-eight`: `0.075`
- `e3-circle`: `0.075`
- `e4-cardioid`: `0.075`

## Cases

| trajectory | scale | pass | failed criteria | force error N | contact | max pos err m | max planar slack m/s | max normal slack m/s | qdot sat frac | tail qdot util | max orient err rad | max angular slack rad/s |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e1-cycloid | `0.075` | `True` | `none` | `0.000276144819236912` | `1.0` | `1.1694975573206327e-08` | `5.958126716066033e-10` | `2.5135894620332156e-11` | `0.0` | `0.0038318015338999816` | `0.00010183147439858829` | `0.0001272290438944111` |
| e2-figure-eight | `0.075` | `True` | `none` | `0.0002771005815372496` | `1.0` | `6.708191085550114e-07` | `2.4433712474975925e-09` | `2.461024130117435e-11` | `0.0` | `0.005903898478793365` | `0.004516128236962064` | `0.005076738194606452` |
| e3-circle | `0.075` | `True` | `none` | `0.00027633354479075225` | `1.0` | `4.49993594371628e-07` | `3.695694551120664e-09` | `2.5135894633884683e-11` | `0.0` | `0.005652094795331068` | `0.006787233568225033` | `0.007632937570076151` |
| e4-cardioid | `0.075` | `True` | `none` | `0.00027616389259353056` | `1.0` | `2.3656478121235595e-08` | `5.958126716066033e-10` | `2.5135894620332156e-11` | `0.0` | `0.0038831831175570393` | `1.2211424954475569e-05` | `1.6778016440715262e-05` |
