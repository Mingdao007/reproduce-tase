# Paper Method Verification: paper_method_formula_faithful

## Verdict

- Acceptance mode: `diagnostic`.
- Overall pass: `true`.
- Result file: `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_formula_faithful/paper_method_formula_faithful_results.mat`.

## Fig. 6 Landmarks

- q7 sample time: `22.000 s`.
- q7 at 22 s: `1.124179 rad`.
- q7 absolute error to `2.5 rad` limit: `1.375821 rad`; pass: `false`.
- Startup max `|dq|`: `[0.5112 0.6353 0.3161 0.2313 0.1518 0.4503 0.7249] rad/s`.
- Startup reaches velocity limit: `false`.

## Convergence Metrics

- Tail mean `|e_f|`: `0.0476436 N`; pass: `true`.
- Tail mean `||e_p||`: `0.000583872 m`; pass: `true`.
- Tail mean `||e_o||`: `7.42197e-05`; pass: `true`.

## Constraint Checks

- Max joint-limit violation: `0 rad`.
- Max velocity-limit violation: `0 rad/s`.
- Constraints pass: `true`.

## Method Coverage

- Required method coverage pass: `true`.
- `M1_task_geometry`: true
- `M2_force_motion_split`: true
- `M2_paper_literal_eq17`: true
- `M3_orientation_compliance`: true
- `M4_dynamic_programming_bounds`: true
- `M5_finite_time_inner_loop`: true
- `M6_simulation_constraints`: true
