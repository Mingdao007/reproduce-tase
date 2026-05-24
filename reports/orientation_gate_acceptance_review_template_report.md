# Orientation Gate Acceptance Review Template Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v94-gate-acceptance-review-template`

## Objective

Create a separate, non-default orientation gate-acceptance review path that
cannot be invoked by the read-only evidence finalizer. The scaffold must
default to `not_accepted` and preserve all hardware, calibration, gate
relaxation, and hardware-readiness claim boundaries.

## Artifacts

- New template:
  `templates/orientation_gate_acceptance_review/`
- New scaffold command:
  `scripts/create_orientation_gate_acceptance_review.py`
- New audit command:
  `scripts/audit_orientation_gate_acceptance_review.py`
- New scaffold run:
  `runs/orientation_gate_acceptance_review/20260525T020054`
- New scaffold audit:
  `runs/orientation_gate_acceptance_review_audit/20260525T020055`
- New tests:
  `tests/test_orientation_gate_acceptance_review_template.py`

## Result

The review template is intentionally separate from
`templates/read_only_calibration_measurement/` and the read-only finalizer. A
fresh review scaffold records:

```text
status = review_scaffold_not_executed
source_read_only_run = null
source_run_audit = null
approved_read_only_audit_passed = false
evidence_reviewed = false
user_approved_gate_acceptance_review = false
orientation_gate_acceptance.decision = not_accepted
orientation_gate_acceptance.review_only = true
accepted_gate_value_rad = null
supports_gate_relaxation = false
supports_hardware_claim = false
hardware_readiness = false
```

The audit rejects any drift toward an accepted gate, including non-null
accepted-gate fields and any false claim-boundary field changing to true.

The new scaffold audit passed:

```text
audit_passed = true
violations = []
review_status = review_scaffold_not_executed
decision = not_accepted
review_only = true
live_hardware_accessed = false
robot_motion_commanded = false
configuration_written = false
force_control_run = false
supports_gate_relaxation = false
supports_hardware_claim = false
hardware_readiness = false
artifact file count = 7
heavy_payloads = []
```

## Claim Boundary

V94 does not collect live measurements, execute the read-only SOP, move the
UR10e, write configuration, zero/bias/filter the force sensor, run force
control, reconcile force-source frames, accept a replacement orientation gate,
calibrate the contact model, prove robustness, prove strict paper-equivalent
feasibility, or make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/create_orientation_gate_acceptance_review.py scripts/audit_orientation_gate_acceptance_review.py scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py`
  passed.
- `scripts/run_tests.sh tests/test_orientation_gate_acceptance_review_template.py tests/test_read_only_calibration_measurement_template.py`
  passed with `11 passed in 2.03s`.
- `python3 scripts/create_orientation_gate_acceptance_review.py --review-id 20260525T020054`
  created the v94 review scaffold.
- `python3 scripts/audit_orientation_gate_acceptance_review.py runs/orientation_gate_acceptance_review/20260525T020054 --run-id 20260525T020055`
  passed.
- `scripts/run_tests.sh` passed with `126 passed in 4.72s`.
- `git diff --check` passed after full-test validation.

## Next Step

If a future live read-only measurement step is explicitly approved, use the
read-only measurement scaffold/finalizer/audit path first. The gate-acceptance
review template should remain unused until an approved-read-only evidence run
exists and a separate gate-acceptance review is explicitly authorized.
