# Read-Only Calibration Measurement Run Audit Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v89-readonly-run-audit`

## Objective

Add an offline verifier for read-only calibration measurement run folders. The
verifier checks that a scaffolded run is still non-executed and cannot be
misread as contact calibration, orientation-gate relaxation, hardware evidence,
or hardware readiness.

## Artifacts

- Audit script:
  `scripts/audit_read_only_calibration_measurement_run.py`
- Audited run:
  `runs/read_only_calibration_measurement/20260525T012234`
- Audit run:
  `runs/read_only_calibration_measurement_run_audit/20260525T012835`
- Tests:
  `tests/test_read_only_calibration_measurement_template.py`

## Result

The audit passed for the v88 scaffold run. It verified required worksheet
files, `metrics.yaml` / `metrics.json` consistency, expected CSV headers,
non-executed run status, false execution flags, false hardware/gate/calibration
verdicts, false claim-boundary flags, expected `not_collected` evidence
statuses, and absence of heavy payloads.

The generated audit metrics report:

```text
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
```

## Claim Boundary

V89 does not collect live measurements. It does not execute the SOP, move the
UR10e, write configuration, zero/bias/filter the force sensor, run force
control, reconcile force-source frames, accept a replacement orientation gate,
calibrate the contact model, prove robustness, prove strict paper-equivalent
feasibility, or make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  passed.
- `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  passed with `3 passed in 0.63s`.
- `python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T012234 --run-id 20260525T012835`
  passed.
- `scripts/run_tests.sh` passed with `118 passed in 3.22s`.
- `git diff --check` passed before full-test validation.
- Artifact audit: `4` files, `20K`, no `.npz/.npy/.mat/.tar/.gz/.zip`
  payloads under
  `runs/read_only_calibration_measurement_run_audit/20260525T012835`.

## Next Step

Before any future worksheet-filled run is used as evidence, run this verifier
and keep unsupported claims false. Live bench evidence collection still
requires explicit approval for the exact read-only SOP step.
