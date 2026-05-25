# Phase1 Row-Quality Guard Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v133-phase1-row-quality-guard`

Run: `runs/phase1_row_quality_guard/20260525T120000`

## Scope

This v133 audit hardens the future phase1 approved-read-only finalization path
by validating TCP/contact measurement row content before approved evidence can
be written. It exercises malformed phase1 rows in temporary dry-run scaffolds.
It does not approve phase1, create repository evidence, collect live
measurements, or authorize execution.

## Result

Key metrics:

```text
audit_passed = true
phase1_row_quality_guard_complete = true
source_sequence_boundary_audit_passed = true
case_count = 5
rejected_case_count = 5
scaffold_preserved_case_count = 5
approved_read_only_evidence_created_count = 0
repository_evidence_run_created = false
temp_only_dry_run = true
guarded_step_id = phase1_mounted_stack_tcp_contact_measurement
guarded_worksheet = tcp_contact_measurements.csv
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

| Case | Result |
| --- | --- |
| Placeholder datum | Rejected; scaffold preserved |
| Invalid tool-axis sign | Rejected; scaffold preserved |
| Nonnumeric distance | Rejected; scaffold preserved |
| Nonpositive resolution | Rejected; scaffold preserved |
| Placeholder row operator | Rejected; scaffold preserved |

## Interpretation

The finalizer and approved-read-only audit now reject malformed phase1
TCP/contact measurement rows. A future approved phase1 run still requires
explicit approval, a fresh scaffold, valid worksheet rows, finalization, and a
passed approved-read-only audit. This guard is not approved evidence.

## Validation

- `python3 -m py_compile scripts/audit_read_only_calibration_measurement_run.py scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_phase1_row_quality_guard.py`
- `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py tests/test_phase1_row_quality_guard.py`
  reported `17 passed in 6.00s`.
- `python3 scripts/audit_phase1_row_quality_guard.py --run-id 20260525T120000`
- Full tests reported `236 passed in 19.47s`.
- YAML anchor and raw/heavy artifact scans passed.
- `git diff --check` passed.

## Limit

This audit does not collect live measurements, approve a read-only SOP step,
create approved calibration evidence, accept a contact model, accept a setup
target, relax a gate, prove strict paper-equivalent feasibility, prove
robustness, establish hardware readiness, or authorize hardware work.
