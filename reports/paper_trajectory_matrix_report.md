# Paper Trajectory Matrix Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v7-paper-trajectory-matrix`

## Scope

This iteration extends the paper-shaped planar trajectory support from E1 only
to the Section VI E1-E4 trajectory family:

- E1 cycloid.
- E2 figure-eight.
- E3 circle.
- E4 cardioid.

The controller is still the simulation-only velocity-level UR10e force-motion
smoke: planar TCP tracking plus normal-force feedback using MuJoCo contact
force. E3 and E4 use `zero_initial_offset = true` so the simulation starts the
desired curve at the current TCP instead of injecting the paper curve's initial
center-relative offset as an instantaneous tracking error.

## Full-Speed Matrix, Conservative Limits

Run root: `runs/paper_trajectory_matrix/20260524T014139`

Common command shape:

```bash
python3 scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e.yaml --duration-s 8.0 --target-force-N 5.0 --force-gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5 --paper-time-scale 1.0 --planar-kp 0.5 --trajectory <trajectory>
```

| trajectory | tail mean abs force error N | max position error m | solver success | contact present | max qdot rad/s |
| --- | ---: | ---: | ---: | ---: | ---: |
| E1 cycloid | `0.00898488092600231` | `1.9621295447925046e-06` | `1.0` | `1.0` | `0.013568982999521384` |
| E2 figure-eight | `5.0` | `8.944233779332086e-06` | `1.0` | `0.424` | `0.04999392234580082` |
| E3 circle | `5.0` | `2.615710676688101e-05` | `1.0` | `0.426` | `0.049984317682033284` |
| E4 cardioid | `0.6582364172926808` | `3.2482774243285304e-06` | `1.0` | `1.0` | `0.024097415021617902` |

Interpretation:

The first full-speed matrix is negative evidence for the initial conservative
`0.05 rad/s` qdot cap. E2 and E3 solve their planar velocity tasks but lose
contact for most of the run, so their tail force error is the full `5 N`
target.

## Full-Speed Matrix, Higher Simulation Qdot Cap

Run root: `runs/paper_trajectory_matrix/20260524T014244`

This rerun used `--qdot-limit-rad-s 0.15`, matching the repo's staged
post-validation simulation cap and the paper-extracted experimental velocity
limit. E2 and E3 still lost contact:

| trajectory | tail mean abs force error N | max position error m | solver success | contact present | max qdot rad/s |
| --- | ---: | ---: | ---: | ---: | ---: |
| E1 cycloid | `0.00898488092600231` | `1.9621295447925046e-06` | `1.0` | `1.0` | `0.013568982999521384` |
| E2 figure-eight | `5.0` | `8.944233779332086e-06` | `1.0` | `0.424` | `0.06257171191905564` |
| E3 circle | `5.0` | `2.2364375253766477e-05` | `1.0` | `0.426` | `0.11746291997870727` |
| E4 cardioid | `0.6582364172926808` | `3.2482774243285304e-06` | `1.0` | `1.0` | `0.024097415021617902` |

Additional E2/E3 probes with `force_gain = 5e-4` saturated near the
`0.15 rad/s` cap and still did not restore contact. This suggests the current
velocity-level normal-force term is not enough for full-speed E2/E3 in the
approximate MJCF setup.

## Low-Speed Matrix

Run root: `runs/paper_trajectory_matrix/20260524T014344`

Common command shape:

```bash
python3 scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e.yaml --duration-s 8.0 --target-force-N 5.0 --force-gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5 --paper-time-scale 0.25 --planar-kp 0.5 --trajectory <trajectory>
```

| trajectory | tail mean abs force error N | max position error m | solver success | contact present | max qdot rad/s |
| --- | ---: | ---: | ---: | ---: | ---: |
| E1 cycloid | `2.7377314706467093e-06` | `1.2975956668356727e-07` | `1.0` | `1.0` | `0.013568982999521384` |
| E2 figure-eight | `0.22110301894575918` | `2.236053449085177e-06` | `1.0` | `1.0` | `0.013210458453207279` |
| E3 circle | `0.07713928700031802` | `1.4999786407036843e-06` | `1.0` | `1.0` | `0.013568982999521393` |
| E4 cardioid | `2.7477968988542934e-06` | `2.621139110103472e-07` | `1.0` | `1.0` | `0.013568982999521384` |

Interpretation:

The low-speed matrix is the accepted v7 baseline. All four paper trajectory
shapes can be tracked in contact with the current approximate MuJoCo UR10e
model when the paper time variable is scaled by `0.25`.

## Limitations

- These are trajectory-shape smokes, not full paper reproduction.
- The accepted matrix uses time scaling, so it is not a claim that the current
  controller reproduces full-speed Section VI experiments.
- Orientation compliance, impedance dynamics, `z0`, and full force-source
  reconciliation remain unresolved.
- The force source is MuJoCo contact force, not OnRobot or UR RTDE.
- No real robot motion, zeroing, TCP write, payload write, or URCap change was
  performed or authorized.

## Next Step

Investigate why full-speed E2/E3 lose contact in the approximate MJCF setup.
The likely next code step is a two-priority velocity solve or explicit
normal-force task weighting so normal contact is not lost while the planar task
is tracked.
