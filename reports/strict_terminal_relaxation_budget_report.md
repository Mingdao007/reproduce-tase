# Strict Terminal Relaxation Budget Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v126-strict-terminal-relaxation-budget`

Run: `runs/strict_terminal_relaxation_budget/20260525T105000`

## Scope

This v126 audit is a post-hoc offline budget calculation over the existing
v116 strict-terminal optimization rows and v125 tradeoff boundary. It does not
run a new optimizer or a new MuJoCo experiment. Its purpose is to quantify the
scalar gate relaxation that would be required by the existing rows, while
explicitly accepting no relaxation.

## Result

Key metrics:

```text
audit_passed = true
strict_terminal_pass_count = 0
eligible_scalar_relaxation_row_count = 9
minimum_uniform_multiplier = 2.11994927622362
minimum_uniform_case_id = xy_force_orientation__best_candidate__slsqp
minimum_uniform_requires_all_three_scalar_gates = true
orientation_only_relaxation_case_id = xy_force__best_candidate__l-bfgs-b
orientation_only_multiplier = 4.899002392744376
contactless_xy_orientation_row_count = 2
relaxation_budget_acceptance_allowed = false
new_optimization_run = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

Minimum uniform relaxation row:

| Criterion | Multiplier | Increase |
| --- | ---: | ---: |
| `force_error_N` | `1.0678992823355102` | `0.01697482058387756 N` |
| `tangential_error_m` | `1.9702784401478524` | `0.0019405568802957048 m` |
| `orientation_error_rad` | `2.11994927622362` | `0.0335984782867086 rad` |

Best single-scalar relaxation row:

| Row | Passing criteria | Required relaxation |
| --- | --- | --- |
| `xy_force__best_candidate__l-bfgs-b` | Force, x/y, target contact, joint limits | Orientation multiplier `4.899002392744376`; increase `0.11697007178233126 rad` |

The strict best-combined orientation increase is `0.0335984782867086 rad`,
which is `59.31389790209757` times the v85 diagnostic required normal
rotation (`0.0005664520369604714 rad`). This comparison is scale context only;
it does not justify changing any strict gate.

## Interpretation

The existing strict-terminal rows would need substantial non-accepted gate
relaxation. The smallest uniform budget still requires force, x/y, and
orientation gates to move together. The best single-scalar recovery path needs
a much larger orientation relaxation. Rows that recover x/y and orientation
without scalar relaxation lose the required target contact and force.

## Validation

- `python3 -m py_compile scripts/audit_strict_terminal_relaxation_budget.py`
- `scripts/run_tests.sh tests/test_strict_terminal_relaxation_budget.py`
  reported `3 passed in 0.28s`.
- `python3 scripts/audit_strict_terminal_relaxation_budget.py --run-id 20260525T105000`
- YAML anchor check found no anchors in
  `runs/strict_terminal_relaxation_budget/20260525T105000/metrics.yaml`.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v126 run
  directory.
- Full tests passed with `211 passed in 11.65s`.
- `git diff --check` passed.

## Limit

This is offline bookkeeping over existing rows only. It does not collect live
measurements, run a new optimizer, accept a contact/setup target, relax a gate,
prove strict paper-equivalent feasibility, prove robustness, establish UR10e
hardware readiness, or authorize hardware work.
