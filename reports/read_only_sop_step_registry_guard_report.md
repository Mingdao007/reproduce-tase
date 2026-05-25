# Read-Only SOP Step Registry Guard Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v119-readonly-step-registry-finalizer-guard`

Implementation commit: `IMPLEMENTATION_COMMIT_PENDING`

## Objective

Tighten the approval path for future read-only calibration evidence. The
read-only evidence finalizer previously required a non-empty
`--approved-step-id`, but did not verify that the ID named an exact SOP step or
that worksheet rows matched the approved step. V119 adds a machine-readable
step registry and guards finalization/audit against unknown step IDs and
out-of-scope worksheet rows.

No hardware command, live read, robot motion, configuration write, zeroing,
force-control step, contact/setup-target acceptance, orientation-gate
acceptance, or hardware-readiness claim is performed.

## Artifacts

- New registry:
  `configs/read_only_sop_step_registry.yaml`
- New registry audit:
  `scripts/audit_read_only_sop_step_registry.py`
- Updated finalizer:
  `scripts/finalize_read_only_calibration_measurement_evidence.py`
- Updated run auditor:
  `scripts/audit_read_only_calibration_measurement_run.py`
- Updated template:
  `templates/read_only_calibration_measurement/`
- New registry audit run:
  `runs/read_only_sop_step_registry_audit/20260525T094000`
- Updated tests:
  `tests/test_read_only_calibration_measurement_template.py`

## Result

The registry audit reports:

```text
audit_passed = true
violations = []
step_count = 6
finalizer_eligible_step_count = 5
finalizer_eligible_step_ids =
  phase1_mounted_stack_tcp_contact_measurement
  phase2_ksm_contact_patch_convention
  phase3_plane_normal_external_measurement
  phase4_force_source_read_only_comparison
  phase5_orientation_gate_semantics_evidence
```

The non-finalizer preflight step is:

```text
phase0_static_bench_preflight
```

Finalization now rejects:

- unknown `--approved-step-id` values
- step IDs not eligible for evidence finalization
- worksheet rows outside the approved step scope
- registry drift that weakens the no-motion/no-write/no-zeroing/no-force-control
  boundary

Approved read-only audits also check the recorded finalization metadata
against the registry and actual worksheet row counts.

## Claim Boundary

V119 is an approval-scoping and finalizer-guard change only. It does not
collect live measurements, execute the read-only SOP, move the UR10e, write
configuration, zero/bias/filter the force sensor, run force control, reconcile
force-source frames, accept a contact model, accept a setup target, relax a
gate, calibrate contact geometry, prove robustness, prove strict
paper-equivalent feasibility, or make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py scripts/audit_read_only_sop_step_registry.py scripts/create_read_only_calibration_measurement_run.py`
  passed.
- `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  passed with `12 passed in 2.34s`.
- `python3 scripts/audit_read_only_sop_step_registry.py --run-id 20260525T094000`
  created the v119 registry audit run.
- `rg -n "&id|\*id" runs/read_only_sop_step_registry_audit/20260525T094000/metrics.yaml`
  found no YAML anchors in the root summary metrics.
- `find runs/read_only_sop_step_registry_audit/20260525T094000 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `188 passed in 8.24s`.
- `git diff --check`
  passed.
- Branch push was verified at
  `BRANCH_PUSH_PENDING`.

## Next Step

The top blocker remains explicit approval for one exact read-only SOP step.
When approval exists, use one registered finalizer-eligible step ID and fill
only that step's allowed worksheet rows. Without approval, continue only
non-final offline work and keep all contact/setup-target, orientation-gate,
robustness, strict-feasibility, and hardware-readiness claims false.
