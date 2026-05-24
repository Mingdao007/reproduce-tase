# Planar-Primary Approach Summary

Run root: `runs/staged_orientation_planar_primary_approach/20260524T103539`

## Counts

- Cases: `6`
- Approach terminal-orientation passes: `6 / 6`
- Approach terminal-budget passes: `0 / 6`
- Approach ordinary-feasibility passes: `0 / 6`
- Trajectory-after-approach passes: `1 / 6`
- Full staged-feasibility passes: `0 / 6`

## Rows

| case | terminal budget failed | final orient | qdot sat | drift m | planar slack | angular slack | trajectory after |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `weighted_ref_kp2_a0p25_4s` | max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization | `0.0020290714973557108` | `1.0` | `0.008347977658392892` | `0.019029396767311284` | `0.01473460419378443` | `True` |
| `planar_primary_kp2_a0p25_4s` | contact_present_fraction;tail_mean_abs_force_error_N;max_abs_normal_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization | `7.570584319181321e-05` | `0.185` | `1.5446522353872519e-06` | `8.19003835426546e-11` | `0.011087482069239096` | `False` |
| `planar_primary_kp2_a0p35_4s` | contact_present_fraction;tail_mean_abs_force_error_N;max_abs_normal_velocity_slack_m_s;qdot_saturation_fraction | `7.565716621433935e-05` | `0.0715` | `2.063170116845328e-05` | `1.2117730267564345e-10` | `7.843152726498693e-05` | `False` |
| `planar_primary_kp2_a0p50_4s` | contact_present_fraction;tail_mean_abs_force_error_N;max_abs_normal_velocity_slack_m_s;qdot_saturation_fraction | `7.565056974434516e-05` | `0.029` | `2.025056658426158e-05` | `1.2193143147714868e-10` | `7.84336421797315e-05` | `False` |
| `planar_primary_kp1_a0p25_8s` | contact_present_fraction;tail_mean_abs_force_error_N;max_abs_normal_velocity_slack_m_s;qdot_saturation_fraction | `9.379294441211913e-05` | `0.03975` | `2.807367009237914e-05` | `1.1939196704305498e-10` | `5.2289721516242674e-05` | `False` |
| `planar_primary_kp2_cap0p05_a0p25_8s` | contact_present_fraction;tail_mean_abs_force_error_N;max_abs_normal_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization | `1.8807622454296194e-05` | `0.02925` | `2.789035007869957e-05` | `1.188966914560247e-10` | `6.773528627549216e-05` | `False` |
