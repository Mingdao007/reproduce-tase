# Planar-Primary Normal-Weight Summary

Run root: `runs/staged_orientation_planar_primary_normal_weight/20260524T103646`

## Counts

- Cases: `5`
- Approach terminal-orientation passes: `1 / 5`
- Approach terminal-budget passes: `0 / 5`
- Approach ordinary-feasibility passes: `0 / 5`
- Trajectory-after-approach passes: `0 / 5`
- Full staged-feasibility passes: `0 / 5`

## Rows

| case | terminal budget failed | final orient | qdot sat | drift m | normal slack | force err N | trajectory after |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `pp_kp2_a0p35_n10_4s` | contact_present_fraction;tail_mean_abs_force_error_N;max_abs_normal_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization | `0.0017768432101110674` | `0.9235` | `1.9531942401696326e-05` | `0.0034414195124211782` | `5.0` | `False` |
| `pp_kp2_a0p35_n100_4s` | terminal_orientation;tail_mean_abs_force_error_N;max_abs_normal_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization;max_angular_velocity_slack_rad_s | `0.06864583059182422` | `0.923` | `0.000211221375408294` | `0.0007202393756496103` | `2.1082523243052753` | `False` |
| `pp_kp2_a0p35_n1000_4s` | terminal_orientation;qdot_saturation_fraction;tail_max_qdot_utilization;max_angular_velocity_slack_rad_s | `0.07398431554093947` | `0.924` | `1.818489728897324e-05` | `7.932092216135997e-06` | `0.009879165281529831` | `False` |
| `pp_kp2_a0p50_n100_4s` | terminal_orientation;tail_mean_abs_force_error_N;max_abs_normal_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization;max_angular_velocity_slack_rad_s | `0.0684460435312527` | `0.908` | `0.00021667148066177415` | `0.0007172576372811926` | `2.20126388185431` | `False` |
| `pp_kp1_a0p35_n100_8s` | terminal_orientation;tail_mean_abs_force_error_N;max_abs_normal_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization;max_angular_velocity_slack_rad_s | `0.07151974250780353` | `0.90075` | `0.00014456150912877525` | `0.0003860123894250379` | `0.7095111442795621` | `False` |
