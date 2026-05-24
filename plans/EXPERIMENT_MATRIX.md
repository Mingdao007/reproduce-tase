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
scripts/run_paper_7dof_section_v.py --duration-s 5.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc
scripts/run_paper_7dof_section_v.py --duration-s 5.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0
scripts/run_paper_7dof_section_v.py --duration-s 5.0 --dt-s 0.002 --solver-mode pinv_bounded --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0
scripts/run_paper_7dof_q7_variant_probe.py --duration-s 30.0 --dt-s 0.002 --communication-delay-s 0.032 --force-integral-leak 0.0
scripts/compare_paper_7dof_fig6_raw_provenance.py
scripts/audit_legacy_figure_match_source.py
scripts/evaluate_paper_platform_parity.py
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
- Separate paper-platform 7DOF Section V diagnostics with execution, contact,
  force-error, bound, and residual metrics.
- Paper-platform parity gate outputs comparing the Python 7DOF candidate to
  the migrated legacy MATLAB/RNN verification reports.
- Paper-platform q7 variant probe outputs showing whether the Fig.6 q7
  landmark changes across supported solver, orientation, and force-integral
  variants.
- Paper-platform raw Fig.6 provenance outputs comparing Python raw arrays to
  ignored local legacy MATLAB/RNN `.mat` arrays without committing raw data.
- Legacy figure-match source audit outputs that classify tuned landmark knobs
  separately from formula-faithful paper-platform parity.
- Split paper-platform gate outputs that report formula-convergence evidence
  separately from tuned figure-match landmark evidence.

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
- The setup terminal IK audit removes path feasibility and searches directly
  for terminal setup configurations. It produces `0 / 65` terminal setup
  passes; the best candidate is close on force but fails the x/y and
  orientation gates.
- The relaxed setup budget evaluation applies a separate UR10e adapted label
  to the v33 slowed tilted-plane E1-E4 matrix: `4 / 4` relaxed setup passes,
  `4 / 4` trajectory feasibility passes, and `0 / 4` strict full staged
  feasibility passes.
- The v41 paper-platform 7DOF diagnostic provides a separate executable line,
  but force/contact behavior does not pass: tail contact fraction is `0.0`
  and tail mean force error is `5.0 N`.
- The v42 contact-stabilized 7DOF diagnostic passes the tail contact-force
  gate, but it is not paper-faithful KKT parity because it uses
  `pinv_bounded` and a capped force integral.
- The v43 capped-integral KKT 7DOF diagnostic passes the tail contact-force
  gate using `kkt_projection`, but the integral cap remains an adapted
  anti-windup assumption.
- The v44 paper-platform parity gate is now defined. The v43 candidate passes
  legacy formula-faithful tail convergence tolerances, but strict parity fails
  on 30 s duration coverage, Fig.6 q7-at-22 s, missing Python Fig.5 r-sweep
  coverage, and the capped-integral assumption.
- The v45 30 s Python 7DOF candidate passes duration coverage and
  formula-faithful tail convergence tolerances, but strict parity still fails
  on the Fig.6 q7-at-22 s landmark, missing Python Fig.5 r-sweep coverage,
  and the capped-integral assumption.
- The v46 Python 7DOF Fig.5 sweep provides one 0-2 s metrics file per paper r
  value and makes the strict parity gate pass Fig.5 coverage. Strict parity
  still fails on the q7-at-22 s landmark and the capped-integral assumption.
- The v47 uncapped 30 s KKT candidate passes the strict gate's
  paper-assumption compatibility check. Strict parity now fails only on the
  q7-at-22 s landmark.
- The v48 q7 variant probe shows the q7 landmark mismatch is not explained by
  the current supported Python solver, orientation, or force-integral-cap
  variants. Across eight 30 s rows, q7 remains in
  `1.661263839866546-1.6835894792145727 rad` and `0 / 8` rows meet the
  `2.5 rad` figure-match tolerance.
