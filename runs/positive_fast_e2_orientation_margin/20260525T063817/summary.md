# Positive Fast E2 Orientation-Margin Summary

Run root: `runs/positive_fast_e2_orientation_margin/20260525T063817`

- Scenario count: `6`
- E2 pass count: `2 / 6`
- Passing scenarios: `weighted_kp0_normal1, weighted_kp0_normal30`
- Best orientation scenario: `weighted_kp0_normal1`
- Minimum orientation error: `0.11954627160547111`

| scenario | priority | normal weight | orientation_kp | E2 pass | failed criteria | orientation | qdot sat | tail qdot | force err |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| `linear_kp0_normal1` | `linear_primary` | `1.0` | `0.0` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad` | `0.12020305872871904` | `0.999` | `1.0` | `0.006603888075066666` |
| `linear_kp0p003_normal1` | `linear_primary` | `1.0` | `0.003` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad` | `0.12022359024474283` | `0.032` | `1.0` | `0.0015347856938339398` |
| `planar_normal30_kp0p001` | `planar_primary` | `30.0` | `0.001` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.11983992753823672` | `0.072` | `1.0` | `0.20098660314203312` |
| `planar_normal30_kp0p002` | `planar_primary` | `30.0` | `0.002` | `False` | `tail_mean_abs_force_error_N` | `0.11972166555008389` | `0.001` | `0.0012133347645829611` | `0.275874931458737` |
| `weighted_kp0_normal1` | `weighted` | `1.0` | `0.0` | `True` | `none` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0008094383419582085` |
| `weighted_kp0_normal30` | `weighted` | `30.0` | `0.0` | `True` | `none` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0008094383419582085` |

Interpretation:

- The probe keeps `paper_time_scale = 0.0075`, `qdot_limit = 0.15 rad/s`, and the run-local `0.12 rad` orientation gate fixed.
- Passing rows are diagnostic priority-formulation evidence only; they do not make a canonical controller change or close the v99 failed cell.
- Any stronger claim still needs full failed-cell audit coverage and the unresolved contact/gate calibration blockers remain open.
