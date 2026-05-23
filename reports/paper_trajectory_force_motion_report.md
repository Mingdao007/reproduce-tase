# Paper Trajectory Force-Motion Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v6-paper-trajectory-force-motion`

Run:

`runs/paper_trajectory_force_motion/20260524T013829`

Command:

```bash
python3 scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e.yaml --duration-s 8.0 --target-force-N 5.0 --force-gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5 --trajectory e1-cycloid --amplitude-m 0.015 --omega-rad-s 0.1 --paper-time-scale 1.0 --planar-kp 0.5
```

## Scope

This run extends the straight tangential smoke to the paper's Section VI
Experiment 1 cycloid geometry:

```text
x = x0 + 0.015 * (0.1 t - sin(0.1 t))
y = y0 + 0.015 * (1 - cos(0.1 t))
```

It uses the same simulation-only, velocity-level UR10e controller as v5:
planar tracking plus normal-force feedback against MuJoCo contact force.

## Results

| metric | value |
| --- | ---: |
| target force | `5.0 N` |
| initial force | `5.886648180968636 N` |
| final force | `4.976020793039963 N` |
| tail mean force | `4.991015119073998 N` |
| tail mean absolute force error | `0.00898488092600231 N` |
| max absolute force error | `0.8866481809686357 N` |
| final tangential displacement | `[0.0012394851720925958, 0.004549066283786667] m` |
| desired tangential displacement | `[0.0012387489718280922, 0.00454724750054618] m` |
| mean tangential position error | `9.43368250982521e-07 m` |
| max tangential position error | `1.9621295447925046e-06 m` |
| solver success fraction | `1.0` |
| contact present fraction | `1.0` |
| max active bound count | `0` |
| max qdot | `0.013568982999521384 rad/s` |
| max qdot violation | `0.0 rad/s` |
| max joint-limit violation | `0.0 rad` |

## Interpretation

The approximate MuJoCo UR10e model can track the first paper-shaped planar path
at low speed while maintaining contact and holding the 5 N normal-force target
within about `0.009 N` tail mean absolute error. This is the first
paper-trajectory-shaped force-motion smoke in the repo.

## Limitations

- The run is simulation-only and uses the approximate, uncalibrated MJCF.
- The 85 mm TCP is still an unverified CAD guess.
- The paper's `z0`, orientation compliance, and impedance dynamics are still
  unresolved or not implemented.
- The force source is MuJoCo contact force, not OnRobot or UR RTDE.
- The initial posture and base z offset are simulation scaffolding.
- It is not hardware-ready and authorizes no real robot motion.

## Next Step

Add the remaining paper trajectory shapes as simulation-only force-motion
smokes, then separate trajectory tracking error from normal-force response in a
small experiment matrix before revisiting orientation compliance.
