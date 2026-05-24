# Read-Only Calibration Measurement Evidence Finalizer Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v91-readonly-evidence-finalizer`

## Objective

Add a controlled offline transition from a scaffolded read-only measurement
run to an explicitly approved read-only evidence run, without weakening the
hard safety and claim-boundary gates added in v90.

## Artifacts

- New finalizer script:
  `scripts/finalize_read_only_calibration_measurement_evidence.py`
- Updated tests:
  `tests/test_read_only_calibration_measurement_template.py`

No live measurement run was created in this iteration.

## Result

The finalizer accepts a v88 scaffold run only if:

- the confirmation phrase exactly matches
  `I approve this read-only measurement step`
- `--approved-step-id` and `--operator` are non-empty and not `TBD`
- `--live-hardware-accessed` is explicitly declared as `true` or `false`
- required scaffold files are present
- `metrics.yaml` and `metrics.json` match before finalization
- the run status is still `scaffold_created_not_executed`
- all pre-finalization execution, verdict, and claim-boundary flags remain
  false
- default evidence statuses have not drifted
- at least one worksheet CSV contains a non-empty data row

It then writes the run to `approved_read_only_evidence`, sets
`execution.user_confirmed_read_only_step = true`, records the explicit
live-hardware-access metadata flag, derives read-only evidence statuses from
worksheet rows, rewrites `metrics.yaml` and `metrics.json` consistently,
updates `summary.md`, records git state, and self-checks the result through
the v90 `approved-read-only` audit mode.

The evidence-status derivation is intentionally narrow:

- `tcp_contact_measurements.csv` rows mark
  `mounted_stack_tcp_contact_point = collected_read_only`
- `plane_normal_measurements.csv` rows mark
  `plane_normal_robot_base_frame = collected_read_only`
- `force_source_comparison.csv` rows mark
  `force_source_frame_reconciliation = collected_read_only`
- KSM contact patch convention and orientation-gate semantics remain at their
  scaffold defaults unless separately represented by future worksheet or gate
  refinements

## Claim Boundary

V91 does not collect live measurements, execute the SOP, move the UR10e, write
configuration, zero/bias/filter the force sensor, run force control, reconcile
force-source frames, accept a replacement orientation gate, calibrate the
contact model, prove robustness, prove strict paper-equivalent feasibility, or
make a hardware-readiness claim.

The finalizer explicitly preserves false values for robot motion,
configuration writes, zeroing/biasing, force control, contact-model update,
gate relaxation, hardware claims, and hardware readiness.

## Validation

- `python3 -m py_compile scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  passed.
- `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  passed with `6 passed in 1.34s`.
- `scripts/run_tests.sh` passed with `121 passed in 4.01s`.
- `git diff --check` passed after full-test validation.

## Next Step

If a future live read-only step is explicitly approved, instantiate a fresh
run, fill only the approved worksheet rows, finalize it with
`scripts/finalize_read_only_calibration_measurement_evidence.py`, then run the
verifier with `--audit-mode approved-read-only`. If no live bench interaction
is approved, the next offline refinement should add explicit worksheet support
for the KSM contact patch convention and orientation-gate semantics.
