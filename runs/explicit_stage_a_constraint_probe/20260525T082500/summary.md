# Explicit Stage A Constraint Probe Summary

Run root: `runs/explicit_stage_a_constraint_probe/20260525T082500`

- Case count: `5`
- Strict setup-path pass count: `0 / 5`
- Terminal strict-criteria pass count: `0 / 5`
- Qdot-criteria pass count: `5 / 5`
- Planned setup-then-trajectory pass count: `0 / 5`
- Best score case: `diagnostic_contact_path_tracking_reference`
- Best qdot case: `diagnostic_contact_path_tracking_reference`
- Best x/y case: `terminal_xy_orientation_hold`
- Best orientation case: `terminal_xy_orientation_hold`

| case | setup path pass | failed criteria | qdot sat | tail qdot util | terminal xy m | terminal orient rad | terminal force N | contact frac |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `diagnostic_contact_path_tracking_reference` | `False` | `terminal_tangential_error_m;terminal_orientation_error_rad` | `0.0` | `0.9555090015209883` | `0.0030075762251302427` | `0.07240605683117463` | `0.005097546556703136` | `1.0` |
| `terminal_xy_force_hold` | `False` | `terminal_orientation_error_rad` | `0.0` | `0.9500000000000501` | `1.2984463881799684e-15` | `0.14697007178233126` | `2.4868995751603507e-14` | `1.0` |
| `terminal_xy_orientation_hold` | `False` | `terminal_force_error_N;path_target_contact_present_fraction` | `0.0` | `0.9500000000000741` | `5.204170427930421e-18` | `5.551115123125783e-17` | `5.0` | `0.011382113821138212` |
| `terminal_force_orientation_hold` | `False` | `terminal_tangential_error_m` | `0.0` | `0.9500000000000963` | `0.014127706733724453` | `3.608594916770049e-14` | `1.6253665080512292e-13` | `1.0` |
| `terminal_xy_force_orientation_soft_best` | `False` | `terminal_tangential_error_m;terminal_orientation_error_rad` | `0.0` | `0.9500000000000547` | `0.0030075787462736734` | `0.07240603326354965` | `0.005097551486581864` | `1.0` |

Interpretation:

- Qdot-timed paths can remove the v113/v114 setup qdot-saturation failure in all tested rows.
- Removing qdot saturation does not solve the strict terminal compatibility problem.
- The x/y plus orientation terminal row loses target contact and force; the force plus orientation row drifts in x/y.
- The best soft strict terminal compromise still fails strict x/y and orientation.
