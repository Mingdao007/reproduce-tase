# TASE Run Report: paper_method_formula_faithful

## Quick Verdict
- Current verdict: Partially matching, but still not paper-faithful.
- Best-matching part: orientation convergence is the cleanest match right now with final error norm 0.000045.
- Biggest blocker: The paper's clearest timing landmark, q7 hitting the limit at 22 s, is still missing.
- Next step: Make the paper_ideal scene more comparable before chasing secondary plot shape details.

## Run Snapshot
- Run type: `paper_method_formula_faithful`
- Orientation mode: `force_shortest_arc`
- Solver mode: `kkt_projection`
- Result file: `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_formula_faithful/paper_method_formula_faithful_results.mat`
- Branch / commit: `feat/full-paper-reproduction` / `cd36b5a`
- Dirty state: `clean`
- Duration / steps: `29.999 s / 30000`
- Key end metrics: `E_end=0.001938`, `q7@22s=1.1242`, `final |e_f|=0.0134 N`, `|e_p(final)|=0.000486`, `|e_o(final)|=0.000045`

## Current vs Paper
- Fig. 6(c) force error: Match: force channel exists, final |e_f|=0.0134 N, tail mean |e_f|=0.0476 N, final measured force=4.9866 N.
- q7 @ 22 s: Mismatch: paper expects the seventh joint near ±2.5 rad at 22 s, current q7(22 s)=1.1242 rad.
- Joint velocity pattern: Mismatch: paper shows start-up velocity saturation, current max |dq|=[0.511, 0.635, 0.316, 0.231, 0.152, 0.450, 0.725] rad/s.
- Position error: Match: final position error=[-0.000410, 0.000261, -0.000000] m, max=[0.1069, 0.0223, 0.0405] m.
- Orientation error: Match: final orientation error=[-0.000011, 0.000027, -0.000034], max=[0.0049, 0.0058, 0.7854].
- Scene assumptions: Partial: q0_match=True, orientation_mode=force_shortest_arc, solver_mode=kkt_projection, first limit event=t=1.786s joints=4.

## Blocking Gaps
- q7 landmark still misses: q7(22 s)=1.1242 rad instead of about ±2.5 rad.
- Residual inner-loop spike remains: E_max=1.0883, so the plot shape still differs materially.

## Next Single Action
- Make the paper_ideal scene more comparable before chasing secondary plot shape details. This is the highest-leverage move because it addresses the largest paper-side mismatch first.
