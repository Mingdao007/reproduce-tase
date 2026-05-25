# Read-Only Step Approval Packet

Packet ID: `20260525T100200`
Approval status: `not_approved`

## Exact Step

- Step ID: `phase4_force_source_read_only_comparison`
- Title: `Force-source read-only comparison evidence`
- Registry: `configs/read_only_sop_step_registry.yaml`
- Source SOP: `reports/read_only_calibration_measurement_sop.md`
- Finalizer eligible: `True`
- Live hardware access allowed only if separately approved: `True`

## Worksheet Scope

- `force_source_comparison.csv`

## Forbidden Actions

- `robot_motion`
- `force_control`
- `zeroing_or_biasing`
- `tcp_payload_cog_urcap_onrobot_or_rtde_writes`

## Required Confirmation

- Confirmation phrase: `I approve this read-only measurement step`
- Approved step ID: `phase4_force_source_read_only_comparison`
- Operator: `TBD`
- Live hardware accessed metadata: `true` or `false`, explicitly selected at finalization time

This packet is not an approval record. It does not authorize live access,
robot motion, configuration writes, zeroing, force control, contact/setup-target
acceptance, gate relaxation, or hardware readiness.
