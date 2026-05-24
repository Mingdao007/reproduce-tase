# Read-Only Calibration Measurement Template Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v88-readonly-measurement-templates`

## Objective

Convert the v87 read-only calibration measurement SOP into a reusable,
non-executed run template and scaffold command. This supports later evidence
collection without implying that the SOP has been executed or that any hardware
claim is now valid.

## Artifacts

- Template root:
  `templates/read_only_calibration_measurement/`
- Scaffold command:
  `scripts/create_read_only_calibration_measurement_run.py`
- Template-only run:
  `runs/read_only_calibration_measurement/20260525T012234`
- Test:
  `tests/test_read_only_calibration_measurement_template.py`

## Result

The template contains planning/checklist files, empty CSV worksheets for
TCP/contact, plane-normal, and force-source evidence, an orientation-gate
decision placeholder, a photos/external-files manifest, and a metrics schema.
The scaffold command copies the template into a timestamped run folder, stamps
the run id, writes both `metrics.yaml` and `metrics.json`, records git state,
and prints the run path.

The generated v88 run is explicitly marked
`scaffold_created_not_executed`. Its metrics keep these flags false:

- `user_confirmed_read_only_step`
- `live_hardware_accessed`
- `robot_motion_commanded`
- `configuration_written`
- `zeroing_or_biasing_performed`
- `force_control_run`
- `supports_contact_model_update`
- `supports_accepting_v85_margin`
- `supports_gate_relaxation`
- `supports_hardware_claim`
- `hardware_readiness`

## Claim Boundary

V88 does not collect live measurements. It does not execute the SOP, move the
UR10e, write configuration, zero/bias/filter the force sensor, run force
control, reconcile force-source frames, accept a replacement orientation gate,
calibrate the contact model, prove robustness, prove strict paper-equivalent
feasibility, or make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/create_read_only_calibration_measurement_run.py`
  passed.
- `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  passed with `1 passed in 0.19s`.
- `scripts/run_tests.sh` passed with `116 passed in 2.82s`.
- `git diff --check` passed before full-test validation.
- Artifact audit: `12` files, `52K`, no
  `.npz/.npy/.mat/.tar/.gz/.zip` payloads under
  `runs/read_only_calibration_measurement/20260525T012234`.

## Next Step

Use the scaffold only after selecting an explicitly approved read-only SOP
step. If no live bench step is approved, continue refining worksheets and
acceptance gates without changing any hardware state.
