# Paper 7DOF Tuned Figure-Match Provenance Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v52-python-figure-match-candidate`

## Scope

This report compares the Python v52 tuned figure-match candidate against the
ignored local legacy MATLAB/RNN Fig.6 raw arrays. It verifies whether the new
Python candidate reproduces the legacy `figure_match` trajectory, not just the
single q7-at-22 s landmark.

Raw `.mat` and `.npz` arrays remain outside ordinary Git; tracked artifacts
record derived metrics only.

## Run

- Command:
  `scripts/compare_paper_7dof_fig6_raw_provenance.py --python-label python_v52_tuned_figure_match --python-raw-npz runs/paper_7dof_section_v/20260524T134441/paper_7dof_section_v_raw.npz --python-metrics-yaml runs/paper_7dof_section_v/20260524T134441/metrics.yaml`
- Output:
  `runs/paper_7dof_fig6_raw_provenance/20260524T134549`
- Code/artifact commit recorded by the run:
  `e52d3885e5e4db76be8d0c36f1358e489279d8a7`
- Git state at run time:
  clean

## Result

```text
python_fk_matches_sampled_legacy_raw = true
legacy_figure_force_loop_mode = admittance_proxy
python_force_loop_mode = admittance_proxy
legacy_figure_q7_at_22_s_rad = 2.4999999999358065
python_q7_at_22_s_rad = 2.4999999999331863
python_abs_delta_to_figure_q7_at_22_s_rad = 2.6201263381153694e-12
python_abs_delta_to_formula_q7_at_22_s_rad = 1.3758206289207842
legacy_figure_q7_exact_upper_limit_count = 17829
python q7 exact upper-limit count = 17830
legacy_figure_q7_first_near_upper_limit_time_s = 11.872999999998859
python q7 first near-upper-limit time = 11.873000000000001
legacy-vs-python figure-match joint RMSE = 6.081574510252252e-09 rad
legacy-vs-python figure-match q7 RMSE = 2.337566316043061e-11 rad
```

## Interpretation

The Python v52 candidate reproduces the legacy tuned figure-match trajectory
to numerical precision. This closes the "Python implementation of tuned
figure-match landmark" gap.

It also confirms the earlier claim boundary: the reproduced trajectory is the
legacy `admittance_proxy` / `normal_only` / `pinv_bounded` / q7-nullspace-bias
line, not the formula-faithful `paper_literal` / KKT line. Therefore this
does not make the formula-faithful paper-platform candidate pass full
paper-equivalent numerical parity.

## Next Step

Keep the formula-convergence and tuned-landmark claims separate. The next
productive branch should either formalize the split evidence as the accepted
paper-platform reporting structure, or move back to the UR10e adapted line by
validating/replacing the approximate TCP/contact model.
