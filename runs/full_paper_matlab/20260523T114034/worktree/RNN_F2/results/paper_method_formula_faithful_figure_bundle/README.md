# Paper Simulation Figure Bundle

## What is included
- `fig5/`: Fig. 5(a-f) panels and `figure5_simulation_bundle.png`
- `fig6/`: Fig. 6(a-f) panels and `figure6_simulation_bundle.png`
- `raw_runs/`: fresh `.mat` results used to generate the figures
- bundle zip: `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_formula_faithful_figure_bundle/paper_method_formula_faithful_figure_bundle.zip`

## Data source
- Source variant: `formula_faithful`
- Orientation mode: `force_shortest_arc`
- Solver mode: `kkt_projection`
- Force loop mode: `paper_literal`
- Fig. 5 runs use `r ∈ {0.2, 0.4, 0.6, 0.8, 1.0}` with `0–2 s` simulation windows
- Fig. 6 uses the selected source variant full 30 s simulation

## Generation command
```bash
matlab -batch "cd('/home/andy/Documents/UR5e_ws/RNN_F2'); run_paper_method_figure_bundle('formula_faithful')"
```

## Current paper-alignment notes
- This bundle is the formula-first line. It uses the paper-literal Eq.(16)-(17) normal velocity update and KKT-style inner loop.
- `Rd(F)` remains mathematically ambiguous in the paper; this line uses the force-axis shortest-arc repair and records that choice.
- `q7@22s = 1.1242 rad` in the regenerated Fig. 6 run.
- Tail mean `|e_f| = 0.0476 N`, tail mean `|e_p| = 0.000584 m`, tail mean `|e_o| = 0.000074 rad` in the regenerated Fig. 6 run.
- Fig. 5 panels are reconstructed from the six residual components `J*dq - xdot_c`, not only the scalar norm `E_save`.

## Raw run files
- `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_formula_faithful_figure_bundle/raw_runs/formula_faithful_fig5_r02_results.mat` for Fig. 5 with `r = 0.2`
- `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_formula_faithful_figure_bundle/raw_runs/formula_faithful_fig5_r04_results.mat` for Fig. 5 with `r = 0.4`
- `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_formula_faithful_figure_bundle/raw_runs/formula_faithful_fig5_r06_results.mat` for Fig. 5 with `r = 0.6`
- `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_formula_faithful_figure_bundle/raw_runs/formula_faithful_fig5_r08_results.mat` for Fig. 5 with `r = 0.8`
- `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_formula_faithful_figure_bundle/raw_runs/formula_faithful_fig5_r10_results.mat` for Fig. 5 with `r = 1.0`
- `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_formula_faithful_figure_bundle/raw_runs/formula_faithful_fig6_results.mat` for Fig. 6
