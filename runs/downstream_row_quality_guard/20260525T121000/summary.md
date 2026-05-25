# Downstream Row-Quality Guard Audit

Run id: `20260525T121000`

Audit passed: `True`
Guard complete: `True`
Case count: `4`
Rejected cases: `4`
Scaffold-preserved cases: `4`
Approved evidence created in dry runs: `0`
Repository evidence run created: `False`
Guard authorizes execution: `False`
Completion claim allowed: `False`
Do not mark goal complete: `True`

Rejection cases:

| Case | Step | Worksheet | Rejected | Scaffold preserved | Expected stderr |
| --- | --- | --- | ---: | ---: | --- |
| `phase2_placeholder_contact_patch_description` | `phase2_ksm_contact_patch_convention` | `ksm_contact_patch_convention.csv` | `True` | `True` | `contact_patch_description must be non-empty and not a placeholder` |
| `phase3_nonunit_plane_normal` | `phase3_plane_normal_external_measurement` | `plane_normal_measurements.csv` | `True` | `True` | `normal_vector must have unit length` |
| `phase4_negative_timestamp` | `phase4_force_source_read_only_comparison` | `force_source_comparison.csv` | `True` | `True` | `timestamp_s must be nonnegative` |
| `phase5_accepted_decision_row` | `phase5_orientation_gate_semantics_evidence` | `orientation_gate_semantics.csv` | `True` | `True` | `decision must be one of` |

Violations:

- None

Interpretation:

The finalizer rejects malformed downstream read-only worksheet rows before approved evidence can be written. No repository evidence run is created, and this audit authorizes no live access or execution.
