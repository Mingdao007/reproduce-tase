# Read-Only Calibration Measurement SOP

## Purpose

This SOP defines the read-only evidence needed before the project may accept
the v85 calibration margin, relax the diagnostic orientation gate, update the
contact model from physical measurements, or make any hardware-readiness claim.

It is a planning and gate artifact only. It was not executed in v87.

## Source Boundary

The SOP is based on:

- `reports/measured_geometry_readiness_report.md`
- `runs/measured_geometry_readiness/20260525T000739/metrics.yaml`
- `/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/current_hardware_state.md`
- `/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/eoat_design/EOAT_TCP_NOTE.md`
- `/home/andy/codex-private-skills/skills/ur10e-realsetup/references/eoat-v13-onrobot-context.md`

V85 margin under audit:

| quantity | value |
| --- | ---: |
| required normal rotation | `0.0005664520369604714 rad` |
| required normal rotation | `0.03245531101442353 deg` |
| equivalent geometry correction | `0.014963398168061883 mm` |
| equivalent geometry correction | `14.963398168061882 um` |

## Absolute Safety Boundary

Do not perform any of the following under this SOP:

- robot motion
- force-control execution
- `zero_ftsensor()`
- OnRobot `F/T Zero`
- OnRobot `F/T Set TCP`
- UR TCP, payload, CoG, URCap, OnRobot, or RTDE register writes
- Compute Box setting changes
- vendor template `.urp` execution
- use direct OnRobot TCP DAQ `READFT` as control truth

If a required step appears to need a write, motion, zeroing, or force-control
action, stop and create a separate explicit SOP for user approval.

## Required Artifacts

Create one timestamped folder for any future execution:

```text
runs/read_only_calibration_measurement/<YYYYMMDDTHHMMSS>/
```

Minimum contents:

- `measurement_plan.md`
- `operator_checklist.md`
- `tcp_contact_measurements.csv`
- `plane_normal_measurements.csv`
- `force_source_comparison.csv`
- `orientation_gate_decision.md`
- `photos_manifest.md`
- `metrics.yaml`
- `summary.md`
- `git_state.md`

All raw photos or large files should be referenced by manifest path unless Git
LFS is explicitly configured for that artifact class.

## Phase 0 - Preconditions

Objective: prove the bench is in a safe static state before collecting
measurements.

User-side checks:

1. Robot is not touching the environment.
2. No force-control program is running.
3. EOAT, KSM-8N, OnRobot HEX-E, Adapter Flange A, and cables are visually
   reachable and safe to inspect without moving the robot.
4. Emergency stop path is known.
5. No one will press Play, Freedrive, zero, or TCP/payload setup controls
   during measurement.

Codex-side checks, read-only only:

```bash
git status --short --branch
sed -n '1,220p' /home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/current_hardware_state.md
```

Pass gate:

- static bench confirmed by user
- no write/motion/zeroing action planned
- current hardware-state file consulted

Abort gate:

- any contact risk, cable strain, unexpected safety mode, confusing UI state,
  or request to write TCP/payload/zero settings

## Phase 1 - Mounted Stack TCP/Contact Point

Objective: replace the design-only `85.0 mm` candidate with measured mounted
stack geometry.

Required measurement records:

- reference datum name: UR flange, OnRobot sensor flange, Adapter Flange A
  face, or another explicitly identified face
- sign convention in UR tool frame
- measured distance from datum to physical contact datum
- at least three repeated measurements
- instrument type, resolution, calibration state, and operator
- photos showing datum, measurement setup, KSM seating, and contact point

CSV schema:

```text
sample_id,datum,tool_axis_sign,distance_mm,instrument,resolution_mm,operator,notes
```

Pass gate for model update:

- datum and sign convention are unambiguous
- repeat range is recorded
- measured value can be traced to the mounted UR10e + OnRobot + EOAT stack

Pass gate for accepting the v85 `14.963398168061882 um` margin:

- expanded uncertainty is less than or equal to `0.014963398168061883 mm`
- datum bias is bounded or corrected
- KSM contact datum is the same datum used by the orientation/contact gate

Fail gate:

- only CAD metadata is available
- only the current UR TCP readback `[0, 0, 0.12254, 0, 0, 0]` is available
- uncertainty exceeds `0.014963398168061883 mm`

## Phase 2 - KSM Contact Patch Convention

Objective: decide whether the physical contact datum is ball top, ball center,
loaded patch, receiver face, or another point.

Required records:

