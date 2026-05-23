# Timing Feasibility Sweep Summary

Run root: `runs/timing_feasibility_sweep/20260524T021322`

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

- `e2-figure-eight`: `0.2`
- `e3-circle`: `0.2`

## Cases

| trajectory | scale | pass | failed criteria | force error N | contact | max pos err m | max planar slack m/s | max normal slack m/s | qdot sat frac | tail qdot util |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| e2-figure-eight | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0479840836286729` | `1.0` | `0.02114338335402673` | `0.013216502110190214` | `0.00010718233529072995` | `0.78175` | `0.9999999999999998` |
| e2-figure-eight | `0.75` | `False` | `solver_success_fraction;max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.03045464335463004` | `1.0` | `0.015202002057587127` | `0.010267050563011332` | `8.318032365387142e-05` | `0.697` | `0.9999999999999998` |
| e2-figure-eight | `0.5` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.01159829983132263` | `1.0` | `0.00795109456427083` | `0.005962011882315249` | `4.865735029919749e-05` | `0.55925` | `0.9999999999999998` |
| e2-figure-eight | `0.35` | `False` | `solver_success_fraction;max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0028221942256946362` | `1.0` | `0.0030961234538903716` | `0.0030659153238616252` | `2.6521352327178817e-05` | `0.3675` | `0.9999999999999998` |
| e2-figure-eight | `0.25` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0007294332645588986` | `1.0` | `0.00031737751452890384` | `0.0007251472811804109` | `5.0713298296600925e-06` | `0.11525` | `0.9999999999999998` |
| e2-figure-eight | `0.2` | `True` | `none` | `0.00034204709355621144` | `1.0` | `1.7888622586078747e-06` | `2.3310453749022684e-07` | `1.9912104774848293e-08` | `0.00075` | `0.10194983790754977` |
| e2-figure-eight | `0.15` | `True` | `none` | `0.0003427587992907799` | `1.0` | `1.341651517564839e-06` | `7.179941391533738e-08` | `1.9984226734242342e-08` | `0.00075` | `0.04410922858722124` |
| e2-figure-eight | `0.1` | `True` | `none` | `0.00034347390161298063` | `1.0` | `8.944407745611925e-07` | `7.260979574082636e-08` | `2.005623196891778e-08` | `0.00075` | `0.026550172666882487` |
| e3-circle | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.014410140908808211` | `1.0` | `0.016176223350410992` | `0.010692708281149576` | `5.456710213298902e-05` | `0.7635` | `0.9999999999999998` |
| e3-circle | `0.75` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.007488841114131854` | `1.0` | `0.010666778889808088` | `0.0072607244352757274` | `3.68949436568819e-05` | `0.68325` | `0.9999999999999998` |
| e3-circle | `0.5` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0027643106311170816` | `1.0` | `0.00531453044480968` | `0.0038908995363691854` | `1.9011512800189808e-05` | `0.52325` | `0.9999999999999998` |
| e3-circle | `0.35` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0016541100146724686` | `1.0` | `0.002267666619382421` | `0.001959416003380574` | `9.256189626158597e-06` | `0.31775` | `0.9999999999999998` |
| e3-circle | `0.25` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0003790708341966742` | `1.0` | `0.00023000343483424836` | `0.0009047004546188087` | `4.201553695565921e-06` | `0.044` | `0.9999999999999998` |
| e3-circle | `0.2` | `True` | `none` | `0.00034345836495965564` | `1.0` | `1.1999829125721333e-06` | `1.592789560750357e-07` | `2.0199615644770825e-08` | `0.00075` | `0.0713623093095374` |
| e3-circle | `0.15` | `True` | `none` | `0.0003448327783867366` | `1.0` | `8.999871845433577e-07` | `7.45871304727192e-08` | `2.0199615271021736e-08` | `0.00075` | `0.036838329548078856` |
| e3-circle | `0.1` | `True` | `none` | `0.0003453163106393231` | `1.0` | `5.999914565779483e-07` | `7.443403444049948e-08` | `2.0199612487562628e-08` | `0.00075` | `0.023567264296563285` |
