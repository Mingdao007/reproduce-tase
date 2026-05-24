# Read-Only Calibration Measurement Audit Modes Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v90-readonly-evidence-audit-modes`

## Objective

Refine the read-only measurement run verifier so it can distinguish two safe
states:

- untouched scaffold runs
- future explicitly approved read-only evidence runs

The new `approved-read-only` mode allows user-confirmed read-only evidence
status changes and worksheet rows, while still rejecting robot motion,
configuration writes, zeroing/biasing, force control, contact-model updates,
gate relaxation, hardware claims, and hardware readiness.

## Artifacts

- Updated audit script:
  `scripts/audit_read_only_calibration_measurement_run.py`
- New scaffold-mode audit run:
  `runs/read_only_calibration_measurement_run_audit/20260525T013421`
- Tests:
  `tests/test_read_only_calibration_measurement_template.py`

## Result

The audit script now supports:

```text
--audit-mode scaffold
--audit-mode approved-read-only
```

`scaffold` mode requires the v88 run to remain
`scaffold_created_not_executed`, with user confirmation and live hardware
access false and all worksheets empty except headers.

`approved-read-only` mode requires:

- `status = approved_read_only_evidence`
- `execution.user_confirmed_read_only_step = true`
- `execution.live_hardware_accessed` is explicitly boolean
- at least one evidence-status field changes from the scaffold default
- evidence statuses stay within the read-only vocabulary
- hard safety and claim-boundary fields remain false

The v90 scaffold-mode audit of the existing v88 run passed:

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
```

## Claim Boundary

V90 does not collect live measurements. It does not execute the SOP, move the
UR10e, write configuration, zero/bias/filter the force sensor, run force
control, reconcile force-source frames, accept a replacement orientation gate,
calibrate the contact model, prove robustness, prove strict paper-equivalent
feasibility, or make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  passed.
- `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  passed with `4 passed in 0.86s`.
- `python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T012234 --audit-mode scaffold --run-id 20260525T013421`
  passed.
- `scripts/run_tests.sh` passed with `119 passed in 3.50s`.
- `git diff --check` passed before full-test validation.
- Artifact audit: `4` files, `20K`, no `.npz/.npy/.mat/.tar/.gz/.zip`
  payloads under
  `runs/read_only_calibration_measurement_run_audit/20260525T013421`.
- Branch push was verified at
  `aa4f48f8cb87d5af1f0051f65768fbc09e3c06ab`.

## Next Step

If a future live read-only step is explicitly approved, instantiate a fresh
run, fill only the approved worksheet rows, set
`status = approved_read_only_evidence`, then run the verifier with
`--audit-mode approved-read-only`. Hardware writes, zeroing, force control, and
robot motion still require a separate approved SOP.
