# Read-Only Step Execution Preflight Audit

Run root: `/home/andy/reproduce-tase/runs/read_only_step_execution_preflight/20260525T101000`

- Audit passed: `True`
- Preflight ready steps: `5 / 5`
- Missing ready steps: `[]`
- Violations: `[]`
- Approved packets: `0`
- Execution-authorizing packets: `0`
- Live-access-authorizing packets: `0`

## Preflight Rows

- `phase1_mounted_stack_tcp_contact_measurement`: ready `True`, worksheets `['tcp_contact_measurements.csv']`
- `phase2_ksm_contact_patch_convention`: ready `True`, worksheets `['ksm_contact_patch_convention.csv']`
- `phase3_plane_normal_external_measurement`: ready `True`, worksheets `['plane_normal_measurements.csv']`
- `phase4_force_source_read_only_comparison`: ready `True`, worksheets `['force_source_comparison.csv']`
- `phase5_orientation_gate_semantics_evidence`: ready `True`, worksheets `['orientation_gate_semantics.csv']`

## Claim Boundary

This audit checks only offline command-path readiness. It does not
approve any packet, authorize live access, instantiate an approved
run, collect evidence, or support hardware readiness or goal
completion.
