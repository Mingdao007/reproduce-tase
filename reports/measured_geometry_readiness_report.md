# Measured Geometry Readiness Report

## Objective

V86 audits whether existing local records already constrain the mounted-stack
TCP/contact point, contact patch convention, plane/contact normal, and
force-source/frame definition tightly enough to support the v85
calibration-margin result.

The answer is no. Existing records are useful, but they are design metadata,
temporary hardware readbacks, analytic simulation assumptions, or unresolved
force-source observations. They do not justify accepting the v85 margin as a
calibrated correction, relaxing the diagnostic orientation gate, or making a
hardware-readiness claim.

## Source Records

- Hardware state:
  `/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/current_hardware_state.md`
- EOAT TCP note:
  `/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/eoat_design/EOAT_TCP_NOTE.md`
- EOAT v13 verification:
  `/home/andy/ur10e_lab_vault/onrobot/hex_e_v2_3010007655/eoat_design/v13_ksm8n_receiver_5p3mm_side_window_85mm/verification.json`
- Contact-point simulation config:
  `configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml`
- Contact-point MJCF:
  `assets/mjcf/ur10e_tilted_plane_10deg_tcp_contact_point.xml`
- V85 calibration margin:
  `runs/contact_orientation_calibration_margin/20260524T235723/metrics.yaml`

## Command

```bash
python3 scripts/audit_measured_geometry_readiness.py
```

Formal run:

- `runs/measured_geometry_readiness/20260525T000739`

Parent commit before v86 changes:

- `3a97eac42688c09c1d26d253c6fa8630163716c9`

## V85 Margin Under Audit

| quantity | value |
| --- | ---: |
| required normal rotation | `0.0005664520369604714 rad` |
| required normal rotation | `0.03245531101442353 deg` |
| equivalent base-z/contact-point correction | `0.014963398168061883 mm` |
| equivalent base-z/contact-point correction | `14.963398168061882 um` |
| accepted replacement gate in v85 | `false` |
| more Stage B qdot tuning supported in v85 | `false` |

## Readiness Checks

| check | status | measured record exists | constrains v85 margin |
| --- | --- | ---: | ---: |
| `mounted_stack_tcp_contact_point` | `insufficient_design_only` | `false` | `false` |
| `contact_patch_convention` | `insufficient_design_assumption` | `false` | `false` |
| `plane_contact_normal` | `insufficient_analytic_simulation_only` | `false` | `false` |
| `force_source_frame` | `unresolved_conflict` | `true` | `false` |
| `orientation_gate_semantics` | `not_accepted` | `false` | `false` |

## Evidence Summary

- The EOAT records provide a `85.0 mm` contact-point candidate from CAD/design
  metadata. The EOAT note explicitly treats it as a design candidate, not a
  verified UR10e TCP setting.
- The current UR TCP readback is `[0.0, 0.0, 0.12254, 0.0, 0.0, 0.0]`, with
  payload `0.44 kg`. The hardware note says this is temporary and not
  validated for contact experiments or force-control use.
- The OnRobot FT Setup record says `Use UR default TCP Configuration` is
  selected and `Set from sensor flange` is not selected.
- The KSM-8N dimensions and seating remain assumptions to confirm. The v13 CAD
  assembly excludes the purchased KSM placeholder from printable outputs, so
  the physical contact patch is not measured by the tracked CAD artifact.
- The MuJoCo contact normal is analytic: a single material plane tilted
  `10 deg` about `y`, with expected normal `[0.1736481777, 0.0, 0.984807753]`.
  There is no measured plane normal in the robot base frame.
- Force source/frame remains unresolved. Existing records show direct TCP DAQ
  `READFT` with `Fz mean = -32.7114 N` stopped and `-32.6699 N` while a
  no-motion wait program was running, while RTDE `actual_TCP_force` was
  observed around `0.30 N`. The current evidence says not to use direct TCP
  DAQ force values as control truth.

## V86 Answers

1. Measured mounted-stack TCP/contact point: not found. Existing records are a
   CAD candidate and temporary UR TCP readback.
2. `85.0 mm` EOAT datum: design contact-point candidate. The mounted KSM
   contact patch or ball datum is not verified.
3. Plane/contact normal: analytic MuJoCo tilted-plane assumption only. No
   robot-base-frame measurement exists.
4. Force source/frame: not reconciled. Direct TCP DAQ and RTDE/PolyScope force
   values disagree by about `32 N`.
5. Measurement uncertainty: no accepted uncertainty exists that is small enough
   to justify the v85 `0.03246 deg` or `14.96 um` correction.
6. Required measurement/SOP: mounted TCP/contact measurement, KSM contact-patch
   verification, plane-normal measurement, force-source reconciliation, and
   accepted orientation-gate semantics.
7. More Stage B qdot tuning: not supported. The missing evidence is
   geometry/normal/force-frame readiness, and v85 already showed `0.0` qdot
   saturation in the hard row.

## Measurement Checklist

- Measure mounted stack TCP/contact point from a named flange/sensor/tool
  datum.
- Measure or verify the physical KSM-8N contact datum and loaded contact patch
  convention.
- Measure the contact plane normal in the robot base frame and record angle
  uncertainty.
- Reconcile OnRobot URCap variables, UR RTDE, and direct TCP DAQ force
  frames/zeroing without robot motion.
- Define diagnostic orientation-gate semantics and uncertainty budget before
  relaxing any gate.
- Only after the read-only evidence is accepted, update simulation geometry or
  gate definitions in a separate branch.

## Claim Boundary

This audit is read-only local-record evidence. It is not:

- recovery of the `+1.0 mm`, `0.119 rad` row
- acceptance of a replacement orientation gate
- contact-model calibration
- a canonical controller default
- a robustness proof
- strict paper-equivalent feasibility
- hardware readiness or authorization to move/configure the real UR10e

## Validation

- `python3 -m py_compile scripts/audit_measured_geometry_readiness.py` passed.
- `python3 scripts/audit_measured_geometry_readiness.py` produced
  `runs/measured_geometry_readiness/20260525T000739`.
- `scripts/run_tests.sh`: `115 passed in 2.64s`.
- `git diff --check` passed.
- Artifact audit: `4` files, `44K`, no `.npz/.npy/.mat/.tar/.gz/.zip`
  payloads under `runs/measured_geometry_readiness/20260525T000739`.
- Branch push was verified at
  `70a1b35cf6436b284ed8bc8d1fcf936f9b0724a1`.

## Next Executable Step

Turn the measurement checklist into a read-only hardware/bench SOP. The first
useful next gate is a no-motion measurement plan for TCP/contact geometry,
plane normal, and force-source reconciliation, not Stage B qdot tuning.
