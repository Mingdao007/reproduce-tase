# Paper Platform Split Evidence Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v52-python-figure-match-candidate`

## Scope

This report is the current paper-platform claim contract. It prevents two
different evidence lines from being collapsed into one full
paper-equivalent-parity claim.

## Evidence Lines

| Claim | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| `paper_platform_7dof_formula_convergence` | Pass | `runs/paper_platform_parity_eval/20260524T124200/metrics.yaml` | Formula-faithful Python candidate passes execution/contact/bounds, duration, Fig.5 coverage, uncapped force-integral assumption, and tail convergence against the formula-faithful legacy reference. It does not reproduce Fig.6 q-trajectory parity. |
| `paper_platform_7dof_tuned_figure_match_candidate` | Pass | `runs/paper_7dof_section_v/20260524T134441/metrics.yaml` and `runs/paper_7dof_fig6_raw_provenance/20260524T134549/metrics.yaml` | Separate Python candidate reproduces the legacy tuned figure-match q7 trajectory using `admittance_proxy`, `normal_only`, `pinv_bounded`, `alpha = 20.0`, `kp = 25.0`, and `q7_nullspace_speed_rad_s = 0.35`. It is not formula-faithful paper parity. |
| `paper_platform_7dof_legacy_strict_all_checks` | Not claimed | v51 strict aggregate remains false for the formula candidate; v52 tuned candidate is separate non-paper-faithful evidence | Do not call the current state full paper-equivalent numerical parity or Fig.6 q-trajectory parity of the formula-faithful controller. |

## Accepted Wording

Use:

```text
The current repository has split paper-platform evidence: the formula-faithful
Python line passes formula-convergence checks, and a separate tuned Python
figure-match line reproduces the legacy Fig.6 q7 landmark. Full
paper-equivalent numerical parity remains unclaimed.
```

Do not use:

```text
The paper-platform reproduction fully passes.
The formula-faithful controller reproduces Fig.6 q trajectories.
The tuned figure-match line proves the paper equations.
```

## Next Step

For paper-platform reporting, keep this split contract. For the broader UR10e
project, the next executable technical step is to validate or replace the
approximate UR10e TCP/contact model and rerun the terminal setup audit before
any hardware gate.
