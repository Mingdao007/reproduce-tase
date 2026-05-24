# Controller Implementation Plan

## Scope

Implement the finite-time force-motion controller after math and simulation
contracts are testable.

## Assumptions

- The first implementation targets simulation only.
- Real-time UR10e execution is out of scope until the hardware gate passes.
- `qpsolvers` with `osqp` is the preferred first QP backend.

## Exact Files Touched

- `src/tase_repro/controller.py`
- `src/tase_repro/constraints.py`
- `src/tase_repro/orientation.py`
- `src/tase_repro/force_feedback.py`
- `src/tase_repro/staged_force_motion.py`
- `src/tase_repro/kinematics.py`
- `src/tase_repro/panda_kinematics.py`
- `src/tase_repro/paper_7dof.py`
- `scripts/run_controller_smoke.py`
- `scripts/run_paper_7dof_section_v.py`
- `scripts/run_paper_7dof_q7_variant_probe.py`
- `scripts/compare_paper_7dof_fig6_raw_provenance.py`
- `scripts/audit_legacy_figure_match_source.py`
- `scripts/run_paper_trajectory_force_motion.py`
- `scripts/run_timing_feasibility_sweep.py`
- `tests/test_controller.py`
- `tests/test_force_motion.py`
- `tests/test_kinematics.py`
- `tests/test_panda_kinematics.py`
- `tests/test_paper_7dof.py`
- Future: `src/tase_repro/contact.py`
- Future: `src/tase_repro/metrics.py`
- Future: `tests/*`

## Commands To Run

```bash
scripts/run_tests.sh
python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml
python3 scripts/run_ur10e_mujoco_adaptation.py --config configs/mujoco_ur10e.yaml --smoke
scripts/run_paper_7dof_section_v.py --duration-s 5.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc
scripts/run_paper_7dof_section_v.py --duration-s 5.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0
scripts/run_paper_7dof_section_v.py --duration-s 5.0 --dt-s 0.002 --solver-mode pinv_bounded --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0
scripts/run_paper_7dof_q7_variant_probe.py --duration-s 30.0 --dt-s 0.002 --communication-delay-s 0.032 --force-integral-leak 0.0
scripts/compare_paper_7dof_fig6_raw_provenance.py
scripts/audit_legacy_figure_match_source.py
```

## Expected Outputs

- Unit tests for finite-time dynamics, kinematics, contact sign, and QP
  constraints.
- Controller logs with slack, saturation, solver status, and task residuals.
- Optional orientation-hold runs log orientation error, angular residual, and
  angular slack.
- Linear-primary orientation runs preserve the first-stage TCP linear velocity
  before optimizing angular velocity.
- Force-normal orientation runs align TCP local z to the simulated 3D contact
  normal and record the same angular metrics.
- Tilted-surface force-normal runs can map scalar force correction along the
  measured contact normal instead of only along world z.
- Optional joint-velocity posture targets are solved inside the hard
  velocity/joint bounds and recorded in staged run metrics.
- Planar-primary orientation priority preserves x/y TCP velocity rows before
  optimizing contact-normal and angular rows as secondary tasks.
- Separate paper-platform 7DOF diagnostics record execution success separately
  from contact-force tail success.

## Pass/Fail Criteria

Pass:

- No controller output is clipped outside the QP without reporting.
- Infeasible QP states return a stop or fail status, not a silent command.

Fail:

- A trajectory plot is accepted without solver/status metrics.
- Orientation plots are accepted without angular slack and qdot-utilization
  metrics.

## Rollback Point Or Recovery Command

Implement controller code behind tests. Revert the controller commit if tests or
smoke runs regress.

## Unresolved Risks

- Paper finite-time law details remain pending PDF verification.
- Full-speed E2/E3 orientation-gated runs remain qdot-budget limited under the
  current `0.15 rad/s` cap.
- Tilted-plane force-normal smokes expose a qdot/gain tradeoff but do not yet
  pass orientation gates without saturation.
