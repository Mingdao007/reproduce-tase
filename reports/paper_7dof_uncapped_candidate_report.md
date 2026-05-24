# Paper 7DOF Uncapped Candidate Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v47-paper-7dof-q7-variant-probe`

## Scope

This branch removes the finite force-integral cap from the current Python 7DOF
paper-platform candidate while keeping the KKT projection, force-normal
shortest-arc orientation interpretation, 30 s duration, and Section V hard
q/qdot bounds.

The goal is to check whether the cap was still a strict-parity blocker after
the v45/v46 duration and Fig.5 coverage work.

## Run

- Command:
  `scripts/run_paper_7dof_section_v.py --duration-s 30.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-leak 0.0`
- Output:
  `runs/paper_7dof_section_v/20260524T121503`
- Code commit recorded by the run:
  `d4884d79c3e0702228e11205976bb8dc506e4472`
- Git state at run time:
  clean
- Ignored raw artifact:
  `runs/paper_7dof_section_v/20260524T121503/paper_7dof_section_v_raw.npz`

## Result

- `execution_success = true`
- `contact_force_tail_success = true`
- `duration_s = 30.0`
- `tail_contact_fraction = 1.0`
- `tail_force_error_mean_N = 0.023282898803479644`
- `tail_position_error_mean_m = 0.0005087140069982723`
- `tail_orientation_error_mean_rad = 5.032735496157772e-05`
- `q_bound_violation_count = 0`
- `qdot_bound_violation_count = 0`
- `force_integral_limit = .inf`
- `fig6_q7_at_22s_rad = 1.6680622878116045`
- `fig6_q7_abs_error_to_2p5_rad = 0.8319377121883955`

## Gate Effect

The v47 parity evaluation at
`runs/paper_platform_parity_eval/20260524T121542` changes
`paper_assumption_compatibility` from `false` to `true`.

Strict parity remains failed only because:

- `fig6_q7_22s_landmark = false`

## Interpretation

The finite force-integral cap is no longer needed for the current 30 s KKT
paper-platform diagnostic to pass execution, force/contact tail behavior, and
hard bounds. Removing the cap does not fix the q7 landmark; q7 at 22 s remains
far below the figure-match legacy value of `2.5 rad`.

## Next Step

Investigate the q7-at-22 s mismatch directly. The remaining candidate causes
are model/provenance, redundancy/nullspace behavior, or differences between
the formula-faithful and figure-match legacy lines.
