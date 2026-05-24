# Strict Feasibility Policy Probe Summary

Run root: `runs/strict_feasibility_policy_probe/20260525T073519`

- Case count: `8`
- Setup terminal-state pass count: `0 / 8`
- Trajectory feasibility pass count: `4 / 8`
- Planned setup-then-trajectory pass count: `0 / 8`
- Full staged feasibility pass count: `0 / 8`
- Best setup-score case: `linear_recenter_4_no_settle`
- Best tangential-error case: `linear_recenter_4_linear_settle_4`
- Best orientation-error case: `weighted_recenter_4_weighted_settle_2`

| case | setup pass | setup failed criteria | setup orientation rad | setup x/y m | setup score | trajectory pass | full pass |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| `baseline_no_recenter` | `False` | `final_tangential_position_error_m;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0020066885453873624` | `0.008331820021419366` | `102.18631817397498` | `True` | `False` |
| `linear_recenter_4_no_settle` | `False` | `final_orientation_error_rad;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.06145597706622979` | `0.0011999597171791256` | `100.06894073213962` | `False` | `False` |
| `linear_recenter_4_weighted_settle_1` | `False` | `final_tangential_position_error_m;tail_mean_abs_force_error_N;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.010778239789397223` | `0.0072283702782736416` | `104.2362076400481` | `True` | `False` |
| `linear_recenter_4_weighted_settle_2` | `False` | `final_tangential_position_error_m;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0033171930051022775` | `0.008185871326022855` | `102.11334382627673` | `True` | `False` |
| `linear_recenter_4_linear_settle_4` | `False` | `final_orientation_error_rad;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.07224261496880678` | `0.0001777515283299582` | `100.4284953288922` | `False` | `False` |
| `weighted_recenter_4_weighted_settle_2` | `False` | `final_tangential_position_error_m;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0019220380036386873` | `0.008340633692578243` | `102.19072500955443` | `True` | `False` |
| `weighted_recenter_high_planar_kp_4_2` | `False` | `final_tangential_position_error_m;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.012237589847266798` | `0.006937444956527452` | `101.48913064151665` | `False` | `False` |
| `linear_recenter_weighted_settle_high_planar_kp` | `False` | `final_orientation_error_rad;final_tangential_position_error_m;tail_mean_abs_force_error_N;qdot_saturation_fraction;tail_max_qdot_utilization` | `0.033578553216320674` | `0.004202949914517587` | `100.58365785495744` | `False` | `False` |

Interpretation:

- No tested Stage A policy satisfies the strict setup terminal-state gate.
- Weighted settling preserves orientation and force but gives back x/y recentering.
- Linear-primary settling preserves x/y but fails orientation and the following E2 trajectory.
- Aggressive planar retention reduces x/y drift but reintroduces orientation, force, and qdot pressure.
