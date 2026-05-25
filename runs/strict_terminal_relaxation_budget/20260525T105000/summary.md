# Strict Terminal Relaxation Budget Audit

Run id: `20260525T105000`

Audit passed: `True`
Strict terminal pass count: `0`
Minimum uniform multiplier: `2.11994927622362`
Minimum uniform case: `xy_force_orientation__best_candidate__slsqp`
Minimum uniform requires all three scalar gates: `True`
Best single-scalar multiplier: `4.899002392744376`
Orientation-only case: `xy_force__best_candidate__l-bfgs-b`
Contactless xy+orientation rows: `2`
Relaxation acceptance allowed: `False`
Do not mark goal complete: `True`

Minimum uniform relaxation row:

| Criterion | Multiplier | Increase |
| --- | ---: | ---: |
| `force_error_N` | `1.0678992823355102` | `0.01697482058387756` |
| `tangential_error_m` | `1.9702784401478524` | `0.0019405568802957048` |
| `orientation_error_rad` | `2.11994927622362` | `0.0335984782867086` |

Best single-scalar relaxation row:

- Case: `xy_force__best_candidate__l-bfgs-b`
- Failed scalar criteria: `['orientation_error_rad']`
- Required multipliers: `{'force_error_N': 1.0, 'tangential_error_m': 1.0, 'orientation_error_rad': 4.899002392744376}`

Scale comparison:

- Strict orientation increase: `0.0335984782867086`
- V85 diagnostic required normal rotation: `0.0005664520369604714`
- Ratio: `59.31389790209757`

Violations:

- None

Interpretation:

The existing strict-terminal rows would require substantial non-accepted scalar gate relaxation. The smallest uniform budget still scales force, x/y, and orientation together, while the single-scalar recovery path needs a much larger orientation relaxation. This audit accepts no relaxation and creates no strict feasibility evidence.