- Tilted-plane gain/time-scale tuning cannot pass the existing max-orientation
  gate from a flat initial TCP orientation, because the initial error is about
  `0.174 rad`.
- A staged weighted approach can make the following E1 trajectory pass, but
  the approach phase currently uses sustained qdot saturation and about
  `9.7 mm` planar drift.
- A seven-case Stage A bracket did not find a scalar gain or slack-weight
  setting that makes the tilted approach phase pass the ordinary feasibility
  gate. Trajectory-enabling weighted cases still saturate qdot for most of the
  approach, while the linear-primary approach stalls above the orientation
  threshold.
- Longer low-gain Stage A probes also fail. Three weighted cases reach the
  terminal orientation threshold, but none pass the terminal approach budget
  or make the following trajectory pass; qdot saturation remains above
  `0.526` in the low-gain weighted cases.
- The v27 angular-command cap is respected and reduces weighted qdot
  saturation, but it does not make Stage A feasible. Weighted capped cases
  still fail qdot and planar-drift budgets, while capped linear-primary stalls
  above the orientation threshold.
- Separate Stage A and Stage B qdot caps are now supported, but relaxing Stage
  A qdot alone still does not produce a pass. Weighted approaches align with
  about `8 mm` drift, while `linear-primary` approaches preserve position but
  stall above the orientation threshold.
- The v29 staged E1-E4 matrix shows that weighted prealignment is not enough
  for a full trajectory family claim. E1, E3, and E4 pass the slowed Stage B
  gate, but E2 remains qdot-saturated after prealignment.
- The v30 E2 bracket shows that this E2 saturation survives lower timing and
  zero trajectory orientation gain. The blocker is likely posture-conditioned
  tangent velocity authority, not the angular task alone.
- The v31 short-approach bracket shows that stopping Stage A near the first
  orientation threshold only trades E2 qdot failure for E2 orientation failure;
  duration alone is not an adequate terminal-configuration control.
- The v32 posture regularization hook solves the isolated E2 Stage B qdot
  blocker for moderate trajectory posture weights, but all tested cases still
  fail ordinary Stage A feasibility. Strong approach posture weighting can
  also break contact/force tracking.
- The v33 matrix carries the moderate trajectory posture objective into E1-E4
  and all four Stage B trajectories pass after prealignment. The remaining
  controller problem is now the Stage A approach formulation.
- The v34 planar-primary Stage A mode controls drift but either loses
  contact/force or stalls orientation when normal weighting is increased.
  It is diagnostic, not an accepted approach solution.
- The v35 two-phase recenter probe adds an explicit original x/y setup
  reference and a setup terminal-state gate. No E2 row passes the setup gate.
  Short recenter windows keep Stage B passing but fail force and x/y terminal
  gates; long recentering meets x/y and force but loses terminal orientation.
- The v36 three-phase settle probe also passes `0 / 10` setup terminal-state
  rows. Weighted settling restores force/orientation and Stage B compatibility
  by drifting back toward `8 mm`; linear-primary settling preserves x/y but
  keeps terminal orientation too high.
- The v37 terminal IK audit removes path and velocity-controller constraints
  and still finds `0 / 65` accepted terminal setup states. The best candidate
  keeps contact and force but fails both the `2 mm` x/y gate and `0.03 rad`
  force-normal orientation gate.
- The v38 relaxed setup budget creates a separate simulation-only acceptance
  label. It gives the v33 slowed E1-E4 matrix `4 / 4` UR10e adapted
  trajectory-after-relaxed-setup passes while preserving `0 / 4` strict full
  staged feasibility.
- The v41 paper-platform 7DOF diagnostic executes with hard bounds respected,
  but its paper-literal force loop loses tail contact. It is a separate
  executable line, not paper-faithful numerical parity.
- The v42 contact-stabilized paper-platform diagnostic passes tail contact and
  force error with hard bounds respected, but it uses `pinv_bounded` plus a
  capped force integral, not the paper-faithful KKT-projection path.
