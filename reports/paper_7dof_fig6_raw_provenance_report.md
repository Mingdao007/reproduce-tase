# Paper 7DOF Fig.6 Raw Provenance Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v49-paper-fig6-raw-provenance-audit`

## Scope

This branch compares the current Python paper-platform Fig.6 candidate with
ignored local legacy MATLAB/RNN raw Fig.6 arrays. The goal is to determine
whether the remaining q7-at-22 s mismatch is a Python Panda kinematics
porting issue or a provenance difference between the formula-faithful and
figure-match legacy lines.

Raw `.mat` and `.npz` arrays remain outside ordinary Git. This report and the
run folder record derived lightweight metrics only.

## Run

- Command:
  `scripts/compare_paper_7dof_fig6_raw_provenance.py`
- Output:
  `runs/paper_7dof_fig6_raw_provenance/20260524T123130`
- Code commit recorded by the run:
  `b5941061881fd5962e4b2504b40d1f0f61575704`
- Git state at run time:
  clean

## Inputs

- Legacy root:
  `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2`
- Legacy source files:
  `forward_panda.m`, `getJacobian_panda.m`
- Legacy raw Fig.6 files:
  `formula_faithful_fig6_results.mat`, `figure_match_fig6_results.mat`
- Python raw candidate:
  `runs/paper_7dof_section_v/20260524T121503/paper_7dof_section_v_raw.npz`

## Result

- `python_fk_matches_sampled_legacy_raw = true`
- Legacy formula-faithful force loop: `paper_literal`
- Legacy figure-match force loop: `admittance_proxy`
- Python candidate force loop: `paper_literal`
- Legacy formula-faithful q7 at 22 s: `1.1241793710124022 rad`
- Legacy figure-match q7 at 22 s: `2.4999999999358065 rad`
- Python candidate q7 at 22 s: `1.6680622878116045 rad`
- Python absolute delta to figure-match q7: `0.831937712124202 rad`
- Python absolute delta to formula-faithful q7: `0.5438829167992023 rad`
- Legacy figure-match exact upper-limit q7 samples: `17829`
- Legacy figure-match first near-upper-limit q7 time: `11.872999999998859 s`
- Legacy figure-match acceptance mode: `landmark`

Kinematics source checks:

| Legacy run | max position error m | max quaternion delta norm | max condJ error |
| --- | ---: | ---: | ---: |
| `legacy_formula_faithful` | `0.0` | `1.1274399064233892e-16` | `8.881784197001252e-15` |
| `legacy_figure_match` | `1.1102230246251565e-16` | `1.1485179310268942e-16` | `6.217248937900877e-15` |

Joint trajectory comparisons:

| Reference | Candidate | q7 delta at 22 s rad | q7 RMSE rad | joint RMSE rad |
| --- | --- | ---: | ---: | ---: |
| `legacy_formula_faithful` | `python_v47_uncapped_kkt` | `0.5438829167992287` | `0.5680000838185039` | `0.23473749435738336` |
| `legacy_figure_match` | `python_v47_uncapped_kkt` | `-0.8319377121241756` | `0.7395891219830576` | `0.6121241447298901` |
| `legacy_formula_faithful` | `legacy_figure_match` | `1.3758206289234043` | `1.2905082815516138` | `0.6776166090314514` |

## Interpretation

The Python Panda DH/FK/Jacobian port matches the sampled legacy raw states to
numerical precision. The remaining q7 mismatch is therefore not explained by
a simple Python kinematics porting error.

The legacy `figure_match` q7 landmark is produced by a documented
figure-matching line with `pinv_bounded`, `normal_only`, `admittance_proxy`,
and `landmark` acceptance mode. It pins q7 near the upper limit from about
`11.873 s` onward. The formula-faithful line and the Python candidate both use
`paper_literal` force-loop semantics and do not pin q7 at the upper limit.

## Gate Implication

The strict parity gate should continue to fail until the project decides how
to treat the figure-match q7 landmark: either reproduce and justify the
`admittance_proxy` figure-match line in Python as a separate tuned landmark
candidate, or revise the strict paper-platform gate to make the
formula-faithful line primary and keep figure-match q7 as provenance evidence
rather than a paper-equivalence requirement.

## Next Step

Audit the legacy `admittance_proxy` force loop and figure-match tuning source,
then decide whether to implement that line in Python as a separate
figure-matching candidate or change the strict parity gate claim structure.