- The v49 raw Fig.6 provenance audit shows Python Panda FK/Jacobian
  conditioning matches sampled legacy raw states to numerical precision. The
  `2.5 rad` q7 landmark comes from the legacy `admittance_proxy`
  figure-match line with `landmark` acceptance and q7 upper-limit pinning, not
  from the formula-faithful `paper_literal` line.
- The v50 source audit shows the legacy `figure_match` path has eight
  non-paper-faithful tuning knobs and an explicit q7 nullspace bias. The
  q7@22 s figure-match landmark should therefore be treated as tuned landmark
  evidence unless a separate Python figure-match candidate is intentionally
  implemented and labeled.
- The v51 split gate reports `paper_platform_formula_convergence_pass = true`
  while keeping `paper_platform_figure_match_landmark_pass = false` and the
  backward-compatible strict aggregate `paper_platform_parity_pass = false`.
- The v52 tuned Python candidate reproduces the legacy figure-match q7
  trajectory with q7@22 s delta `2.6201263381153694e-12 rad` and joint RMSE
  `6.081574510252252e-09 rad`; this is tuned landmark evidence only.
- The v53 TCP/contact audit shows the current UR10e tilted-plane model places
  the 85 mm TCP site at the center of the contact sphere. The simulated
  contact surface is one `0.045 m` sphere radius away, and the terminal setup
  rerun remains `0 / 65`.
- The v54 contact-point model separates the 85 mm site from the colliding
  sphere center, but the strict terminal setup rerun remains `0 / 65`.
- The v55 broad terminal audit enforces the intended `contact_plane` /
  `contact_tip` target force pair and still finds `0 / 513` strict terminal
  passes.
- The v56 contact-manifold audit shows the remaining strict setup blocker is a
  gate-definition conflict rather than a broad-seed contact discovery issue.
- The v57 adapted terminal setup gate passes `1 / 513` terminal candidates as
  a diagnostic-only label, with no path or trajectory claim.
- The v58 target-selection decision chooses the v57 diagnostic terminal setup
  as the next Stage A simulation prototype target. This is not a controller or
  trajectory-feasibility claim.
- The v59 diagnostic-target handoff starts from that target and evaluates
  E1-E4. It keeps target contact and small force/x-y/diagnostic-orientation
  errors, but every row fails qdot saturation gates, so the handoff pass count
  is `0 / 4`.
- The v60 qdot-aware diagnostic handoff slows timing, lowers force gain, and
  holds the diagnostic orientation envelope. It reports `4 / 4` direct-target
  handoff passes, but it still does not implement a Stage A path.
- The v61 contact path audit finds an offline 128-knot quasi-static path from
  ordinary initial q to the selected diagnostic target with a qdot-limited
  minimum duration of `14.332635022800167 s`, but it is not an online
  controller.
- The v62 contact path tracker follows that path over `15.0 s` with max qdot
  `0.14332635022814824 rad/s`, zero qdot saturation, target contact throughout,
  and a passing terminal diagnostic gate, but it is not connected to Stage B.
- The v63 stitched run executes the v62 Stage A tracker and v60 slowed handoff
  in one script and reports a passing stitched gate with Stage B `4 / 4`.
- The v64 stitched sensitivity audit passes `4 / 9` cases. It fails 1 mm
  base-z/contact perturbations, `stage_a_14s`, `qdot_limit_0p12`, and
  `paper_time_scale_0p02`, so the v63 result remains nominal diagnostic
  evidence only.
- The v65 timing-margin audit recovers nearby timing/qdot failures:
  `stage_a_14p5_recovery`, `qdot012_stage_a_18p0_recovery`, and
  `paper_time_scale_0p012_recovery` pass. The 1 mm base-z/contact perturbation
  failures remain unaddressed.
- The v66 base-z recovery audit recovers only
  `base_z_minus_1mm_stage_a_16s_recovery`. The exact `15.0 s`
  `base_z_minus_1mm` reference remains qdot-limited, and `base_z_plus_1mm`
  still lacks a passing start plus terminal target pair under the diagnostic
  search.