- KSM-8N seating photo after installation
- measured protrusion or ball-top location relative to receiver/front face
- loaded versus unloaded contact-state convention
- whether the CAD placeholder dimensions match the purchased part
- whether hot glue or nut seating changes the contact datum

Pass gate:

- contact datum can be named and related to the TCP/contact measurement
- CAD assumption differences are either measured or bounded

Fail gate:

- purchased KSM-8N seating remains assumed
- contact datum is still described only as the `85.0 mm` design candidate

## Phase 3 - Plane Normal In Robot Base Frame

Objective: replace the analytic MuJoCo `10 deg` plane normal with a measured
robot-base-frame normal.

CSV schema:

```text
sample_id,method,normal_x,normal_y,normal_z,angle_uncertainty_deg,notes
```

Allowed read-only measurement approaches:

- fixture or external metrology that does not command robot motion
- manually recorded static poses only if a separate approved no-motion data
  collection protocol exists
- existing photos or measurements only if datum and uncertainty are explicit

Pass gate for model update:

- normal vector is normalized and expressed in the robot base frame
- method and uncertainty are documented

Pass gate for accepting the v85 `0.03245531101442353 deg` margin:

- expanded angle uncertainty is less than or equal to
  `0.03245531101442353 deg`
- the measured normal belongs to the same surface/contact condition used in
  the diagnostic gate

Fail gate:

- only the MuJoCo analytic normal `[0.1736481777, 0, 0.984807753]` is available
- uncertainty exceeds `0.03245531101442353 deg`

## Phase 4 - Force Source And Frame Reconciliation

Objective: decide which force source can be used as diagnostic truth.

Current blocker:

- direct OnRobot TCP DAQ `READFT` has reported about `-32.7 N` Fz in states
  where RTDE/PolyScope values were near zero

Required records:

- UR RTDE `actual_TCP_force`
- PolyScope OnRobot variables exported to RTDE registers, if separately
  approved and configured
- direct OnRobot TCP DAQ `READFT`, recorded as informational until reconciled
- zero/reference/frame state for every source
- no-contact static state and payload/TCP readback

CSV schema:

```text
timestamp_s,source,Fx_N,Fy_N,Fz_N,Tx_Nm,Ty_Nm,Tz_Nm,zero_state,frame,notes
```

Pass gate:

- selected control/diagnostic force source has documented zero and frame
- same-state disagreement is within a predeclared tolerance, initially
  `0.5 N` for no-contact Fz comparison
- direct TCP DAQ is not used as control truth unless its offset/frame is
  explained and validated

Fail gate:

- direct TCP DAQ and RTDE/PolyScope remain separated by about `32 N`
- the source frame or zero state is unknown

## Phase 5 - Orientation Gate Semantics

Objective: define what the diagnostic orientation gate measures before any
replacement gate is considered.

Required decision fields:

- gate type: force-normal-only or full-frame rotation
- normal source: measured normal, analytic simulation normal, or other
- contact datum source
- uncertainty budget
- accepted gate value and reason
- claim scope: simulation diagnostic, calibrated model, or hardware-ready

Pass gate:

- gate definition is machine-readable in `metrics.yaml`
- uncertainty budget covers both geometry and normal measurement
- replacement gate, if any, is tied to measured evidence rather than
  simulation recovery alone

Fail gate:

- gate is accepted only because `0.11955`, `0.1196`, or `0.11995 rad`
  recovered a simulation row
- normal/contact datum remains unmeasured

## Phase 6 - Summary Decision

The final summary must set these booleans explicitly:

```yaml
supports_contact_model_update: false
supports_accepting_v85_margin: false
supports_gate_relaxation: false
supports_hardware_claim: false
supports_more_stage_b_qdot_tuning: false
```

Set any value to `true` only if the preceding pass gates are met by concrete
artifacts.

## Claim Boundary

Completing this SOP design does not itself prove:

- recovery of the `+1.0 mm`, `0.119 rad` row
- a calibrated contact model
- an accepted replacement orientation gate
- robust UR10e adapted performance
- strict paper-equivalent feasibility
- hardware readiness

## Validation

- `scripts/run_tests.sh`: `115 passed in 2.65s`.
- `git diff --check` passed.
- No live hardware commands were run.
- Branch push was verified at
  `e60a90cfb112e4f5962c67efc2abbbcc3db313d0`.

## Next Executable Step

Before execution, create a new branch and run folder for the measurement
session. Keep all live-bench actions read-only unless the user separately
approves a specific write, zeroing, or motion SOP.
