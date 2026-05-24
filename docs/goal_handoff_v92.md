# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V92

Date: 2026-05-25

Use this after the v91 read-only evidence finalizer. Verify every claim from
repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v91 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v92.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_calibration_measurement_sop.md`
- `reports/read_only_calibration_measurement_template_report.md`
- `reports/read_only_calibration_measurement_run_audit_report.md`
- `reports/read_only_calibration_measurement_audit_modes_report.md`
- `reports/read_only_calibration_measurement_evidence_finalizer_report.md`
- `runs/read_only_calibration_measurement/20260525T012234/metrics.yaml`
- `runs/read_only_calibration_measurement_run_audit/20260525T013421/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, not contact
calibrated, and not hardware-ready. The UR10e adapted line is diagnostic
simulation only. V87 defined a read-only measurement SOP, v88 created a
non-executed template/scaffold, v89 added an offline audit gate, v90 split the
audit gate into `scaffold` and `approved-read-only` modes, and v91 added an
offline finalizer that can convert a worksheet-filled scaffold into
`approved_read_only_evidence` only when the exact read-only approval phrase,
approved step ID, operator, explicit live-read metadata flag, and worksheet
rows are present. The finalizer still forbids robot motion, configuration
writes, zeroing/biasing, force control, contact-model updates, gate
relaxation, hardware claims, and hardware readiness.

Concrete v92 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v88 scaffold, v91 finalizer, and v90 verifier, or refine the
worksheets/audit gates for KSM contact patch convention and orientation-gate
semantics if the measurement path is still ambiguous. Do not move the real
UR10e. Do not write TCP, payload, CoG, URCap settings, OnRobot settings, RTDE
registers, zero/bias/filter settings, or run force control unless the user
separately approves that exact SOP step.
```

## Current Verified V91 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v91-readonly-evidence-finalizer
```

Verified implementation commit:

```text
0121ea3c6815eacdddcad6c0f877d44f2dc7fe73
```

V91 finalizer artifacts:

```text
scripts/finalize_read_only_calibration_measurement_evidence.py
reports/read_only_calibration_measurement_evidence_finalizer_report.md
tests/test_read_only_calibration_measurement_template.py
```

Key result:

```text
finalizer requires exact read-only approval phrase
finalizer requires approved step id and operator
finalizer requires explicit live_hardware_accessed true|false metadata
finalizer derives evidence_status from worksheet CSV rows
finalizer rewrites metrics.yaml and metrics.json consistently
finalizer self-checks with audit-mode approved-read-only
robot motion = false
configuration writes = false
zeroing/biasing = false
force control = false
gate relaxation = false
hardware readiness = false
```

## Recommended V92 Work

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

If the user does not approve live bench interaction, refine the KSM contact
patch convention worksheet, orientation-gate decision artifact, force-source
reconciliation notes, or audit gates without touching hardware.

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