- The v67 base-z bracket audit shows no tested positive delta from `+0.05 mm`
  through `+1.0 mm` has both start and terminal feasibility. Nominal,
  `-0.25 mm`, and `-0.5 mm` recover at `15.0 s`; `-1.0 mm` recovers only at
  `16.0 s`; `-0.75 mm` exposes a path-optimization anomaly.
- The v68 positive base-z start-contact audit shows the positive-side start
  contact itself is recoverable through `+1.0 mm` with broader deterministic
  seed sweeps. Terminal orientation still fails all positive deltas.
- The v69 positive terminal orientation audit shows the current contact-point
  model passes force/x-y/contact for all positive terminal cases but passes the
  `0.08 rad` diagnostic orientation gate for `0 / 8`. Full-rotation and
  force-normal-only errors are numerically identical, so yaw handling is not
  the limiter.
- The v70 positive relaxed-orientation recovery audit uses a run-local
  `0.12 rad` diagnostic orientation envelope. It recovers positive start,
  terminal, and path feasibility `8 / 8` through `+1.0 mm`, but stitched
  recovery remains `0` because Stage B handoff is `3 / 4`, consistently
  failing E2 on qdot saturation.
- The v71 positive Stage B E2 margin audit reuses the v70 relaxed
  terminal/path setup. E2 passes `0 / 8` positive deltas at
  `paper_time_scale = 0.01`, `7 / 8` at `0.0075`, and `8 / 8` at `0.005`.
  Raising qdot limit alone on the hardest `+1.0 mm` case at original timing
  still fails because orientation remains just above `0.12 rad`.
- The v72 positive full stitched recovery audit combines the v70 relaxed
  terminal/path setup with `paper_time_scale = 0.005`. It recovers the full
  positive E1-E4 stitched diagnostic matrix `8 / 8` through `+1.0 mm`.
- The v73 positive stitched sensitivity audit stress-tests the v72 recovered
  policy across five scenarios and eight positive deltas. It passes `37 / 40`
  stitched cells: nominal v72 and `stage_a_14p5s` pass all positive deltas,
  while `qdot012_stage_a18s` fails `+0.2 mm` on Stage A final tracking,
  `paper_time_scale_0p0075` fails `+1.0 mm` on E2 qdot/orientation, and
  `orientation_gate_0p119` fails `+1.0 mm` on orientation gates.
- The v74 qdot012 Stage A margin audit isolates the `qdot012_stage_a18s`
  `+0.2 mm` failure. Stage B passes `4 / 4` for every tested duration; Stage A
  final tracking fails through `18.03 s` and recovers at `18.035 s`.
- The v75 qdot012 positive stitched matrix folds the `18.035 s` Stage A margin
  into all eight positive deltas. Stitched recovery passes `8 / 8` through
  `+1.0 mm` with Stage B `4 / 4` for every row.
- The v76 positive timing-boundary audit isolates the
  `paper_time_scale_0p0075` `+1.0 mm` failure. Stage A passes all timing
  cases; the hardest positive E2 row passes through `paper_time_scale =
  0.0052` and first fails at `0.0054` on orientation just above the `0.12 rad`
  diagnostic gate.
- The v77 positive orientation-gate boundary audit isolates the
  `orientation_gate_0p119` `+1.0 mm` failure. Stage A terminal orientation
  passes once the gate reaches `0.1195 rad`; full stitched recovery first
  passes at `0.11998 rad` because E2 reaches `0.1199788204275829 rad`.
- The v78 Stage B orientation-kp probe tests the existing orientation-feedback
  hook on the localized E2 `+1.0 mm` row at a `0.11995 rad` gate. Stage A
  passes all `30 / 30` cells, but stitched recovery passes `0 / 30`: low gains
  miss orientation, while orientation-correcting gains fail qdot saturation
  and/or tail qdot utilization.
