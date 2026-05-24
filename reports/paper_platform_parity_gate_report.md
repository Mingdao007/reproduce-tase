# Paper Platform Parity Gate Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v49-paper-fig6-raw-provenance-audit`

## Scope

This report defines and applies the strict paper-platform parity gate for the
separate Python 7DOF Section V diagnostic line. The current gate compares the
v47 uncapped Python KKT candidate against the migrated legacy
MATLAB/RNN verification outputs without upgrading the claim to
paper-equivalent parity.

## Inputs

- Candidate Python run:
  `runs/paper_7dof_section_v/20260524T121503/metrics.yaml`
- Candidate raw arrays when present locally:
  `runs/paper_7dof_section_v/20260524T121503/paper_7dof_section_v_raw.npz`
- Formula-faithful legacy reference:
  `runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_formula_faithful/paper_method_formula_faithful_verification.md`
- Figure-match legacy reference:
  `runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_figure_match/paper_method_figure_match_verification.md`
- Gate config:
  `configs/paper_platform_parity.yaml`
- Gate output:
  `runs/paper_platform_parity_eval/20260524T121542`
- q7 variant probe output:
  `runs/paper_7dof_q7_variant_probe/20260524T122345`
- raw Fig.6 provenance output:
  `runs/paper_7dof_fig6_raw_provenance/20260524T123130`

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
  `0.023282898803479644 N` vs `0.0476436 N`, delta
  `0.024360701196520358 N`, tolerance `0.05 N`.
- Candidate tail position error against formula-faithful reference:
  `0.0005087140069982723 m` vs `0.000583872 m`, delta
  `7.515799300172779e-05 m`, tolerance `0.001 m`.
- Candidate tail orientation error against formula-faithful reference:
  `5.032735496157772e-05 rad` vs `7.42197e-05 rad`, delta
  `2.389234503842228e-05 rad`, tolerance `0.0001 rad`.
- Duration coverage passes: candidate duration is `30.0 s`, required duration
  is `30.0 s`.
- Fig.5 r-sweep coverage passes: the gate validates one metrics file for each
  required r value over the required `2.0 s` window.
- Paper-assumption compatibility passes: `force_integral_limit = .inf`.

Failing checks:

- Fig.6 q7-at-22 s landmark fails: the Python candidate has
  `q7 = 1.6680622878116045 rad` at `22.0 s`; the figure-match reference is
  `2.5 rad`, so the absolute delta is `0.8319377121883955 rad` against a
  `0.05 rad` tolerance.

## Claim Boundary

The Python candidate now has a formal partial result: its 30 s run covers the
Fig.6 duration, its tail convergence metrics are close to the formula-faithful
legacy MATLAB/RNN reference under the configured tolerances, and Python Fig.5
r-sweep coverage is present. It no longer relies on the finite force-integral
cap. It still cannot be called paper-equivalent numerical parity because the
strict gate fails on the Fig.6 q7 landmark.

The v48 q7 variant probe checks the supported Python solver, orientation, and
force-integral-cap variants without changing the gate. Across eight full
30 s rows, q7 at 22 s remains in `1.661263839866546-1.6835894792145727 rad`;
`0 / 8` rows are within the `0.05 rad` tolerance of the `2.5 rad`
figure-match reference.

The v49 raw Fig.6 provenance audit checks whether this is a Python kinematics
porting problem. Python Panda FK and Jacobian conditioning match sampled
legacy raw states to numerical precision. The `2.5 rad` q7 landmark is
instead tied to the legacy `figure_match` line, which uses `pinv_bounded`,
`normal_only`, `admittance_proxy`, and `landmark` acceptance. That raw
trajectory pins q7 at the upper limit for `17829` samples and first nears the
upper limit at `11.872999999998859 s`.

## Next Step

To pursue paper-platform parity, audit the legacy `admittance_proxy` force
loop and figure-match tuning source, then decide whether to implement it as a
separate Python landmark candidate or revise the strict parity gate's claim
structure. Keep this path separate from UR10e adapted simulation and hardware
readiness claims.
