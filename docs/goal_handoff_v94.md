# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V94

Date: 2026-05-25

Use this after the v93 orientation-gate acceptance-boundary refinement. Verify
every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v93 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v94.md`
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
- `reports/read_only_calibration_measurement_orientation_acceptance_boundary_report.md`
- `runs/read_only_calibration_measurement/20260525T015400/metrics.yaml`
- `runs/read_only_calibration_measurement_run_audit/20260525T015401/metrics.yaml`

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
offline finalizer for approved read-only evidence runs, v92 added explicit KSM
contact-patch and orientation-gate-semantics worksheet coverage, and v93 made
orientation-gate acceptance a separate not-accepted boundary in metrics,
finalizer output, and audit checks. All these steps still forbid robot motion,
configuration writes, zeroing/biasing, force control, contact-model updates,
gate relaxation, hardware claims, and hardware readiness.

Concrete v94 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 scaffold, v91 finalizer, and v90/v93 verifier, or refine
a separate non-default gate-acceptance review template offline. Do not move
the real UR10e. Do not write TCP, payload, CoG, URCap settings, OnRobot
settings, RTDE registers, zero/bias/filter settings, or run force control
unless the user separately approves that exact SOP step.
```

## Current Verified V93 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v93-orientation-acceptance-boundary
```

Verified implementation commit:

```text
b8246d247734c5df5a3d0c3f056d4ac60b25729c
```

V93 orientation-boundary artifacts:

```text
templates/read_only_calibration_measurement/metrics.yaml
templates/read_only_calibration_measurement/orientation_gate_decision.md
scripts/audit_read_only_calibration_measurement_run.py
scripts/finalize_read_only_calibration_measurement_evidence.py
runs/read_only_calibration_measurement/20260525T015400
runs/read_only_calibration_measurement_run_audit/20260525T015401
reports/read_only_calibration_measurement_orientation_acceptance_boundary_report.md
```

Key result:

```text
orientation_gate_acceptance.decision = not_accepted
orientation_gate_acceptance.evidence_only = true
accepted gate fields = null
orientation worksheet rows can be collected read-only
collected orientation rows do not accept a gate
scaffold audit passed with violations = []
robot motion = false
configuration writes = false
zeroing/biasing = false
force control = false
gate relaxation = false
hardware readiness = false
```

## Recommended V94 Work

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

If the user does not approve live bench interaction, keep work offline and
define a separate gate-acceptance review template that cannot be invoked by the
read-only evidence finalizer.

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
