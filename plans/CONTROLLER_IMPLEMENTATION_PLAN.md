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
- The first force-normal orientation smoke uses a flat MuJoCo plane, so it
  does not yet validate nontrivial curved-surface normal tracking.

## Next Executable Step

Use the v21 force-normal orientation mode on a tilted or curved MuJoCo contact
surface before revisiting full-speed orientation claims. Keep the v18
linear-primary `paper_time_scale = 0.075` matrix as the current flat-surface
orientation-gated fallback.
