# Paper 7DOF 30 s Candidate Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v45-paper-7dof-30s-candidate`

## Scope

This branch extends the Python 7DOF Section V diagnostic evidence from the
short 5 s contact-tail run to a 30 s candidate that covers the legacy Fig.6
simulation window and records the q7-at-22 s landmark in tracked metrics.

## Run

- Command:
  `scripts/run_paper_7dof_section_v.py --duration-s 30.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0`
- Output:
  `runs/paper_7dof_section_v/20260524T120439`
- Code commit recorded by the run:
  `51f76512449051d278abe8f8a75cd96ed45480c8`
- Git state at run time:
  clean
- Ignored raw artifact:
  `runs/paper_7dof_section_v/20260524T120439/paper_7dof_section_v_raw.npz`

## Result

- `execution_success = true`
- `contact_force_tail_success = true`
- `duration_s = 30.0`
- `sample_count = 15001`
- `tail_contact_fraction = 1.0`
- `tail_force_error_mean_N = 0.07253258857158651`
- `tail_position_error_mean_m = 0.0005112191438856145`
- `tail_orientation_error_mean_rad = 5.0892640898279366e-05`
- `q_bound_violation_count = 0`
- `qdot_bound_violation_count = 0`
- `fig6_q7_sample_time_s = 22.0`
- `fig6_q7_at_22s_rad = 1.6755097668200787`
- `fig6_q7_abs_error_to_2p5_rad = 0.8244902331799213`

## Interpretation

The 30 s run preserves the successful contact-tail behavior from v43 while
covering the full Fig.6 duration. It does not match the figure-match legacy
q7 landmark: the reference is `2.5 rad`, while the Python candidate gives
`1.6755097668200787 rad` at `22 s`.

This is stronger paper-platform diagnostic evidence, not paper-equivalent
numerical parity. The finite force-integral cap remains an adapted
anti-windup assumption.

## Next Step

The next paper-platform parity work should target the q7 landmark mismatch,
add Python Fig.5 r-sweep outputs, or justify/remove the force-integral cap
against paper truth.
