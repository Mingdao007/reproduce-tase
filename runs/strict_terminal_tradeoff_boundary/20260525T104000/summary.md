# Strict Terminal Tradeoff Boundary Audit

Run id: `20260525T104000`

Audit passed: `True`
Strict terminal pass count: `0`
Best combined row: `xy_force_orientation__best_candidate__slsqp`
Best combined max-gate ratio: `2.11994927622362`
Best combined fails all three scalar gates: `True`
Force+xy/contact without orientation rows: `1`
Xy+orientation without force/contact rows: `2`
Tradeoff boundary preserved: `True`
New optimization run: `False`
Do not mark goal complete: `True`

Best combined row ratios:

| Criterion | Ratio |
| --- | ---: |
| `force_error_N` | `1.0678992823355102` |
| `tangential_error_m` | `1.9702784401478524` |
| `orientation_error_rad` | `2.11994927622362` |

Tradeoff examples:

- Force+xy/contact without orientation: `xy_force__best_candidate__l-bfgs-b`
- Xy+orientation without force/contact: `xy_orientation__best_candidate__slsqp`

Violations:

- None

Interpretation:

The existing v116 optimization rows show a strict terminal tradeoff rather than a hidden pass: force/xy can be recovered at the cost of orientation, while xy/orientation can be recovered only without the required force/contact. This audit is post-hoc bookkeeping over existing rows and does not close strict feasibility.
