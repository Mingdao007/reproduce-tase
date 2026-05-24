# Paper Platform Split Claim Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v51-split-paper-parity-claims`

## Scope

This branch splits the paper-platform gate into explicit claim levels after
the v49-v50 provenance audits showed that the Fig.6 q7 landmark belongs to a
tuned figure-match line rather than the formula-faithful controller path.

The change does not make the legacy strict aggregate pass. It separates the
accepted formula-convergence evidence from the still-failing tuned
figure-match q7 landmark.

## Run

- Command:
  `scripts/evaluate_paper_platform_parity.py`
- Output:
  `runs/paper_platform_parity_eval/20260524T124200`
- Code commit recorded by the run:
  `bddf1dad1645199de92458616162291b6881aa4c`
- Git state at run time:
  clean

## Result

- `paper_platform_parity_pass = false`
- `paper_platform_formula_convergence_pass = true`
- `paper_platform_figure_match_landmark_pass = false`

Claim levels:

| Claim Level | Pass | Boundary |
| --- | ---: | --- |
| `formula_convergence` | `true` | Execution/contact/bounds, duration, Fig.5 coverage, uncapped force integral, and tail convergence against the formula-faithful legacy reference. Does not claim full q-trajectory or Fig.6 q7 landmark parity. |
| `figure_match_landmark` | `false` | Tuned legacy figure-match q7 landmark, kept separate because v49-v50 show explicit figure-match tuning. |
| `legacy_strict_all_checks` | `false` | Backward-compatible aggregate requiring both formula convergence and tuned figure-match q7 landmark. |

The current candidate passes all formula-convergence checks:

- candidate execution/contact/bounds
- formula-faithful legacy reference overall verification
- tail force, position, and orientation deltas against formula-faithful legacy
- `30.0 s` duration coverage
- Fig.5 r-sweep coverage
- uncapped force-integral paper-assumption compatibility

It still fails:

- `fig6_q7_22s_landmark`: candidate q7 is `1.6680622878116045 rad`,
  tuned figure-match reference is `2.5 rad`, delta is
  `0.8319377121883955 rad`.

## Claim Boundary

The project may now claim formula-convergence evidence for the Python
paper-platform line, but it must not call this full paper-equivalent numerical
parity. Full q-trajectory parity and the tuned figure-match q7 landmark remain
unachieved.

## Next Step

Either implement a separately labeled Python figure-match candidate with the
audited tuning knobs, or continue UR10e adapted work while keeping
formula-convergence and tuned landmark evidence separate.
