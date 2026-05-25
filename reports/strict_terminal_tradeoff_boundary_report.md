# Strict Terminal Tradeoff Boundary Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v125-strict-terminal-tradeoff-boundary`

Run: `runs/strict_terminal_tradeoff_boundary/20260525T104000`

## Scope

This v125 audit is a post-hoc offline analysis of the existing v116 strict
terminal constrained-optimization rows. It does not run a new optimizer or a
new MuJoCo experiment. Its purpose is to make the current strict terminal
tradeoff explicit without upgrading it into strict feasibility evidence.

## Result

Key metrics:

```text
audit_passed = true
strict_terminal_pass_count = 0
optimization_case_count = 12
best_combined_case_id = xy_force_orientation__best_candidate__slsqp
best_combined_max_gate_ratio = 2.11994927622362
best_combined_failed_all_three_scalar_gates = true
force_xy_without_orientation_count = 1
xy_orientation_without_force_or_contact_count = 2
tradeoff_boundary_preserved = true
new_optimization_run = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

Best combined row:

| Criterion | Ratio | Actual |
| --- | ---: | ---: |
| `force_error_N` | `1.0678992823355102` | `0.26697482058387756 N` |
| `tangential_error_m` | `1.9702784401478524` | `0.003940556880295705 m` |
| `orientation_error_rad` | `2.11994927622362` | `0.0635984782867086 rad` |

Tradeoff examples:

| Row | What passes | What remains blocked |
| --- | --- | --- |
| `xy_force__best_candidate__l-bfgs-b` | Force, x/y, contact, joint limits | Orientation ratio `4.899002392744376` |
| `xy_orientation__best_candidate__slsqp` | X/y and orientation | Force ratio `20.0` and no target contact |

## Interpretation

The existing v116 optimized rows show a terminal tradeoff rather than a hidden
strict pass. Force and x/y can be recovered together only by violating the
orientation gate. X/y and orientation can be recovered together only without
the required force/contact. The best combined row remains outside all three
scalar strict terminal gates.

## Validation

- `python3 -m py_compile scripts/audit_strict_terminal_tradeoff_boundary.py`
- `scripts/run_tests.sh tests/test_strict_terminal_tradeoff_boundary.py`
  reported `3 passed in 0.24s`.
- `python3 scripts/audit_strict_terminal_tradeoff_boundary.py --run-id 20260525T104000`
- YAML anchor check found no anchors in
  `runs/strict_terminal_tradeoff_boundary/20260525T104000/metrics.yaml`.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v125 run
  directory.
- Full tests passed with `208 passed in 11.32s`.
- `git diff --check` passed.

## Limit

This is offline bookkeeping over existing v116 rows only. It does not collect
live measurements, run a new optimizer, accept a contact/setup target, relax a
gate, prove strict paper-equivalent feasibility, prove robustness, establish
UR10e hardware readiness, or authorize hardware work.
