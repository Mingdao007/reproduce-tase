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

## Next Executable Step

Use `runs/staged_orientation_e2_short_approach_bracket/20260524T101113` as
evidence that Stage A duration alone is not enough. The next executable
experiment should add a posture/nullspace objective or otherwise change the
terminal configuration before rerunning E2.
