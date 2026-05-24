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

## Next Executable Step

Use `runs/tilted_orientation_gain_timing_sweep/20260524T091826` as negative
evidence that scalar gain/time-scale tuning is insufficient. The next
executable experiment is a staged tilted-plane orientation approach followed by
paper-trajectory tracking under the same orientation and qdot gates.
