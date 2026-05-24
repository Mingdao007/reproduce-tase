# Read-Only Calibration Measurement Orientation Acceptance Boundary Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v93-orientation-acceptance-boundary`

## Objective

Make the orientation-gate boundary explicit: collecting rows in
`orientation_gate_semantics.csv` can document read-only evidence, but it must
not imply that a replacement orientation gate was accepted.

## Artifacts

- Updated template metrics:
  `templates/read_only_calibration_measurement/metrics.yaml`
- Updated orientation decision artifact:
  `templates/read_only_calibration_measurement/orientation_gate_decision.md`
- Updated audit script:
  `scripts/audit_read_only_calibration_measurement_run.py`
- Updated finalizer:
  `scripts/finalize_read_only_calibration_measurement_evidence.py`
- New scaffold run:
  `runs/read_only_calibration_measurement/20260525T015400`
- New scaffold audit:
  `runs/read_only_calibration_measurement_run_audit/20260525T015401`
- Updated tests:
  `tests/test_read_only_calibration_measurement_template.py`

## Result

The read-only measurement metrics now carry an explicit
`orientation_gate_acceptance` block:

```yaml
decision: not_accepted
evidence_only: true
requires_separate_gate_audit: true
accepted_gate_type: null
accepted_gate_value_rad: null
accepted_normal_source: null
accepted_contact_datum_source: null
accepted_uncertainty_budget: null
orientation_semantics_rows: 0
```

The audit now rejects any approved read-only run that changes
`orientation_gate_semantics` evidence without preserving the not-accepted
orientation-gate boundary. It also rejects non-null accepted-gate fields and
checks that `orientation_gate_decision.md` still states
`Decision status: not_accepted`.

The finalizer preserves the same boundary even when orientation semantics rows
are present: `orientation_gate_semantics` may become `collected_read_only`,
but `orientation_gate_acceptance.decision` remains `not_accepted` and all
accepted-gate fields remain null.

The new scaffold run passed:

```text
audit_mode = scaffold
audit_passed = true
violations = []
run_status = scaffold_created_not_executed
orientation_gate_acceptance.decision = not_accepted
orientation_gate_acceptance.evidence_only = true
accepted_gate_value_rad = null
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

V93 does not collect live measurements, execute the SOP, move the UR10e, write
configuration, zero/bias/filter the force sensor, run force control, reconcile
force-source frames, accept a replacement orientation gate, calibrate the
contact model, prove robustness, prove strict paper-equivalent feasibility, or
make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  passed.
- `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  passed with `8 passed in 1.81s`.
- `python3 scripts/create_read_only_calibration_measurement_run.py --run-id 20260525T015400`
  created the v93 scaffold run.
- `python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T015400 --audit-mode scaffold --run-id 20260525T015401`
  passed.
- `scripts/run_tests.sh` passed with `123 passed in 4.43s`.
- `git diff --check` passed after full-test validation.

## Next Step

If a future live read-only step is explicitly approved, instantiate a fresh
run, fill only the approved worksheet rows, finalize it with
`scripts/finalize_read_only_calibration_measurement_evidence.py`, then run the
verifier with `--audit-mode approved-read-only`. If no live bench interaction
is approved, the next offline refinement should add a separate, non-default
gate-acceptance review template that remains disconnected from read-only
evidence finalization until explicitly authorized.
