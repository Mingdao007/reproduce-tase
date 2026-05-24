# Read-Only Calibration Measurement Worksheet Coverage Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v92-readonly-worksheet-coverage`

## Objective

Add explicit worksheet coverage for the two read-only evidence items that v91
still left as prose-only artifacts:

- KSM-8N contact patch convention
- orientation-gate semantics

The refinement must remain backward-compatible with older scaffold runs and
must not authorize live hardware access, robot motion, configuration writes,
zeroing/biasing, force control, gate relaxation, or hardware-readiness claims.

## Artifacts

- Added template worksheets:
  - `templates/read_only_calibration_measurement/ksm_contact_patch_convention.csv`
  - `templates/read_only_calibration_measurement/orientation_gate_semantics.csv`
- Updated template instructions:
  - `templates/read_only_calibration_measurement/README.md`
  - `templates/read_only_calibration_measurement/measurement_plan.md`
  - `templates/read_only_calibration_measurement/operator_checklist.md`
- Updated scripts:
  - `scripts/audit_read_only_calibration_measurement_run.py`
  - `scripts/finalize_read_only_calibration_measurement_evidence.py`
- New scaffold run:
  `runs/read_only_calibration_measurement/20260525T014755`
- New scaffold audit:
  `runs/read_only_calibration_measurement_run_audit/20260525T014756`
- Updated tests:
  `tests/test_read_only_calibration_measurement_template.py`

## Result

New scaffold runs now contain five worksheet CSVs:

- `tcp_contact_measurements.csv`
- `ksm_contact_patch_convention.csv`
- `plane_normal_measurements.csv`
- `force_source_comparison.csv`
- `orientation_gate_semantics.csv`

The audit gate remains backward-compatible: the KSM and orientation semantics
worksheets are optional for older runs, but if present their headers are
validated. Scaffold mode rejects rows in either optional worksheet.

The v91 finalizer now derives additional evidence statuses when optional
worksheet rows exist:

- `ksm_contact_patch_convention.csv` rows mark
  `ksm_contact_patch_convention = collected_read_only`
- `orientation_gate_semantics.csv` rows mark
  `orientation_gate_semantics = collected_read_only`

The new scaffold run passed:

```text
audit_mode = scaffold
audit_passed = true
violations = []
run_status = scaffold_created_not_executed
live_hardware_accessed = false
robot_motion_commanded = false
configuration_written = false
zeroing_or_biasing_performed = false
force_control_run = false
supports_gate_relaxation = false
supports_hardware_claim = false
hardware_readiness = false
artifact file count = 14
heavy_payloads = []
```

## Claim Boundary

V92 does not collect live measurements, execute the SOP, move the UR10e, write
configuration, zero/bias/filter the force sensor, run force control, reconcile
force-source frames, accept a replacement orientation gate, calibrate the
contact model, prove robustness, prove strict paper-equivalent feasibility, or
make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  passed.
- `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  passed with `7 passed in 1.56s`.
- `python3 scripts/create_read_only_calibration_measurement_run.py --run-id 20260525T014755`
  created the updated scaffold run.
- `python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T014755 --audit-mode scaffold --run-id 20260525T014756`
  passed.
- `scripts/run_tests.sh` passed with `122 passed in 4.26s`.
- `git diff --check` passed after full-test validation.
- Branch push was verified at
  `11bfa3ac02a06cf184343e119739e2392ae9cfbf`.

## Next Step

If a future live read-only step is explicitly approved, instantiate a fresh
run, fill only the approved worksheet rows, finalize it with
`scripts/finalize_read_only_calibration_measurement_evidence.py`, then run the
verifier with `--audit-mode approved-read-only`. If no live bench interaction
is approved, the remaining offline work is to refine pass/fail semantics for
orientation-gate acceptance without turning collected read-only evidence into
gate relaxation.
