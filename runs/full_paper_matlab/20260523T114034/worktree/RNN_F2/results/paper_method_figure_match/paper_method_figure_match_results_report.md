# TASE Run Report: paper_method_figure_match

## Quick Verdict
- Current verdict: Close on the core paper landmarks.
- Best-matching part: orientation convergence is the cleanest match right now with final error norm 0.000003.
- Biggest blocker: Only secondary plot-shape differences remain.
- Next step: Diagnose the remaining spike and start-up velocity shape.

## Run Snapshot
- Run type: `paper_method_figure_match`
- Orientation mode: `normal_only`
- Solver mode: `pinv_bounded`
- Result file: `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_figure_match/paper_method_figure_match_results.mat`
- Branch / commit: `feat/full-paper-reproduction` / `cd36b5a`
- Dirty state: `clean`
- Duration / steps: `29.999 s / 30000`
- Key end metrics: `E_end=0.114101`, `q7@22s=2.5000`, `final |e_f|=0.0006 N`, `|e_p(final)|=0.001006`, `|e_o(final)|=0.000003`

## Current vs Paper
- Fig. 6(c) force error: Match: force channel exists, final |e_f|=0.0006 N, tail mean |e_f|=0.0006 N, final measured force=4.9994 N.
- q7 @ 22 s: Match: paper expects the seventh joint near ±2.5 rad at 22 s, current q7(22 s)=2.5000 rad.
- Joint velocity pattern: Partial: paper shows start-up velocity saturation, current max |dq|=[0.170, 1.500, 0.067, 1.498, 0.186, 1.500, 0.169] rad/s.
- Position error: Match: final position error=[0.000294, 0.000962, 0.000000] m, max=[0.1069, 0.0011, 0.0252] m.
- Orientation error: Match: final orientation error=[-0.000001, 0.000003, 0.000000], max=[0.0531, 0.1259, 0.0000].
- Scene assumptions: Match: q0_match=True, orientation_mode=normal_only, solver_mode=pinv_bounded, first limit event=t=0.197s joints=4.

## Blocking Gaps
- Residual inner-loop spike remains: E_max=2.6726, so the plot shape still differs materially.

## Next Single Action
- Diagnose the remaining spike and start-up velocity shape. This is the highest-leverage move because it addresses the largest paper-side mismatch first.
