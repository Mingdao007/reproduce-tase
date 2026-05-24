# Experiment Matrix Plan

## Scope

Define staged simulation experiments before any hardware motion is considered.

## Assumptions

- Existing article-level E1-E4 runs are synthetic simulation references.
- Paper trajectory mapping must be PDF-verified before being treated as truth.
- UR10e adapted experiments start conservative and increase force gradually.

## Exact Files Touched

- `configs/full_article_experiments.yaml`
- `runs/*`
- `reports/*`

## Commands To Run

```bash
python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml
python3 scripts/run_ur10e_mujoco_adaptation.py --config configs/mujoco_ur10e.yaml --smoke
python3 scripts/run_full_article_experiment_sim.py --config configs/full_article_experiments.yaml
```

## Expected Outputs

- Fig.5 scalar finite-time convergence.
- UR10e smoke.
- Static force ladder: `0.5`, `1`, `2`, `5` N.
- No-contact trajectories.
- Contact trajectories.
- Article-level E1-E4 simulation matrix.
- Orientation-hold E1-E4 matrix with angular residual and slack metrics.
- Force-normal orientation smoke and tilted/curved-surface checks with
  contact-normal velocity mapping.

## Pass/Fail Criteria

Pass:

- Each run records config, command, git commit, dirty state, raw/metric
  artifact locations, plots, and failure notes.

Fail:

- A final comparison omits force error or constraint status.

## Rollback Point Or Recovery Command

Runs are append-only. Failed runs remain documented and later commits supersede
them rather than deleting them.

## Unresolved Risks

- Orientation-hold is not yet paper-faithful orientation compliance.
- Full-speed E2/E3 do not pass the combined force-motion and provisional
  orientation gates under the current linear-primary controller.
- Tilted-plane force-normal smokes expose the qdot/gain tradeoff but do not
  yet pass the orientation gates without saturation.
- Tilted-plane scalar gain/time-scale tuning fails the max-orientation-error
  gate from a flat initial orientation before trajectory timing can help.
- Staged prealignment lets the following E1 trajectory pass the gates, but the
  approach phase itself fails due to sustained qdot saturation and planar
  drift.
- Stage A scalar/slack bracketing did not produce an ordinary approach
  feasibility pass. The best trajectory-enabling cases still rely on sustained
  qdot saturation, and the planar-preserving linear-primary case does not
  reach the tilted-normal orientation threshold.
- Longer low-gain Stage A probes do not fix the approach either. They reduce
  angular slack but still exceed the qdot saturation and planar-drift budgets,
  and none make the following trajectory pass.
- Angular-command caps are respected and reduce weighted saturation, but still
  do not produce a Stage A pass. The remaining issue appears to be task
  structure, not just requested angular-rate magnitude.
- Separate approach and trajectory qdot caps are supported, but relaxed Stage
  A qdot alone still does not produce a terminal approach-budget or full
  staged-feasibility pass.
- The first staged E1-E4 after-prealignment matrix passes Stage B for E1, E3,
  and E4, but E2 remains qdot-budget limited after prealignment. The matrix is
  therefore partial evidence, not a complete staged tilted-plane reproduction.
- The E2 post-prealignment timing/gain bracket did not find a pass. Even
  `paper_time_scale = 0.025` with zero trajectory orientation gain remains
  qdot-saturated for `90.6%` of the trajectory.
- Shorter weighted Stage A durations near the first orientation-threshold
  crossing also do not fix E2. Short approaches fail E2 orientation gates;
  longer approaches recover orientation but keep E2 qdot saturation near
  `0.99`.
- Moderate trajectory-phase posture regularization fixes the isolated E2
  Stage B qdot blocker after weighted prealignment, but it does not fix Stage
  A. In v32, four trajectory-after-approach rows passed, while all ten rows
  still failed ordinary approach feasibility.
- Carrying the moderate trajectory posture objective into the slowed E1-E4
  matrix makes all four Stage B trajectories pass after weighted
  prealignment. The remaining full-staged failure is Stage A ordinary
  feasibility.
- Planar-primary Stage A priority controls x/y drift but does not solve the
  approach. Default normal secondary weighting loses contact/force; high
  normal weighting restores force but stalls orientation near `0.07 rad`.
- The two-phase recenter probe does not solve Stage A either. The explicit
  setup terminal-state gate passes `0 / 10` E2 rows: short recenter windows
  keep the following trajectory passing but fail setup force and x/y gates,
  while long recentering fixes x/y and force at the cost of terminal
  orientation.
- The three-phase settle probe also passes `0 / 10` setup terminal-state rows.
  Weighted settling improves the following E2 trajectory pass count to
  `8 / 10`, but only by allowing final x/y error around `7.2-8.3 mm`.

## Next Executable Step

Use `runs/staged_orientation_three_phase_settle/20260524T110039` as evidence
that scalar planned-phase scheduling is not sufficient. The next executable
step should either define an accepted relaxed setup budget and keep it
separate from full staged paper-equivalent feasibility, or change the Stage A
mathematical formulation rather than adding another duration bracket.
