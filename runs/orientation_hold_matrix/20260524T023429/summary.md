# Timing Feasibility Sweep Summary

Run root: `runs/orientation_hold_matrix/20260524T023429`

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

| trajectory | scale | pass | failed criteria | force error N | contact | max pos err m | max planar slack m/s | max normal slack m/s | qdot sat frac | tail qdot util | max orient err rad | max angular slack rad/s |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e1-cycloid | `1.0` | `True` | `none` | `0.00027029934127870245` | `1.0` | `8.681961433797088e-06` | `8.003170786422185e-06` | `2.5138538108367022e-11` | `0.0` | `0.026984383521778604` | `0.017123697812485454` | `0.02116478539299565` |
| e2-figure-eight | `1.0` | `True` | `none` | `0.0004916689518725792` | `1.0` | `2.797143784170073e-05` | `2.9408999634158134e-05` | `3.0544515859632325e-08` | `0.0` | `0.6171247964473606` | `0.03763453579359901` | `0.04250367598436786` |
| e3-circle | `1.0` | `True` | `none` | `0.0008205269114679869` | `1.0` | `5.097698265515408e-05` | `3.483121447610465e-05` | `1.3843127033316384e-09` | `0.0` | `0.28127974679800305` | `0.08108796381776726` | `0.08895566203803207` |
| e4-cardioid | `1.0` | `True` | `none` | `0.00017134573277962305` | `1.0` | `1.0950950750024289e-05` | `1.2398130453431907e-05` | `6.136117199949192e-11` | `0.0` | `0.054561711669854386` | `0.024563131472431995` | `0.03274048254777163` |
