# Paper Platform Claim Boundary Audit

Run id: `20260525T103000`

Audit passed: `True`
Formula convergence claim allowed: `True`
Tuned figure-match claim allowed: `True`
Strict paper-equivalent claim allowed: `False`
Claim lines collapsed: `False`
Do not mark goal complete: `True`

Claim rows:

| Claim | Allowed | Boundary |
| --- | ---: | --- |
| `paper_platform_7dof_formula_convergence` | `True` | Formula-faithful Python candidate passes formula-convergence checks but does not claim Fig.6 q-trajectory parity. |
| `paper_platform_7dof_tuned_figure_match_candidate` | `True` | Separate tuned Python candidate matches the legacy Fig.6 q7 landmark with documented non-paper-faithful tuning. |
| `paper_platform_7dof_legacy_strict_all_checks` | `False` | Full paper-equivalent numerical parity remains unclaimed unless the strict aggregate is independently updated and accepted. |

Violations:

- None

Interpretation:

The formula-convergence and tuned Fig.6 evidence lines remain separate. Full paper-equivalent numerical parity and UR10e hardware readiness remain unclaimed.
