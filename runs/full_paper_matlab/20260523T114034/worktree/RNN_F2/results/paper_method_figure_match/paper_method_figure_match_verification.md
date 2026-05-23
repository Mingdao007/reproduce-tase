# Paper Method Verification: paper_method_figure_match

## Verdict

- Acceptance mode: `landmark`.
- Overall pass: `true`.
- Result file: `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_figure_match/paper_method_figure_match_results.mat`.

## Fig. 6 Landmarks

- q7 sample time: `22.000 s`.
- q7 at 22 s: `2.500000 rad`.
- q7 absolute error to `2.5 rad` limit: `0.000000 rad`; pass: `true`.
- Startup max `|dq|`: `[0.1554 1.5 0.02558 1.498 0.03634 1.5 0.1689] rad/s`.
- Startup reaches velocity limit: `true`.

## Convergence Metrics

- Tail mean `|e_f|`: `0.000574393 N`; pass: `true`.
- Tail mean `||e_p||`: `0.000907723 m`; pass: `true`.
- Tail mean `||e_o||`: `2.69494e-06`; pass: `true`.

## Constraint Checks

- Max joint-limit violation: `0 rad`.
- Max velocity-limit violation: `0 rad/s`.
- Constraints pass: `true`.

## Method Coverage

- Required method coverage pass: `true`.
- `M1_task_geometry`: true
- `M2_force_motion_split`: true
- `M4_dynamic_programming_bounds`: true
- `M6_simulation_constraints`: true
