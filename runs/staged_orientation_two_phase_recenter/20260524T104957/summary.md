# Two-Phase Recenter Probe Summary

Run root: `runs/staged_orientation_two_phase_recenter/20260524T104957`

- Cases: `10`
- Setup terminal-state passes: `0 / 10`
- Trajectory feasibility passes: `4 / 10`
- Legacy trajectory-after-approach passes: `4 / 10`
- Planned setup-then-trajectory passes: `0 / 10`
- Full staged-feasibility passes: `0 / 10`

| case | setup pass | setup failed | setup orient | setup xy m | recenter force N | traj pass | traj orient | planned pass |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| `baseline_no_recenter` | `False` | `final_tangential_position_error_m` | `0.0020290714973557108` | `0.008347977658392892` | `None` | `True` | `0.0203545748607252` | `False` |
| `weighted_recenter_4s` | `False` | `final_tangential_position_error_m` | `0.0019417654495737476` | `0.008360473956959848` | `0.0018400756047352229` | `True` | `0.02025995207705162` | `False` |
| `lp_recenter_0p2s` | `False` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.006039879488210821` | `0.007569057342219271` | `1.400552924999047` | `True` | `0.02639072763347245` | `False` |
| `lp_recenter_0p3s` | `False` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.00853105574687911` | `0.0072102171132026795` | `1.55001710834636` | `True` | `0.0292611395207697` | `False` |
| `lp_recenter_0p4s` | `False` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.01106774413292786` | `0.006869050548521516` | `1.5740320031502257` | `False` | `0.032042070707147687` | `False` |
| `lp_recenter_1s` | `False` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.025158611518183098` | `0.005138335667478752` | `1.0513662147686107` | `False` | `0.04697943449746931` | `False` |
| `lp_recenter_2s` | `False` | `final_orientation_error_rad;final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.042531446608710555` | `0.003166655425799055` | `0.41587533900905554` | `False` | `0.06605196016208538` | `False` |
| `lp_recenter_4s` | `False` | `final_orientation_error_rad` | `0.06144921366675186` | `0.001202027969075075` | `0.07268453631886647` | `False` | `0.08828833304324712` | `False` |
| `lp_recenter_4s_pkp0p2` | `False` | `final_orientation_error_rad;final_tangential_position_error_m` | `0.036920046275825014` | `0.0038469273903788785` | `0.09516531574555645` | `False` | `0.059178088812845336` | `False` |
| `pp_recenter_1s` | `False` | `final_tangential_position_error_m;contact_present_fraction;tail_mean_abs_force_error_N` | `0.0002897152712036141` | `0.005069982952668492` | `5.0` | `False` | `0.047597452958071426` | `False` |
