# Strict Command-Limited Stage A Summary

Run root: `runs/strict_command_limited_stage_a/20260525T074557`

- Case count: `4`
- Strict setup-chain pass count: `0 / 4`
- Trajectory feasibility pass count: `2 / 4`
- Planned setup-then-trajectory pass count: `0 / 4`
- Best score case: `v113_reference_uncapped`
- Best qdot-saturation case: `v113_reference_uncapped`
- Best x/y case: `v113_reference_uncapped`
- Best orientation case: `angular_cap_0p01_low_planar_slow`

| case | setup chain pass | failed criteria | setup max qdot sat | setup orientation rad | setup x/y m | trajectory pass |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `v113_reference_uncapped` | `False` | `final_tangential_position_error_m;setup_max_qdot_saturation_fraction;setup_max_tail_qdot_utilization` | `1.0` | `0.0033171930051022775` | `0.008185871326022855` | `True` |
| `strict_qdot_uncapped_reference` | `False` | `final_tangential_position_error_m;setup_min_contact_present_fraction;setup_max_qdot_saturation_fraction;setup_max_tail_qdot_utilization` | `1.0` | `0.0033071069360462086` | `0.008186437167975314` | `True` |
| `angular_cap_0p02_low_force_longer` | `False` | `final_tangential_position_error_m;setup_min_contact_present_fraction;setup_max_qdot_saturation_fraction;setup_max_tail_qdot_utilization` | `1.0` | `0.0019390306197518306` | `0.008348543286142098` | `False` |
| `angular_cap_0p01_low_planar_slow` | `False` | `final_tangential_position_error_m;terminal_tail_mean_abs_force_error_N;setup_min_contact_present_fraction;setup_max_qdot_saturation_fraction;setup_max_tail_qdot_utilization` | `1.0` | `0.0003898438945537693` | `0.008476991494629436` | `False` |

Interpretation:

- Command limiting changes Stage A command generation before allocation, but no tested row satisfies the strict setup chain.
- Lower force gain and angular caps reduce some terminal force/orientation pressure but do not recover x/y recentering.
- The best qdot-saturation row still saturates far above the strict `0.01` fraction threshold.
