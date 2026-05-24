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
- `src/tase_repro/orientation.py`
- `src/tase_repro/force_feedback.py`
- `src/tase_repro/kinematics.py`
- `scripts/run_controller_smoke.py`
- `scripts/run_paper_trajectory_force_motion.py`
- `scripts/run_timing_feasibility_sweep.py`
- `tests/test_controller.py`
- `tests/test_force_motion.py`
- `tests/test_kinematics.py`
- Future: `src/tase_repro/contact.py`
- Future: `src/tase_repro/metrics.py`
- Future: `tests/*`

## Commands To Run

```bash
scripts/run_tests.sh
python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml
python3 scripts/run_ur10e_mujoco_adaptation.py --config configs/mujoco_ur10e.yaml --smoke
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

## Next Executable Step

Test a Stage A structure that changes task priority instead of only changing
orientation command magnitude or qdot budget. The next candidate should
preserve contact and planar position first, then use remaining velocity budget
for orientation; if that still fails, record a separate relaxed-drift
approach-budget decision before expanding staged checks to E2-E4.
