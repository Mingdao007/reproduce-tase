# Posture Feasibility Sweep Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v13-posture-feasibility`

Run root:

`runs/posture_feasibility_sweep/20260524T022145`

## Scope

This iteration tests whether a small simulation-only UR10e posture change can
move the E2/E3 feasibility boundary found in v12 closer to full paper timing.

Each posture is first calibrated to start near `5 N` normal force by changing
the MuJoCo `base_link` z offset. This is a model setup operation only; it is
not a robot command and must not be translated to the real UR10e.

Postures tested:

| name | initial q rad | calibrated base z offset m | initial force N |
| --- | --- | ---: | ---: |
| baseline | `[0, -0.02, 0.03, -0.01, 0, 0]` | `-1.8310546875000003e-05` | `5.003594660789989` |
| bend_0p03 | `[0, -0.03, 0.05, -0.02, 0, 0]` | `-8.544921875e-05` | `4.996673617685873` |
| bend_0p05 | `[0, -0.05, 0.08, -0.03, 0, 0]` | `-0.0002545166015625` | `5.004200770165302` |
| bend_0p075 | `[0, -0.075, 0.115, -0.04, 0, 0]` | `-0.0005566406250000001` | `5.009464736393783` |
| bend_0p10 | `[0, -0.1, 0.15, -0.05, 0, 0]` | `-0.0009710693359375` | `4.995281922830507` |

Common run settings:

- E2 figure-eight and E3 circle.
- `--paper-time-scale 1.0,0.75,0.6,0.5,0.35,0.25,0.2`
- `--use-slack-solve`
- `--planar-slack-weight 1`
- `--normal-slack-weight 10000`
- `--slack-constraint-weight 1000`
- `--qdot-limit-rad-s 0.15`
- `--force-gain 5e-4`

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

Fastest scale passing both E2 and E3:

| posture | fastest passing scale |
| --- | ---: |
| baseline | none |
| bend_0p03 | `0.25` |
| bend_0p05 | `0.5` |
| bend_0p075 | `0.75` |
| bend_0p10 | `1.0` |

Representative full-speed rows:

| posture | trajectory | pass | force error N | max pos err m | max planar slack m/s | qdot sat frac | tail qdot util |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | E2 | `False` | `0.08097697498404266` | `0.022994130404429502` | `0.014298549809126072` | `0.828` | `0.9999999999999998` |
| baseline | E3 | `False` | `0.022621162113788083` | `0.017242221453595254` | `0.011087649384373089` | `0.81` | `0.9999999999999998` |
| bend_0p075 | E2 | `False` | `0.002108501096022637` | `0.002538656201726373` | `0.004109752962304516` | `0.22225` | `0.9999999999999998` |
| bend_0p075 | E3 | `False` | `0.0008917036172458414` | `0.0028046925749286578` | `0.002652310734312028` | `0.22875` | `0.9999999999999998` |
| bend_0p10 | E2 | `True` | `0.0004002236522971103` | `8.944242301072789e-06` | `3.4331973232314785e-07` | `0.0` | `0.15222223080960362` |
| bend_0p10 | E3 | `True` | `0.000821132687569398` | `5.999914591097446e-06` | `1.1696023075496035e-06` | `0.0` | `0.27981610187783346` |

Full aggregate tables are in:

- `runs/posture_feasibility_sweep/20260524T022145/summary.md`
- `runs/posture_feasibility_sweep/20260524T022145/summary.csv`
- `runs/posture_feasibility_sweep/20260524T022145/summary.yaml`
- `runs/posture_feasibility_sweep/20260524T022145/summary.json`

## Interpretation

Posture is a dominant feasibility variable in the current velocity-level
UR10e adapted simulation. The lightly bent `bend_0p10` posture passes the
current E2/E3 full-speed gates without sustained qdot saturation, while the
near-straight calibrated baseline fails.

This does not mean the real robot should move to `bend_0p10`. It means the
baseline failure was not only a trajectory-speed issue; the current near-zero
posture is poorly conditioned for simultaneous planar motion and normal-force
regulation in the approximate MuJoCo model.

The v13 baseline is not a direct replacement for v12 because v13 recalibrates
the initial contact force to about `5 N`, while v12 used the earlier fixed
`-4e-5 m` base offset. The useful v13 result is the posture trend and the
full-speed passing evidence for `bend_0p10` under the calibrated setup.

## Limitations

- Simulation only. No real UR10e motion, TCP write, payload write, force
  zeroing, URCap setting, or OnRobot configuration change was performed.
- The posture is a MuJoCo initial condition, not a hardware command.
- Contact remains an approximate model setup via base z offset.
- Orientation compliance, torque dynamics, impedance behavior, and real
  force-source reconciliation are still missing.
- The postures are small synthetic candidates, not measured hardware-safe
  approach poses.

## Next Step

Use `bend_0p10` as the full-speed simulation baseline for the next controller
step, then add orientation compliance or a planned approach phase around that
posture. Before hardware consideration, reproduce the same posture read-only in
planning documents with measured TCP, payload, force-source, and emergency
stop gates.
