# Paper 7DOF q7 Variant Probe Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v48-paper-7dof-q7-mismatch-probe`

## Scope

This branch tests whether the remaining Fig.6 q7-at-22 s mismatch is
sensitive to the supported Python paper-platform variants:

- solver: `kkt_projection` vs `pinv_bounded`
- orientation: `force_shortest_arc` vs `normal_only`
- force integral: uncapped vs `0.1` cap

This is a diagnostic sensitivity probe. It does not change the strict parity
gate or upgrade the paper-platform claim.

## Run

- Command:
  `scripts/run_paper_7dof_q7_variant_probe.py --duration-s 30.0 --dt-s 0.002 --communication-delay-s 0.032 --force-integral-leak 0.0`
- Output:
  `runs/paper_7dof_q7_variant_probe/20260524T122345`
- Code commit recorded by the run:
  `48683797d62c4bbee0d8e1dbaeaacd5a4c545b68`
- Git state at run time:
  clean

## Result

- `variant_count = 8`
- `all_execution_success = true`
- `all_q7_available = true`
- `q7_min_rad = 1.661263839866546`
- `q7_max_rad = 1.6835894792145727`
- `q7_range_rad = 0.02232563934802667`
- `figure_match_q7_rad = 2.5`
- `figure_match_tolerance_rad = 0.05`
- `figure_match_pass_count = 0`
- closest variant: `pinv_force_cap0p1`
- closest variant q7: `1.6835894792145727 rad`
- closest variant absolute error to figure-match: `0.8164105207854273 rad`

| Variant | q7 at 22 s rad | Delta to figure-match rad | Tail force error N |
| --- | ---: | ---: | ---: |
| `kkt_force_uncapped` | `1.6680622878116045` | `0.8319377121883955` | `0.023282898803479644` |
| `kkt_force_cap0p1` | `1.6755097668200787` | `0.8244902331799213` | `0.07253258857158651` |
| `kkt_normal_uncapped` | `1.6677473123331963` | `0.8322526876668037` | `0.023240532668525615` |
| `kkt_normal_cap0p1` | `1.6751976272672546` | `0.8248023727327454` | `0.07246008363175997` |
| `pinv_force_uncapped` | `1.6818497721293582` | `0.8181502278706418` | `0.0006321261374228985` |
| `pinv_force_cap0p1` | `1.6835894792145727` | `0.8164105207854273` | `0.003688206107040649` |
| `pinv_normal_uncapped` | `1.661263839866546` | `0.838736160133454` | `0.006717510310330816` |
| `pinv_normal_cap0p1` | `1.6821932683797627` | `0.8178067316202373` | `0.003690067691211803` |

## Interpretation

The q7 mismatch is not explained by the tested solver mode, orientation mode,
or force-integral-cap choice. All supported variants remain clustered around
`1.66-1.68 rad` at `22 s`, while the legacy figure-match reference is
`2.5 rad`.

The current strict parity gate remains failed only on the Fig.6 q7 landmark.
The next likely causes are Panda/Franka model provenance, redundancy/nullspace
behavior not represented by the current Python line, or the legacy
figure-match tuning path itself.

## Next Step

Compare the Python Panda kinematics and q trajectory against the legacy MATLAB
`forward_panda.m`, `getJacobian_panda.m`, and raw Fig.6 `.mat` data, or audit
the source of the legacy figure-match q7 landmark before changing the parity
candidate.
