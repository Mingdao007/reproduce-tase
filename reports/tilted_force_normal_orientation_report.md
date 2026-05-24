# Tilted Force-Normal Orientation Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v22-tilted-force-normal`

Starting commit: `8745c0d284058a2c42185d17d25276c449d405c9`

## Scope

Add a nontrivial MuJoCo contact normal for the v21 force-normal orientation
mode. This iteration stays simulation-only and does not move or write settings
to the real UR10e, OnRobot, TCP, payload, URCap, or force sensor.

## Model And Controller Changes

New files:

- `assets/mjcf/ur10e_tilted_plane_10deg.xml`
- `configs/mujoco_ur10e_tilted_plane.yaml`

The tilted plane is rotated `0.1745329252 rad` about the y-axis. The expected
world normal is:

```text
[0.1736481777, 0.0, 0.9848077530]
```

The controller now accepts:

```text
normal_velocity_mode = "world_z" | "contact_normal"
```

`contact_normal` maps the scalar finite-time force correction onto the measured
3D MuJoCo contact-normal force direction. The default remains `world_z` for
backward compatibility with previous flat-surface runs.

## Verification

Commands:

```bash
python3 -m py_compile src/tase_repro/force_feedback.py scripts/run_paper_trajectory_force_motion.py scripts/run_timing_feasibility_sweep.py scripts/run_posture_feasibility_sweep.py
scripts/run_tests.sh
git diff --check
python3 scripts/run_paper_trajectory_force_motion.py \
  --config configs/mujoco_ur10e_tilted_plane.yaml \
  --output-dir runs/tilted_force_normal_orientation_smoke/20260524T050139 \
  --duration-s 1.0 \
  --target-force-N 5.0 \
  --force-gain 5e-4 \
  --r 0.5 \
  --base-z-offset-m=-0.0011631221220595766 \
  --initial-q 0,-0.1,0.15,-0.05,0,0 \
  --qdot-limit-rad-s 0.15 \
  --trajectory e1-cycloid \
  --omega-rad-s 0.1 \
  --paper-time-scale 0.075 \
  --planar-kp 0.5 \
  --use-slack-solve \
  --planar-slack-weight 1.0 \
  --normal-slack-weight 10000.0 \
  --slack-constraint-weight 1000.0 \
  --normal-velocity-mode contact-normal \
  --orientation-mode force-normal \
  --orientation-priority-mode linear-primary \
  --orientation-kp 5.0 \
  --angular-axis-weight 1.0 \
  --angular-slack-weight 1.0
```

Additional low-gain comparison:

```bash
python3 scripts/run_paper_trajectory_force_motion.py \
  --config configs/mujoco_ur10e_tilted_plane.yaml \
  --output-dir runs/tilted_force_normal_orientation_smoke/20260524T050139_kp0p1 \
  --duration-s 2.0 \
  --target-force-N 5.0 \
  --force-gain 5e-4 \
  --r 0.5 \
  --base-z-offset-m=-0.0011631221220595766 \
  --initial-q 0,-0.1,0.15,-0.05,0,0 \
  --qdot-limit-rad-s 0.15 \
  --trajectory e1-cycloid \
  --omega-rad-s 0.1 \
  --paper-time-scale 0.075 \
  --planar-kp 0.5 \
  --use-slack-solve \
  --planar-slack-weight 1.0 \
  --normal-slack-weight 10000.0 \
  --slack-constraint-weight 1000.0 \
  --normal-velocity-mode contact-normal \
  --orientation-mode force-normal \
  --orientation-priority-mode linear-primary \
  --orientation-kp 0.1 \
  --angular-axis-weight 1.0 \
  --angular-slack-weight 1.0
```

Test result:

- `49 passed in 0.54s`
- `git diff --check` passed

## Results

| run | orientation kp | duration s | force tail MAE N | max orientation error rad | tail orientation error rad | max angular slack rad/s | qdot saturation fraction | tail qdot saturation fraction | max qdot utilization |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `runs/tilted_force_normal_orientation_smoke/20260524T050139` | `5.0` | `1.0` | `0.003091381344228328` | `0.17416151436895033` | `0.07593713278249946` | `0.6869592104751856` | `1.0` | `1.0` | `1.0000000000000002` |
| `runs/tilted_force_normal_orientation_smoke/20260524T050139_kp0p1` | `0.1` | `2.0` | `0.00017028171203874897` | `0.1744980186604636` | `0.14577470816672422` | `7.001930470953769e-06` | `0.0` | `0.0` | `0.11851363953855767` |

Both runs maintain contact and solver success fraction `1.0`. Neither run is
a complete orientation-gated pass:

- `kp = 5.0` reduces tail orientation error more quickly but saturates the
  `0.15 rad/s` qdot budget throughout the run.
- `kp = 0.1` avoids qdot saturation but leaves the TCP orientation far from
  the tilted normal after 2 seconds.

## Limits

- This is a single tilted analytic plane, not a curved unknown surface.
- The approximate UR10e MJCF and unverified 85 mm TCP remain simulation
  scaffolding.
- The controller is velocity-level and kinematic, not the paper's torque-level
  finite-time RNN.
- The qdot/gain tradeoff is now visible but not solved.

## Next Step

Run a small orientation-gain/timing sweep on the tilted plane and gate it with
the existing orientation thresholds. If no gain passes without qdot
saturation, the next controller decision should be an explicit orientation
approach phase or qdot-budget tradeoff rather than another scalar gain tweak.
