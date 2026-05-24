# Measured Geometry Readiness Summary

Run root: `runs/measured_geometry_readiness/20260525T000739`

## V85 Margin

- Required normal rotation: `0.0005664520369604714` rad
- Required normal rotation: `0.03245531101442353` deg
- Equivalent geometry correction: `14.963398168061882` um

## Readiness Checks

| check | status | measured record | constrains v85 margin |
| --- | --- | ---: | ---: |
| `mounted_stack_tcp_contact_point` | `insufficient_design_only` | `False` | `False` |
| `contact_patch_convention` | `insufficient_design_assumption` | `False` | `False` |
| `plane_contact_normal` | `insufficient_analytic_simulation_only` | `False` | `False` |
| `force_source_frame` | `unresolved_conflict` | `True` | `False` |
| `orientation_gate_semantics` | `not_accepted` | `False` | `False` |

## Verdict

- Supports accepting v85 margin: `False`
- Supports gate relaxation: `False`
- Supports hardware claim: `False`
- Supports more Stage B qdot tuning: `False`

## Required Measurement Checklist

- Measure mounted stack TCP/contact point from a named flange/sensor/tool datum.
- Measure or verify the physical KSM-8N contact datum and loaded contact patch convention.
- Measure the contact plane normal in the robot base frame and record angle uncertainty.
- Reconcile OnRobot URCap variables, UR RTDE, and direct TCP DAQ force frames/zeroing without motion.
- Define the diagnostic orientation gate semantics and uncertainty budget before relaxing any gate.
- Only after the read-only evidence is accepted, update simulation geometry or gate definitions in a separate branch.
