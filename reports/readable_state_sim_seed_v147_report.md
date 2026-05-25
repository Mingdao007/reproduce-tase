# Readable State Simulation Seed V147 Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v147-readable-state-sim-seed`

## Scope

V147 backs up the currently readable UR10e / OnRobot state while the real
UR10e is available, copies only lightweight simulation seed inputs into the
repository, and builds an offline calibrated MuJoCo seed from that snapshot.

The external backup root is:

```text
/home/andy/ur10e_ros2_ws/experiments/20260525_tase_sim_readable_state_backup
```

The repository-local lightweight inputs are:

```text
data/ur10e_real_snapshot_20260525T1641/current_ur10e_sim_seed.yaml
data/ur10e_real_snapshot_20260525T1641/ur10e_calibration.yaml
assets/urdf/ur10e_calibrated_20260525T1641.urdf
assets/mjcf/ur10e_calibrated_20260525T1641_tcp_offset.xml
configs/mujoco_ur10e_calibrated_20260525T1641_tcp_offset.yaml
```

No robot motion, URScript, RTDE input write, payload/TCP/URCap/OnRobot
configuration write, zeroing, biasing, filtering, or force-control command was
authorized or performed.

## Backup Result

The external backup contains read-only diagnostics for network/interface
state, dashboard state, payload/TCP/force readback, RTDE state, UR calibration,
UR RTDE force traces, direct OnRobot TCP DAQ traces, and URCap RTDE output
register probes.

Key backed-up values:

```text
calibration_hash = calib_7367377276742883610
payload_kg = 0.44
tcp_offset_z_m = 0.12254000000000001
actual_q_rad = [0.7058797478675842, -1.681310316125387, -2.5494725704193115, -0.4866345685771485, 1.5723538398742676, -0.867556397114889]
actual_tcp_pose_m_axis_angle = [0.4561937863181124, 0.16055373507071327, 0.044664812807231266, 3.1374700419770174, 0.007051636876497421, -0.006273548913546367]
```

The repository seed audit is:

```text
runs/current_real_snapshot_sim_seed_after_v146/20260525T210000
```

It reports:

```text
audit_passed = true
current_robot_state_backed_up = true
offline_simulation_can_continue_from_seed = true
repo_local_sim_seed_available = true
repo_local_calibration_available = true
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

The audit also shows why the previous nominal primitive MuJoCo model should not
be used for real-state replay:

```text
nominal_mujoco_to_rtde_tcp_position_error_m = 1.1351349451303372
nominal_mujoco_to_rtde_tcp_orientation_error_rad = 2.840514162594206
```

## Calibrated URDF Result

The calibrated URDF FK audit is:

```text
runs/calibrated_urdf_fk_snapshot_after_v147/20260525T211000
```

It verifies that the generated calibrated URDF plus the live TCP offset frame
matches the backed-up RTDE TCP pose:

```text
calibrated_urdf_fk_matches_rtde_tcp = true
best_frame_id = tool0_plus_live_tcp_offset_z
best_position_error_m = 2.0160035361820057e-06
best_orientation_error_rad = 6.278799181278485e-06
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

This is a kinematic model-alignment result only. It does not accept contact
geometry, force-frame semantics, setup targets, orientation gates, robustness,
hardware readiness, or completion.

## Calibrated MuJoCo Result

The calibrated MuJoCo replay audit is:

```text
runs/calibrated_mjcf_replay_after_v147/20260525T212000
```

It verifies that the simplified calibrated MJCF loads in MuJoCo and reproduces
the backed-up RTDE TCP pose from the seed joint state:

```text
mujoco_model_loads = true
model_nq = 6
model_nv = 6
model_nbody = 11
model_nsite = 1
calibrated_mjcf_replay_matches_rtde_tcp = true
position_error_m = 2.016003536429377e-06
orientation_error_rad = 6.278799181396437e-06
simulation_can_use_calibrated_mjcf_seed = true
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

The calibrated MJCF is now the preferred offline kinematic seed for continuing
simulation from the current real UR10e state. It intentionally does not encode
an accepted contact plane, contact patch, force-source truth, setup target, or
robustness proof.

## Validation

- `python3 -m py_compile scripts/audit_current_real_snapshot_sim_seed_after_v146.py`
- `scripts/run_tests.sh tests/test_current_real_snapshot_sim_seed_after_v146.py`
  reported `4 passed`.
- `scripts/run_tests.sh tests/test_calibrated_urdf_fk_snapshot_after_v147.py`
  reported `5 passed`.
- `scripts/run_tests.sh tests/test_calibrated_mjcf_replay_after_v147.py`
  reported `4 passed`.
- Full `scripts/run_tests.sh` reported `304 passed in 32.86s`.
- YAML anchor scan found no anchors in the new metrics, data, or config YAML
  files.
- Raw/heavy artifact scan found no payloads in the new lightweight data, run,
  URDF, or MJCF artifacts.
- `git diff --check` passed.

## Limit

V147 preserves and uses readable state for offline simulation only. It is not
approved read-only calibration evidence, does not approve any SOP packet, does
not authorize live execution, does not accept a contact model or setup target,
does not relax an orientation gate, does not prove strict paper-equivalent
feasibility, does not prove robustness, does not establish hardware readiness,
and does not close the completion gate.