- The v43 capped-integral KKT paper-platform diagnostic also passes tail
  contact and force error with hard bounds respected. It is closer to the
  paper inner-loop form than v42, but the force-integral cap is still an
  explicit diagnostic anti-windup assumption.
- The v44 parity gate compares the v43 Python 7DOF candidate against the
  legacy MATLAB/RNN formula-faithful and figure-match verification reports.
  Tail convergence agrees with the formula-faithful reference within the gate
  tolerances, but strict parity fails on duration, Fig.6 q7-at-22 s, missing
  Python Fig.5 r-sweep coverage, and the capped force integral.
- The v45 30 s Python 7DOF candidate records q7 at 22 s and covers the full
  legacy Fig.6 duration. Tail convergence still agrees with the
  formula-faithful reference, but q7 at 22 s is `1.6755097668200787 rad`
  rather than the figure-match `2.5 rad`.
- The v46 Python 7DOF Fig.5 sweep records all required r values over 0-2 s
  windows. The strict parity gate now passes Fig.5 r-sweep coverage.
- The v47 uncapped KKT candidate passes force/contact, hard bounds, and the
  strict gate's paper-assumption compatibility check. q7 at 22 s remains
  mismatched at `1.6680622878116045 rad`.
- The v48 q7 variant probe shows the mismatch persists across the current
  supported Python solver, orientation, and force-integral-cap variants. The
  eight-row q7 range is `0.02232563934802667 rad`, and the closest variant is
  still `0.8164105207854273 rad` away from the figure-match q7 reference.
- The v49 raw Fig.6 provenance audit shows the Python Panda FK/Jacobian port
  matches sampled legacy raw states. The figure-match q7 landmark is tied to a
  legacy `admittance_proxy` force-loop and landmark-acceptance line with q7
  upper-limit pinning, not to the formula-faithful `paper_literal` line.
- The v50 source audit shows the legacy `figure_match` path has eight
  non-paper-faithful tuning knobs, including explicit q7 nullspace bias. This
  makes the current q7 landmark a tuned figure-match signal, not a
  formula-faithful controller requirement.
- The v51 split gate lets the Python paper-platform line claim formula
  convergence separately from tuned figure-match landmark reproduction. The
  legacy strict aggregate remains failed.
- The v52 tuned Python candidate reproduces the legacy figure-match q7
  trajectory with explicit non-paper-faithful labels. This closes the tuned
  landmark implementation gap without changing the formula-faithful claim.
- The v53 TCP/contact audit shows the UR10e adapted terminal setup failure is
  still tied to an approximate model convention: the current 85 mm site is the
  colliding sphere center, not the simulated contact surface.
- The v54 contact-point model separates the 85 mm site from the colliding
  sphere center, but the strict terminal setup rerun still fails `0 / 65`.
- The v55 broad terminal audit enforces the intended `contact_plane` /
  `contact_tip` target force pair and still finds `0 / 513` strict terminal
  passes.
- The v56 contact-manifold audit shows the strict setup blocker is a
  gate-definition conflict: x/y+force, x/y+orientation, and force+orientation
  cannot all satisfy the current thresholds together in the audited local
  contact neighborhoods.
- The v57 adapted terminal setup gate is diagnostic-only and passes `1 / 513`
  terminal candidates. It must not be used as a path, trajectory,
  paper-equivalent, or hardware-readiness claim.
- The v58 target-selection decision chooses
  `ur10e_adapted_terminal_setup_diagnostic` for the next Stage A simulation
  prototype. This removes the label ambiguity before another controller
  experiment, but it is still not a controller or feasibility claim.
- The v59 handoff audit starts directly from the selected target and evaluates
  E1-E4 with target-pair force/contact accounting. It reports `0 / 4` passes:
  target contact, force, x/y, and diagnostic orientation remain acceptable,
  but every row fails qdot saturation gates.
