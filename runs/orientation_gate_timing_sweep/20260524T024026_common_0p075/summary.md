# Timing Feasibility Sweep Summary

Run root: `runs/orientation_gate_timing_sweep/20260524T024026_common_0p075`

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
| e1-cycloid | `0.075` | `True` | `none` | `0.0002761448535938249` | `1.0` | `1.8868465925812454e-05` | `1.4265227440402491e-05` | `2.5141813380678056e-11` | `0.0` | `0.003832267316618259` | `3.059816704048032e-05` | `3.780945473030017e-05` |
| e2-figure-eight | `0.075` | `True` | `none` | `0.00027738073633691964` | `1.0` | `0.0008569078322545231` | `0.0005386775381705987` | `2.507376320072545e-11` | `0.0` | `0.013350766959419039` | `0.0012822401289417794` | `0.0014280104295813921` |
| e3-circle | `0.075` | `True` | `none` | `0.0002767261880519001` | `1.0` | `0.0012876485738243357` | `0.0008100249550457771` | `2.5141812546734537e-11` | `0.0` | `0.02105363299341864` | `0.0019271205686722252` | `0.0021471302908745147` |
| e4-cardioid | `0.075` | `True` | `none` | `0.00027616389789717475` | `1.0` | `2.2219365951485773e-06` | `1.9594471061394405e-06` | `2.5141813380678056e-11` | `0.0` | `0.0038831888029910574` | `3.821381556607561e-06` | `5.1934498799531995e-06` |
