# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V93

Date: 2026-05-25

Use this after the v92 read-only worksheet coverage refinement. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v92 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v93.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_calibration_measurement_sop.md`
- `reports/read_only_calibration_measurement_template_report.md`
- `reports/read_only_calibration_measurement_run_audit_report.md`
- `reports/read_only_calibration_measurement_audit_modes_report.md`
- `reports/read_only_calibration_measurement_evidence_finalizer_report.md`
- `reports/read_only_calibration_measurement_worksheet_coverage_report.md`
- `runs/read_only_calibration_measurement/20260525T014755/metrics.yaml`
- `runs/read_only_calibration_measurement_run_audit/20260525T014756/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, not contact
calibrated, and not hardware-ready. The UR10e adapted line is diagnostic
simulation only. V87 defined a read-only measurement SOP, v88 created a
non-executed template/scaffold, v89 added an offline audit gate, v90 split the
audit gate into `scaffold` and `approved-read-only` modes, v91 added an
offline finalizer for approved read-only evidence runs, and v92 added explicit
KSM contact-patch and orientation-gate-semantics worksheet coverage. All these
steps still forbid robot motion, configuration writes, zeroing/biasing, force
control, contact-model updates, gate relaxation, hardware claims, and hardware
readiness.

Concrete v93 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v92 scaffold, v91 finalizer, and v90 verifier, or refine
orientation-gate acceptance semantics offline so collected read-only evidence
cannot be confused with gate relaxation. Do not move the real UR10e. Do not
write TCP, payload, CoG, URCap settings, OnRobot settings, RTDE registers,
zero/bias/filter settings, or run force control unless the user separately
approves that exact SOP step.
```

## Current Verified V92 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v92-readonly-worksheet-coverage
```

V92 worksheet artifacts:

```text
templates/read_only_calibration_measurement/ksm_contact_patch_convention.csv
templates/read_only_calibration_measurement/orientation_gate_semantics.csv
scripts/audit_read_only_calibration_measurement_run.py
scripts/finalize_read_only_calibration_measurement_evidence.py
runs/read_only_calibration_measurement/20260525T014755
runs/read_only_calibration_measurement_run_audit/20260525T014756
reports/read_only_calibration_measurement_worksheet_coverage_report.md
```

Key result:

```text
updated scaffold contains KSM and orientation semantics worksheets
scaffold audit validates optional worksheet headers when present
scaffold audit rejects optional worksheet rows in scaffold mode
finalizer derives KSM and orientation evidence statuses from optional rows
new scaffold audit passed with violations = []
robot motion = false
configuration writes = false
zeroing/biasing = false
force control = false
gate relaxation = false
hardware readiness = false
```

## Recommended V93 Work

Start with explicit user approval before any live bench read. If a specific
read-only step is approved, instantiate a fresh run folder, collect only the
approved worksheet rows, then run:

```bash
python3 scripts/finalize_read_only_calibration_measurement_evidence.py <run-folder> \
  --confirmation-phrase "I approve this read-only measurement step" \
  --approved-step-id <approved-step-id> \
  --operator <operator> \
  --live-hardware-accessed true

python3 scripts/audit_read_only_calibration_measurement_run.py <run-folder> \
  --audit-mode approved-read-only
```

If the user does not approve live bench interaction, refine the orientation
gate decision artifact and audit vocabulary offline so an orientation worksheet
row remains evidence collection, not gate acceptance.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zero/bias/filter, OnRobot
  configuration, or RTDE registers unless the user approves a separate exact
  SOP step.
- Do not use OnRobot direct TCP DAQ as control truth until the force-source
  discrepancy is resolved.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user.
