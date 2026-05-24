# Paper Platform Parity Gate Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v44-paper-platform-parity-gate`

## Scope

This branch defines a strict paper-platform parity gate for the separate
Python 7DOF Section V diagnostic line. The gate compares the v43 Python
capped-integral KKT candidate against the migrated legacy MATLAB/RNN
verification outputs without upgrading the claim to paper-equivalent parity.

## Inputs

- Candidate Python run:
  `runs/paper_7dof_section_v/20260524T114736/metrics.yaml`
- Candidate raw arrays when present locally:
  `runs/paper_7dof_section_v/20260524T114736/paper_7dof_section_v_raw.npz`
- Formula-faithful legacy reference:
  `runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_formula_faithful/paper_method_formula_faithful_verification.md`
- Figure-match legacy reference:
  `runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_figure_match/paper_method_figure_match_verification.md`
- Gate config:
  `configs/paper_platform_parity.yaml`
- Gate output:
  `runs/paper_platform_parity_eval/20260524T115641`

## Gate Definition

The strict gate requires all of these checks to pass:

- Candidate execution, contact tail, and hard q/qdot bounds.
- Both legacy references pass their own verification and constraint checks.
- Python tail force, position, and orientation errors are within absolute
  bounds and within configured deltas of the formula-faithful reference.
- Candidate duration covers the legacy Fig.6 30 s simulation window.
- Candidate exposes the Fig.6 q7-at-22 s landmark and matches the
  figure-match reference within `0.05 rad`.
- Candidate exposes Fig.5 r-sweep coverage for `r = 0.2, 0.4, 0.6, 0.8, 1.0`.
- Candidate does not rely on the finite force-integral cap because that cap is
  not PDF-verified paper truth.

## Result

`paper_platform_parity_pass = false`

Passing checks:

- Candidate execution/contact/bounds pass.
- Formula-faithful and figure-match legacy references pass.
- Candidate tail force error against formula-faithful reference:
  `0.06720487008205062 N` vs `0.0476436 N`, delta
  `0.019561270082050615 N`, tolerance `0.05 N`.
- Candidate tail position error against formula-faithful reference:
  `0.00044122814610554124 m` vs `0.000583872 m`, delta
  `0.0001426438538944588 m`, tolerance `0.001 m`.
- Candidate tail orientation error against formula-faithful reference:
  `2.7345108152399078e-05 rad` vs `7.42197e-05 rad`, delta
  `4.6874591847600916e-05 rad`, tolerance `0.0001 rad`.

Failing checks:

- Duration coverage fails: candidate duration is `5.0 s`, required duration is
  `30.0 s`.
- Fig.6 q7-at-22 s landmark fails: the candidate raw arrays end at `5.000 s`.
- Fig.5 r-sweep coverage fails: no candidate Python 7DOF metrics are
  configured for `r = 0.2, 0.4, 0.6, 0.8, 1.0`.
- Paper-assumption compatibility fails: `force_integral_limit = 0.1` is a
  diagnostic anti-windup assumption, not PDF-verified paper truth.

## Claim Boundary

The Python v43 candidate now has a formal partial result: its tail convergence
metrics are close to the formula-faithful legacy MATLAB/RNN reference under
the configured tolerances. It still cannot be called paper-equivalent
numerical parity because the strict gate fails on duration, Fig.6 landmark,
Fig.5 sweep coverage, and the capped-integral assumption.

## Next Step

To pursue paper-platform parity, run or implement a 30 s Python 7DOF candidate
that records q7 at 22 s, add Python Fig.5 r-sweep outputs, and remove or
justify the finite force-integral cap from paper truth. Keep this path
separate from UR10e adapted simulation and hardware readiness claims.
