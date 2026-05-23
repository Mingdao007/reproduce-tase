# Force-Normal Orientation Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v21-force-normal-orientation`

Starting commit: `e1063f53aebb4e7904d1f0c4cc19725dc3bb0224`

## Scope

Add the first simulation-only orientation mode based on the paper's Section III
3D force-normal contract:

```text
u = F / ||F||
xdot_o = k_o e_o
```

This is not a real-robot controller and does not write UR10e, TCP, payload,
URCap, OnRobot, or force-sensor settings.

## Implementation

New code:

- `src/tase_repro/orientation.py`
  - `rotation_aligning_local_z_to_normal(...)`
- `src/tase_repro/contact_ladder.py`
  - `positive_contact_normal_force_vector(...)`

Updated code:

- `src/tase_repro/force_feedback.py`
  - `orientation_mode="force_normal"` computes desired TCP orientation from
    the summed positive MuJoCo contact-normal force vector.
  - If contact force is unavailable, the last valid desired rotation is held.
- `scripts/run_paper_trajectory_force_motion.py`
  - CLI mode `--orientation-mode force-normal`.
  - direct run folders now include `git_state.md`.
- Timing and posture sweep CLIs accept `--orientation-mode force-normal`.

Convention:

The paper gives a 3D force-normal vector but does not fully specify yaw around
that normal. This implementation aligns the TCP local z-axis to the 3D
contact-normal vector and preserves the initial TCP local x-axis projected into
the tangent plane when possible. That yaw convention is an explicit UR10e
adaptation, not a hidden paper claim.

## Verification

Commands:

```bash
python3 -m py_compile scripts/run_paper_trajectory_force_motion.py src/tase_repro/orientation.py src/tase_repro/contact_ladder.py src/tase_repro/force_feedback.py
scripts/run_tests.sh
git diff --check
python3 scripts/run_paper_trajectory_force_motion.py \
  --config configs/mujoco_ur10e.yaml \
  --output-dir runs/force_normal_orientation_smoke/20260524T045559 \
  --duration-s 1.0 \
  --target-force-N 5.0 \
  --force-gain 5e-4 \
  --r 0.5 \
  --base-z-offset-m=-0.0009710693359375 \
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
  --orientation-mode force-normal \
  --orientation-priority-mode linear-primary \
  --orientation-kp 5.0 \
  --angular-axis-weight 1.0 \
  --angular-slack-weight 1.0
```

Test result:

- `46 passed in 0.49s`
- `git diff --check` passed

Run root:

- `runs/force_normal_orientation_smoke/20260524T045559`

Key metrics:

| metric | value |
| --- | ---: |
| solver success fraction | `1.0` |
| contact present fraction | `1.0` |
| tail mean abs force error | `0.0002761445994167211 N` |
| max abs force error | `0.004718077169492574 N` |
| max tangential position error | `1.0164603681792251e-09 m` |
| max orientation error | `1.589167539872212e-06 rad` |
| max angular slack | `1.1092273136082997e-05 rad/s` |
| max qdot utilization | `0.01583281058707535` |
| qdot saturation fraction | `0.0` |
| max qdot violation | `0.0 rad/s` |
| max joint limit violation | `0.0 rad` |

## Limits

- The current MuJoCo contact surface is a flat plane with normal `+z`, so this
  smoke verifies wiring, metrics, and conventions rather than curved-surface
  normal adaptation.
- The controller is velocity-level and kinematic. It is not the paper's
  torque-level RNN inner loop.
- The force vector comes from MuJoCo contact data, not OnRobot/UR RTDE force
  sensing.
- The yaw convention around the force normal is a documented UR10e adaptation.
- This is not hardware-ready and must not be translated into real robot motion
  without the separate hardware gate.

## Next Step

Create a tilted or curved MuJoCo contact surface so `force_normal` orientation
has a nontrivial normal to track. Then rerun a small orientation-gated matrix
before revisiting full-speed E2/E3 claims.