- The v60 qdot-aware diagnostic handoff starts from the same selected target,
  slows the trajectory timing, lowers force gain, and holds the diagnostic
  orientation envelope. It reports `4 / 4` passes without qdot saturation, but
  it is direct-target handoff evidence only.
- The v62 Stage A contact path tracker follows the v61 path over `15.0 s` with
  zero qdot saturation and a passing terminal diagnostic gate, but it is not
  connected to Stage B handoff.
- The v63 stitched diagnostic run connects the v62 Stage A tracker to the v60
  slowed handoff and reports `4 / 4` Stage B passes in one script. It is still
  diagnostic-label simulation evidence only.
- The v64 sensitivity audit passes only `4 / 9` stitched cases. It preserves
  the nominal pass under slower Stage A timing and two force-gain changes, but
  fails 1 mm base-z/contact perturbations, shorter Stage A timing, lower qdot
  limit, and faster Stage B timing.
- The v65 timing-margin audit recovers the qdot/timing side: Stage A passes at
  `14.5 s`, the `0.12 rad/s` qdot limit passes at `18.0 s`, and Stage B passes
  at `paper_time_scale = 0.012` but not `0.0125`. It does not recover 1 mm
  base-z/contact perturbations.
- The v66 base-z recovery audit recovers `base_z_minus_1mm` only when Stage A
  is extended to `16.0 s` and the start/terminal endpoints are reoptimized.
  The exact `15.0 s` boundary and `base_z_plus_1mm` remain unresolved.
- The v67 base-z bracket audit shows the positive side fails before path
  reoptimization can run: no tested positive delta from `+0.05 mm` through
  `+1.0 mm` has a passing start plus terminal pair.
- The v68 positive start-contact audit shows broader deterministic seeds can
  recover the positive-side start contact through `+1.0 mm`; the terminal
  orientation gate still fails all positive deltas.
- The v69 positive terminal orientation audit shows force/x-y/contact passes
  `8 / 8` positive terminal cases in the current contact-point model, but the
  `0.08 rad` orientation gate passes `0 / 8`. Full-rotation and
  force-normal-only errors match to numerical precision, so yaw is not the
  limiting convention.
- The v70 positive relaxed-orientation recovery audit uses a run-local
  `0.12 rad` terminal orientation envelope and recovers positive start,
  terminal, and path feasibility through `+1.0 mm`, but stitched recovery is
  still `0` because Stage B handoff is `3 / 4` with E2 qdot saturation.
- The v71 positive Stage B E2 margin audit shows E2 passes all positive deltas
  at `paper_time_scale = 0.005` under the v70 run-local relaxed terminal/path
  setup. Qdot-limit-only relaxation at original `0.01` timing does not recover
  the hardest `+1.0 mm` row because orientation remains just above `0.12 rad`.
- The v72 positive full stitched recovery audit uses the v70 relaxed
  terminal/path setup plus `paper_time_scale = 0.005` and recovers all positive
  E1-E4 stitched rows `8 / 8` through `+1.0 mm`.
- The v73 positive stitched sensitivity audit passes `37 / 40` compact matrix
  cells. Nominal v72 and `stage_a_14p5s` pass all positive deltas, while
  `qdot012_stage_a18s` fails `+0.2 mm` on Stage A final tracking,
  `paper_time_scale_0p0075` fails `+1.0 mm` on E2 qdot/orientation, and
  `orientation_gate_0p119` fails `+1.0 mm` on orientation gates.

## Next Executable Step

Use the relaxed label only for UR10e adapted simulation reports. Do not
continue scalar phase-duration tuning under the current instantaneous velocity
task formulation. The next UR10e adapted controller experiment should isolate
the v73 `qdot012_stage_a18s` `+0.2 mm` Stage A final-tracking boundary with a
small duration/path-retiming margin audit. Keep contact, drift, terminal
orientation, force error, and qdot saturation visible together.
