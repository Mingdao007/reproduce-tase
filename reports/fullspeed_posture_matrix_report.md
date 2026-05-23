# Full-Speed Posture Matrix Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v14-fullspeed-posture-matrix`

Run root:

`runs/fullspeed_posture_matrix/20260524T022724`

## Scope

This iteration uses the v13 calibrated `bend_0p10` simulation posture as a
full-speed E1-E4 matrix baseline. The purpose is to check whether the posture
that passed full-speed E2/E3 also passes the complete Section VI trajectory
set under the same v12 feasibility gates.

This is simulation-only MuJoCo evidence. The initial posture and base z offset
are model setup values, not real UR10e commands.

Common run settings:

- trajectories: E1 cycloid, E2 figure-eight, E3 circle, E4 cardioid
- `--time-scales 1.0`
- `--initial-q 0,-0.1,0.15,-0.05,0,0`
- `--base-z-offset-m=-0.0009710693359375`
- `--qdot-limit-rad-s 0.15`
- `--force-gain 5e-4`
- `--planar-slack-weight 1`
- `--normal-slack-weight 10000`
- `--slack-constraint-weight 1000`
- `--duration-s 8.0`
- `--target-force-N 5.0`

## Gates

The v12 feasibility gates are reused:

- solver success fraction `>= 1.0`
- contact present fraction `>= 1.0`
- tail mean absolute force error `<= 0.25 N`
- max tangential position error `<= 0.002 m`
- max planar velocity slack `<= 0.001 m/s`
- max absolute normal velocity slack `<= 0.0002 m/s`
- max qdot violation `<= 1e-9 rad/s`
- max joint-limit violation `<= 1e-9 rad`
- qdot saturation fraction `<= 0.01`
- tail max qdot utilization `<= 0.98`

## Results

All four trajectories pass at `paper_time_scale = 1.0`.

| trajectory | pass | force error N | contact | max pos err m | max planar slack m/s | max normal slack m/s | qdot sat frac | tail qdot util |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 cycloid | `True` | `0.00027102719026141477` | `1.0` | `2.0289880039871015e-06` | `1.897200973171906e-08` | `2.4887024409519794e-11` | `0.0` | `0.0270511666757969` |
| E2 figure-eight | `True` | `0.0004002236522971103` | `1.0` | `8.944242301072789e-06` | `3.4331973232314785e-07` | `6.468019924450903e-10` | `0.0` | `0.15222223080960362` |
| E3 circle | `True` | `0.000821132687569398` | `1.0` | `5.999914591097446e-06` | `1.1696023075496035e-06` | `1.3933000621302316e-09` | `0.0` | `0.27981610187783346` |
| E4 cardioid | `True` | `0.00017724280364998736` | `1.0` | `4.011419213392556e-06` | `4.479704402857127e-08` | `5.559575949227471e-11` | `0.0` | `0.054634419431542555` |

Full aggregate tables and per-trajectory plots are in:

- `runs/fullspeed_posture_matrix/20260524T022724/summary.md`
- `runs/fullspeed_posture_matrix/20260524T022724/summary.csv`
- `runs/fullspeed_posture_matrix/20260524T022724/summary.yaml`
- `runs/fullspeed_posture_matrix/20260524T022724/summary.json`

## Interpretation

The current full-speed planar force-motion baseline is no longer blocked by
E2/E3 under the calibrated `bend_0p10` MuJoCo posture. The same controller,
slack weights, qdot cap, force gain, and feasibility gates pass the complete
E1-E4 trajectory matrix.

The dominant change from v12 is posture and calibrated initial contact setup,
not a new controller. This supports the v13 conclusion that the near-straight
initial posture was poorly conditioned for the adapted 6DOF UR10e task.

## Limitations

- Simulation only. No real UR10e motion, TCP write, payload write, force
  zeroing, URCap setting, or OnRobot configuration change was performed.
- `bend_0p10` is a MuJoCo initial condition, not a hardware-approved approach
  pose.
- Contact is still approximate model setup through a static base z offset.
- Orientation compliance remains absent.
- The paper used a 7DOF manipulator; this repo is testing a 6DOF UR10e
  transfer under approximate contact.

## Next Step

Treat `bend_0p10` as the current full-speed MuJoCo baseline and add orientation
compliance or a planned approach phase around it. Any hardware planning remains
read-only until measured TCP, payload, force-source, and emergency-stop gates
are documented in a separate SOP.