- The v79 Stage B priority recovery audit recovers the localized `+1.0 mm`,
  `0.11995 rad` tightened-gate E1-E4 row with planar-primary priority and
  normal-axis weight `30`. Passing scenarios are `orientation_kp = 0.001` and
  `0.002`, both with Stage B handoff `4 / 4`.
- The v80 positive planar-priority matrix carries both v79 passing candidates
  across all eight positive deltas through `+1.0 mm`. Both scenarios pass
  `8 / 8`, for `16 / 16` stitched cells under the `0.11995 rad` gate.
- The v81 planar-priority stress audit tests those candidates against faster
  timing and the tighter gate. Both pass the focused `+1.0 mm` timing sweep
  through `paper_time_scale = 0.0065` and first fail at `0.007`; both fail the
  full positive-delta `paper_time_scale = 0.0075` stress `0 / 8`; both pass
  the `0.119 rad` gate through `+0.75 mm` but still fail at `+1.0 mm`.
- The v82 weighted timing recovery audit shows weighted zero-angular-command
  priority recovers the faster-timing face under the `0.11995 rad` gate. Both
  tested weighted scenarios pass the full positive-delta
  `paper_time_scale = 0.0075` matrix `8 / 8`, and `weighted_kp0_normal1`
  passes the focused `+1.0 mm` timing sweep through `paper_time_scale = 0.01`.
- The v83 weighted gate/time matrix audit shows the full positive-delta
  `paper_time_scale = 0.01`, `0.11995 rad` matrix also passes `8 / 8` for both
  weighted scenarios, while the tighter `0.119 rad` gate passes through
  `+0.75 mm` but still fails at `+1.0 mm`.

## Next Executable Step

Use the v38 relaxed label in the completion audit for the UR10e adapted
simulation line, while keeping strict full staged feasibility marked as not
achieved. Future UR10e experiment branches should stress-test the v63 stitched
policy before treating it as more than a nominal diagnostic staged pass. v64
did the first stress test, v65 recovered the qdot/timing side, v66 recovered
only the `-1 mm` base-z case with a `16.0 s` Stage A duration, v67 bracketed
the positive side down to `+0.05 mm`, v68 separated positive-side start
contact from terminal orientation, v69 quantified the orientation margin, and
v70 recovered positive-side endpoints/path under an explicit `0.12 rad`
diagnostic envelope, and v71 found that E2 recovers for all positive deltas at
`paper_time_scale = 0.005`. v72 recovers the full positive E1-E4 stitched
matrix at that timing. v73 bounds sensitivity around that exact relaxed
diagnostic policy, and v74 recovers the qdot012 `+0.2 mm` Stage A tracking miss
with a `18.035 s` duration. v75 recovers the full qdot012 positive matrix at
that duration. v76 brackets the `+1.0 mm` faster-timing failure at
`paper_time_scale = 0.0052` pass versus `0.0054` first fail. v77 brackets the
tightened-orientation boundary at `0.11997` fail versus `0.11998` first
stitched pass. v78 rules out the current single-gain Stage B `orientation_kp`
hook as a clean recovery for that boundary. v79 locally recovers the hardest
tightened-gate row with planar-primary priority and normal-axis weight `30`.
v80 carries that recovery across the full positive-delta matrix. v81 improves
the focused timing/gate boundaries but does not recover the full
`paper_time_scale = 0.0075` stress or the `+1.0 mm`, `0.119 rad` row. v82
recovers the `0.0075` faster-timing face with weighted zero-angular-command
priority under the `0.11995 rad` gate. v83 proves the full positive
`paper_time_scale = 0.01`, `0.11995 rad` matrix for the tested weighted
scenarios, but does not recover the `0.119 rad` gate. Keep strict
paper-equivalent setup, v38 trajectory-after-relaxed-setup, and v63-v83
diagnostic staged labels separate.
