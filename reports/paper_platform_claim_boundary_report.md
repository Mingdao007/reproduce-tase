# Paper Platform Claim Boundary Regression Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v124-paper-platform-claim-boundary-regression`

Run: `runs/paper_platform_claim_boundary/20260525T103000`

## Scope

This v124 audit is an offline regression check for the paper-platform claim
boundary. It verifies that the current evidence still supports two separate
partial paper-platform claims while keeping full paper-equivalent numerical
parity unclaimed.

## Result

| Claim | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| `paper_platform_7dof_formula_convergence` | Allowed | `runs/paper_platform_parity_eval/20260524T124200/metrics.yaml` | Formula-faithful Python candidate passes formula-convergence checks but does not claim Fig.6 q-trajectory parity. |
| `paper_platform_7dof_tuned_figure_match_candidate` | Allowed | `runs/paper_7dof_section_v/20260524T134441/metrics.yaml`, `runs/paper_7dof_fig6_raw_provenance/20260524T134549/metrics.yaml` | Separate tuned Python candidate matches the legacy Fig.6 q7 landmark with documented non-paper-faithful tuning. |
| `paper_platform_7dof_legacy_strict_all_checks` | Not allowed | `runs/paper_platform_parity_eval/20260524T124200/metrics.yaml` | Full paper-equivalent numerical parity remains unclaimed. |

Key metrics:

```text
audit_passed = true
formula_convergence_claim_allowed = true
tuned_figure_match_claim_allowed = true
strict_paper_equivalent_claim_allowed = false
claim_lines_collapsed = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

The tuned candidate remains explicitly non-paper-faithful: the audit requires
`admittance_proxy`, `normal_only`, `pinv_bounded`,
`escape_velocity_alpha = 20.0`, `kp = 25.0`,
`q7_nullspace_speed_rad_s = 0.35`, and finite
`force_integral_limit = 5.0`. Its q7 delta to the legacy figure-match line is
`2.6201263381153694e-12 rad`, while its q7 delta to the formula-faithful line
is `1.3758206289207842 rad`.

## Validation

- `python3 -m py_compile scripts/audit_paper_platform_claim_boundary.py`
- `scripts/run_tests.sh tests/test_paper_platform_claim_boundary.py`
  reported `4 passed in 0.17s`.
- `python3 scripts/audit_paper_platform_claim_boundary.py --run-id 20260525T103000`
- YAML anchor check found no anchors in
  `runs/paper_platform_claim_boundary/20260525T103000/metrics.yaml`.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v124 run
  directory.
- Full tests passed with `205 passed in 10.96s`.
- `git diff --check` passed.

## Limit

This is offline paper-platform bookkeeping only. It does not collect live
measurements, approve a read-only SOP step, accept a contact/setup target,
prove strict paper-equivalent feasibility, prove robustness, establish UR10e
hardware readiness, or authorize hardware work.
