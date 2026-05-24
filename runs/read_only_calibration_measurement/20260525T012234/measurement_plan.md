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

- mounted-stack TCP/contact point
- KSM-8N contact patch convention
- plane normal in robot base frame
- force-source/frame reconciliation
- orientation-gate semantics

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
