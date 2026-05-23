# Tangential Force-Motion Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v5-tangential-force-motion`

Run:

`runs/tangential_force_motion/20260524T013342`

Command:

```bash
python3 scripts/run_tangential_force_motion.py --config configs/mujoco_ur10e.yaml --duration-s 4.0 --target-force-N 5.0 --force-gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5 --tangential-velocity 0.0005,0.0 --tangential-kp 0.5
```

## Scope

This is the first low-speed tangential force-motion smoke. It extends the
stationary normal-force feedback controller by commanding a small tangential
TCP velocity in x while regulating the MuJoCo normal contact force.

It is still simulation-only and velocity-level. It does not include orientation
compliance, torque dynamics, or hardware validation.

## Results

| metric | value |
| --- | ---: |
| target force | `5.0 N` |
| initial force | `5.886648180968636 N` |
| final force | `4.999976925773949 N` |
| tail mean force | `4.999982240215888 N` |
| tail mean absolute force error | `1.775978411200585e-05 N` |
| final tangential x displacement | `0.0019989989469737 m` |
| desired tangential x displacement | `0.0019990000000000008 m` |
| max tangential position error | `9.999917177300807e-07 m` |
| solver success fraction | `1.0` |
| contact present fraction | `1.0` |
| max active bound count | `0` |
| max qdot violation | `0.0 rad/s` |
| max joint-limit violation | `0.0 rad` |

## Interpretation

The approximate MuJoCo UR10e model can perform a low-speed x-direction
tangential motion while holding the 5 N normal-force target with the current
bounded velocity-level controller. This is the first UR10e adapted
force-motion smoke in the repo.

## Limitations

- The run uses the approximate, uncalibrated MJCF.
- The 85 mm TCP is still an unverified CAD guess.
- The initial posture and base z offset are simulation scaffolding.
- No orientation compliance is implemented.
- The force source is MuJoCo contact force, not OnRobot or UR RTDE.
- It is not hardware-ready and authorizes no real robot motion.

## Next Step

Extend this from a straight x smoke to the paper's first planar trajectory
shape in simulation, still at low speed and with explicit contact-loss,
force-error, solver-status, and limit metrics.

