# Paper 7DOF Tuned Figure-Match Candidate Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v52-python-figure-match-candidate`

## Scope

This branch implements a separately labeled Python candidate for the legacy
`figure_match` line. It intentionally uses audited non-paper-faithful tuning:
`pinv_bounded`, `normal_only`, `admittance_proxy`, aggressive soft-limit
escape velocity, high position gain, and q7 nullspace bias.

This is a tuned landmark reproduction candidate, not a formula-faithful
paper-equivalent parity claim.

## Run

- Command:
  `scripts/run_paper_7dof_section_v.py --figure-match-preset --duration-s 30 --dt-s 0.001`
- Output:
  `runs/paper_7dof_section_v/20260524T134441`
- Code commit recorded by the run:
  `2f65a5908528670868ed5d9e4ffab9f8443b77a2`
- Git state at run time:
  clean

Tracked lightweight artifacts:

- `metrics.yaml`
- `metrics.json`
- `summary.md`

Ignored raw artifact:

- `paper_7dof_section_v_raw.npz`

## Result

The Python tuned figure-match candidate executes with hard joint and velocity
bounds and reproduces the legacy Fig.6 q7 landmark:

```text
execution_success = true
contact_force_tail_success = true
claim_level = paper_platform_7dof_tuned_figure_match_candidate
solver_mode = pinv_bounded
orientation_mode = normal_only
force_loop_mode = admittance_proxy
force_integral_limit = 5.0
force_integral_leak = 1.5
q7_nullspace_speed_rad_s = 0.35
escape_velocity_alpha = 20.0
kp = 25.0
max_angular_speed_rad_s = 1.5
fig6_q7_at_22s_rad = 2.4999999999331863
fig6_q7_abs_error_to_2p5_rad = 6.681366571115177e-11
tail_force_error_mean_N = 0.0004629648106931554
tail_position_error_mean_m = 0.0012460142796336512
tail_orientation_error_mean_rad = 2.7169713442019066e-06
```

## Claim Boundary

This result closes the Python implementation gap for the tuned figure-match
q7 landmark, but it does not convert the tuned line into a paper-faithful
controller. The line should remain separate from the v51 formula-convergence
claim.

## Next Step

Run a raw-provenance comparison against the legacy MATLAB/RNN
`figure_match_fig6_results.mat` using this Python candidate, then update the
completion audit and parity-claim reports with the measured q7 trajectory
relationship.
