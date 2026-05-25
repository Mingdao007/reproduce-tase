# Read-Only SOP Step Registry Audit

Run root: `/home/andy/reproduce-tase/runs/read_only_sop_step_registry_audit/20260525T094000`
Registry: `configs/read_only_sop_step_registry.yaml`

- Audit passed: `True`
- Step count: `6`
- Finalizer-eligible step count: `5`
- Finalizer-eligible steps: `['phase1_mounted_stack_tcp_contact_measurement', 'phase2_ksm_contact_patch_convention', 'phase3_plane_normal_external_measurement', 'phase4_force_source_read_only_comparison', 'phase5_orientation_gate_semantics_evidence']`

## Violations

- none

## Claim Boundary

The registry is an approval-scoping artifact only. It does not authorize
live access, robot motion, configuration writes, zeroing, force control,
contact/setup-target acceptance, gate relaxation, or hardware readiness.
