# Measurement Plan

Run status: `template_not_executed`

## Objective

Collect the read-only evidence required by
`reports/read_only_calibration_measurement_sop.md`.

## Scope

Allowed:

- static visual inspection
- manual worksheet entry
- read-only file/record inspection
- read-only UR/RTDE/Dashboard sampling only after explicit user confirmation

Not allowed:

- robot motion
- force control
- zeroing or biasing
- TCP, payload, CoG, URCap, OnRobot, or RTDE register writes
- treating direct OnRobot TCP DAQ `READFT` as control truth

## Required Evidence

- mounted-stack TCP/contact point:
  `tcp_contact_measurements.csv`
- KSM-8N contact patch convention:
  `ksm_contact_patch_convention.csv`
- plane normal in robot base frame:
  `plane_normal_measurements.csv`
- force-source/frame reconciliation:
  `force_source_comparison.csv`
- orientation-gate semantics:
  `orientation_gate_semantics.csv` and `orientation_gate_decision.md`

## Pre-Execution Gate

- User confirmation phrase:
  `I approve this read-only measurement step`
- Approved step ID:
  `TBD`
- Operator:
  `TBD`
- Date/time:
  `TBD`

## Abort Conditions

- contact risk
- cable strain
- confusing UI state
- unexpected safety mode
- request to move robot
- request to write configuration
- unresolved force-source mismatch being ignored
