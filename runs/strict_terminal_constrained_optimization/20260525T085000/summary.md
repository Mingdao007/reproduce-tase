# Strict Terminal Constrained Optimization Summary

Run root: `runs/strict_terminal_constrained_optimization/20260525T085000`

- Optimization case count: `12`
- Strict terminal pass count: `0 / 12`
- Optimizer success count: `10 / 12`
- Best case: `xy_force_orientation__best_candidate__slsqp`
- Best max gate ratio: `2.11994927622362`
- V56 strict best max gate ratio: `2.413534442118322`
- Best ratio improvement: `0.29358516589470174`

| case | optimizer ok | gate pass | failed criteria | max gate ratio | force ratio | xy ratio | orient ratio | contact |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `xy_force_orientation__best_candidate__slsqp` | `True` | `False` | `force_error_N;tangential_error_m;orientation_error_rad` | `2.11994927622362` | `1.0678992823355102` | `1.9702784401478524` | `2.11994927622362` | `1` |
| `initial__slsqp` | `True` | `False` | `force_error_N;tangential_error_m;orientation_error_rad` | `2.1199534355232017` | `1.0651562089163171` | `1.9702984846146063` | `2.1199534355232017` | `1` |
| `xy_force__best_candidate__slsqp` | `True` | `False` | `force_error_N;tangential_error_m;orientation_error_rad` | `2.1199561761664807` | `1.0603783887443612` | `1.9703563053127906` | `2.1199561761664807` | `1` |
| `force_orientation__best_optimized_candidate__slsqp` | `True` | `False` | `force_error_N;tangential_error_m;orientation_error_rad` | `2.119960338759908` | `1.0662617291803258` | `1.9702791643569015` | `2.119960338759908` | `1` |
| `initial__l-bfgs-b` | `True` | `False` | `force_error_N;tangential_error_m;orientation_error_rad` | `2.1200296248275188` | `1.0711120088283401` | `1.9700893404388438` | `2.1200296248275188` | `1` |
| `xy_force_orientation__best_candidate__l-bfgs-b` | `True` | `False` | `force_error_N;tangential_error_m;orientation_error_rad` | `2.120062845984372` | `1.0675099199558495` | `1.9701202950720156` | `2.120062845984372` | `1` |
| `force_orientation__best_optimized_candidate__l-bfgs-b` | `True` | `False` | `force_error_N;tangential_error_m;orientation_error_rad` | `2.1200801859123124` | `1.0698812795802723` | `1.9711070407379156` | `2.1200801859123124` | `1` |
| `force_orientation__best_candidate__l-bfgs-b` | `False` | `False` | `tangential_error_m;orientation_error_rad` | `3.8265899667025325` | `0.007763812458286168` | `3.8265899667025325` | `2.9183993411163534` | `1` |
| `xy_force__best_candidate__l-bfgs-b` | `False` | `False` | `orientation_error_rad` | `4.899002392744376` | `9.947598300641403e-14` | `6.492231940899842e-13` | `4.899002392744376` | `1` |
| `xy_orientation__best_candidate__slsqp` | `True` | `False` | `force_error_N;target_contact_count` | `inf` | `20.0` | `2.6020852139652106e-15` | `1.8503717077085944e-15` | `0` |
| `xy_orientation__best_candidate__l-bfgs-b` | `True` | `False` | `force_error_N;target_contact_count` | `inf` | `20.0` | `2.6020852139652106e-15` | `1.8503717077085944e-15` | `0` |
| `force_orientation__best_candidate__slsqp` | `True` | `False` | `force_error_N;tangential_error_m;orientation_error_rad;target_contact_count` | `inf` | `20.0` | `3.8257347973091442` | `2.9185141714568066` | `0` |

Interpretation:

- The smooth-minimax optimizer improves the v56 best strict terminal ratio but still finds no strict pass.
- The best optimized row remains target-contacting, but force, x/y, and orientation are all still outside at least one strict threshold.
- This is terminal compatibility evidence only; no Stage A controller, Stage B trajectory, robustness, calibration, or hardware claim is made.
