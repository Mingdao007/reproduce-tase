# Strict Vs Diagnostic Margin Separation Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v137-strict-diagnostic-margin-separation`

Run: `runs/strict_vs_diagnostic_margin_separation/20260525T124000`

## Scope

This v137 audit is a post-hoc offline comparison over existing v85, v126, and
v136 metrics. It checks that the small v85 diagnostic orientation/contact
definition margin is not confused with the much larger v126 strict-terminal
relaxation gap, while preserving the v136 completion boundary.

The audit does not run a new optimizer, rerun MuJoCo, collect hardware data, or
change any accepted gate.

## Result

Key metrics:

```text
audit_passed = true
strict_vs_diagnostic_margin_separation_complete = true
diagnostic_required_normal_rotation_rad = 0.0005664520369604714
diagnostic_required_normal_rotation_deg = 0.03245531101442353
strict_orientation_increase_rad = 0.0335984782867086
strict_tangential_increase_m = 0.0019405568802957048
strict_force_increase_N = 0.01697482058387756
strict_to_diagnostic_orientation_margin_ratio = 59.31389790209757
minimum_uniform_multiplier = 2.11994927622362
minimum_uniform_case_id = xy_force_orientation__best_candidate__slsqp
minimum_uniform_requires_all_three_scalar_gates = true
v85_margin_can_close_strict_orientation = false
v85_margin_can_close_strict_uniform_relaxation = false
v85_margin_can_close_strict_paper_equivalent_goal = false
accepted_measurement_noise_budget_exists = false
replacement_gate_accepted = false
approved_read_only_run_count = 0
approved_read_only_audit_passed_count = 0
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

Scale comparison:

| Quantity | Value |
| --- | ---: |
| v85 diagnostic normal-rotation margin | `0.0005664520369604714 rad` |
| v126 strict-terminal orientation increase | `0.0335984782867086 rad` |
| Strict/diagnostic orientation ratio | `59.31389790209757` |
| v126 force increase still required | `0.01697482058387756 N` |
| v126 tangential increase still required | `0.0019405568802957048 m` |

## Interpretation

The v85 diagnostic margin is a small orientation/contact definition margin for
the weighted diagnostic row. It is not large enough to close the v126
strict-terminal orientation gap, and the strict best uniform row also needs
force and tangential relaxation. The diagnostic calibration path therefore
remains separate from any strict paper-equivalent feasibility claim.

The v136 completion gate is still binding: the repository has no approved
read-only run and no passed approved-read-only audit.

## Validation

- `python3 -m py_compile scripts/audit_strict_vs_diagnostic_margin_separation.py`
- `scripts/run_tests.sh tests/test_strict_vs_diagnostic_margin_separation.py`
  reported `4 passed in 0.17s`.
- `python3 scripts/audit_strict_vs_diagnostic_margin_separation.py --run-id 20260525T124000`
- Temporary verifier rerun:
  `python3 scripts/audit_strict_vs_diagnostic_margin_separation.py --output-dir /tmp/tase_v137_margin_verify --run-id VERIFY_V137`
- Full tests passed with `255 passed in 29.95s`.
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads.
- `git diff --check` passed.

## Limit

This is offline bookkeeping over existing metrics only. It does not collect
live measurements, approve a read-only SOP step, create repository approved
calibration evidence, accept a contact model, accept a setup target, relax a
gate, prove strict paper-equivalent feasibility, prove robustness, establish
hardware readiness, or authorize hardware work.
