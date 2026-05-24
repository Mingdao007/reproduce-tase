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
scripts/run_paper_7dof_section_v.py --duration-s 5.0 --dt-s 0.002 --solver-mode pinv_bounded --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0
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

## Next Executable Step

Use the relaxed label only for UR10e adapted simulation reports. Do not
continue scalar phase-duration tuning under the current instantaneous velocity
task formulation. Any future controller experiment should either revisit the
model/TCP/contact geometry, introduce a genuinely different Stage A
formulation, or debug the separate paper-platform KKT-projection contact loss.
Keep contact, drift, terminal orientation, force error, and qdot saturation
visible together.
