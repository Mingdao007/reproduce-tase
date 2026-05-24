# Tilted Gain/Timing Sweep Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v23-tilted-gain-timing`

Starting commit: `e37a5545af1cb9d406848180a7ef5d772df7f4e8`

## Scope

Run the v22 tilted-plane force-normal orientation controller through a small
gain/time-scale grid. This remains simulation-only and does not move or write
settings to the real UR10e, OnRobot, TCP, payload, URCap, or force sensor.

Run root:

- `runs/tilted_orientation_gain_timing_sweep/20260524T091826`

## Sweep

Common setup:

- config: `configs/mujoco_ur10e_tilted_plane.yaml`
- trajectory: `e1-cycloid`
- orientation mode: `force-normal`
- orientation priority: `linear-primary`
- normal velocity mode: `contact-normal`
- initial q: `0,-0.1,0.15,-0.05,0,0`
- base z offset: `-0.0011631221220595766 m`
- qdot limit: `0.15 rad/s`
- target force: `5 N`
- duration: `2 s`
- gates: max orientation error `0.03 rad`, max angular slack `0.03 rad/s`,
  plus existing force-motion, qdot, and joint-limit gates.

Swept values:

- orientation kp: `0.1`, `0.25`, `0.5`, `1.0`, `2.0`, `5.0`
- paper time scale: `0.05`, `0.075`, `0.1`

The sweep was executed with `scripts/run_timing_feasibility_sweep.py` for each
orientation gain, using the values above.

## Result

Aggregate summary:

- cases: `18`
- passing cases: `0`
- best max orientation error: `0.17416151436895033 rad` at kp `2.0`, paper
  time scale `0.05`
- best non-saturating max orientation error: `0.1744456588511598 rad` at
  kp `0.25`, paper time scale `0.05`

No gain/time-scale pair passes the existing gates. Low gains avoid qdot
saturation but fail the max-orientation-error gate because the run starts with
about `0.174 rad` misalignment to the tilted normal. Gains at or above `0.5`
also fail qdot saturation and angular-slack gates.

Representative rows:

| kp | time scale | pass | failed criteria | max orientation error rad | max angular slack rad/s | qdot saturation fraction | tail qdot utilization |
| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| `0.1` | `0.075` | `False` | `max_orientation_error_rad` | `0.1744980186604636` | `7.001930470953769e-06` | `0.0` | `0.10864180071848975` |
| `0.25` | `0.075` | `False` | `max_orientation_error_rad` | `0.1744456588511598` | `7.987443653810365e-06` | `0.0` | `0.24531120157979486` |
| `0.5` | `0.075` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.17435839250232021` | `0.0376959415297048` | `0.229` | `1.0` |
| `1.0` | `0.075` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.17418386008451897` | `0.07466040890291388` | `1.0` | `1.0` |
| `5.0` | `0.075` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s` | `0.17416151436895033` | `0.6869592104751856` | `1.0` | `1.0` |

The aggregate machine-readable summary is:

- `runs/tilted_orientation_gain_timing_sweep/20260524T091826/summary.yaml`
- `runs/tilted_orientation_gain_timing_sweep/20260524T091826/summary.json`
- `runs/tilted_orientation_gain_timing_sweep/20260524T091826/summary.csv`
- `runs/tilted_orientation_gain_timing_sweep/20260524T091826/summary.md`

## Limits

- This is still a single analytic tilted plane, not a curved unknown surface.
- The sweep uses E1 only to isolate the orientation transition.
- The max-orientation-error gate includes the first sample, so a sudden change
  from flat initial orientation to a tilted force-normal target cannot pass
  without pre-alignment or an explicit approach phase.
- The controller remains velocity-level and kinematic, not the paper's
  torque-level finite-time RNN.

## Next Step

Stop treating scalar orientation gain as the main remaining knob for tilted
normal tracking. Implement or simulate a staged orientation approach phase
before paper-trajectory tracking, or explicitly decide to relax the qdot budget
and document that deviation.
