# Downstream Row-Quality Guard Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v134-downstream-row-quality-guard`

Run: `runs/downstream_row_quality_guard/20260525T121000`

## Scope

This v134 audit hardens the downstream registered read-only finalization path
for phase2 through phase5 worksheets. It validates row content for KSM contact
patch convention, plane normal, force-source comparison, and orientation-gate
semantics before approved evidence can be written. It exercises malformed rows
in temporary dry-run scaffolds only.

## Result

Key metrics:

```text
audit_passed = true
downstream_row_quality_guard_complete = true
source_phase1_guard_audit_passed = true
case_count = 4
rejected_case_count = 4
scaffold_preserved_case_count = 4
approved_read_only_evidence_created_count = 0
repository_evidence_run_created = false
temp_only_dry_run = true
guarded_downstream_step_count = 4
approved_packet_count = 0
execution_authorizing_packet_count = 0
live_access_authorizing_packet_count = 0
approved_read_only_evidence_created = false
guard_authorizes_live_access = false
guard_authorizes_execution = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

Rejected row-quality cases:

| Case | Step | Worksheet | Result |
| --- | --- | --- | --- |
| Placeholder contact-patch description | `phase2_ksm_contact_patch_convention` | `ksm_contact_patch_convention.csv` | Rejected; scaffold preserved |
| Nonunit plane normal | `phase3_plane_normal_external_measurement` | `plane_normal_measurements.csv` | Rejected; scaffold preserved |
| Negative force-source timestamp | `phase4_force_source_read_only_comparison` | `force_source_comparison.csv` | Rejected; scaffold preserved |
| Accepted orientation decision row | `phase5_orientation_gate_semantics_evidence` | `orientation_gate_semantics.csv` | Rejected; scaffold preserved |

## Interpretation

The finalizer and approved-read-only audit now reject malformed downstream
read-only worksheet rows. A future approved downstream run still requires
explicit approval, a fresh scaffold, valid worksheet rows, finalization, and a
passed approved-read-only audit. This guard is not approved evidence.

## Validation

- `python3 -m py_compile scripts/audit_read_only_calibration_measurement_run.py scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_downstream_row_quality_guard.py`
- `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py tests/test_downstream_row_quality_guard.py`
  reported `21 passed in 6.27s`.
- `python3 scripts/audit_downstream_row_quality_guard.py --run-id 20260525T121000`
- Full tests reported `243 passed in 23.16s`.
- YAML anchor and raw/heavy artifact scans passed.
- `git diff --check` passed.

## Limit

This audit does not collect live measurements, approve a read-only SOP step,
create approved calibration evidence, accept a contact model, accept a setup
target, relax a gate, prove strict paper-equivalent feasibility, prove
robustness, establish hardware readiness, or authorize hardware work.
