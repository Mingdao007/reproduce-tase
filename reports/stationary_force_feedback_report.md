# Stationary Force Feedback Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v4-stationary-force-feedback`

Run:

`runs/stationary_force_feedback/20260524T013040`

Command:

```bash
python3 scripts/run_stationary_force_feedback.py --config configs/mujoco_ur10e.yaml --duration-s 4.0 --target-force-N 5.0 --gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5
```

## Scope

This is the first stationary, closed-loop, simulation-only normal-force
feedback smoke. It uses:

- the v1 approximate UR10e MuJoCo model;
- a lightly bent posture `q = [0, -0.02, 0.03, -0.01, 0, 0]`;
- positive MuJoCo contact-frame normal force;
- finite-time force error law for commanded TCP z velocity;
- bounded velocity solve for UR10e joint velocity limits.

It is not torque dynamics, not tangential trajectory tracking, not orientation
compliance, and not hardware-ready.

## Results

| metric | value |
| --- | ---: |
| target force | `5.0 N` |
| initial force | `5.886648180968636 N` |
| final force | `5.000002800044511 N` |
| tail mean force | `4.999999999997073 N` |
| tail mean absolute force error | `2.8000475610912012e-06 N` |
| solver success fraction | `1.0` |
| contact present fraction | `1.0` |
| max active bound count | `0` |
| max qdot violation | `0.0 rad/s` |
| max joint-limit violation | `0.0 rad` |

## Interpretation

The controller can regulate stationary MuJoCo normal contact force to the paper
target force of `5 N` in this approximate model and selected posture. This is
the first evidence that the contact sign, finite-time force error command, and
bounded velocity solve can work together.

## Limitations

- The initial posture and base z offset are simulation scaffolding, not robot
  commands.
- The model is not calibrated and the 85 mm TCP remains unverified.
- This does not validate OnRobot or UR RTDE force sources.
- No tangential motion, trajectory tracking, or orientation compliance is
  included.
- The run is kinematic velocity-level simulation; it does not model UR10e
  torque dynamics.

## Next Step

Extend from stationary force regulation to low-speed tangential motion while
holding normal force in simulation. Keep solver status, active bounds, force
error, position error, and contact-loss conditions visible in metrics.

