# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V95

Date: 2026-05-25

Use this after the v94 orientation gate-acceptance review template. Verify
every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v94 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v95.md`
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
- `reports/orientation_gate_acceptance_review_template_report.md`
- `runs/read_only_calibration_measurement/20260525T015400/metrics.yaml`
- `runs/read_only_calibration_measurement_run_audit/20260525T015401/metrics.yaml`
- `runs/orientation_gate_acceptance_review/20260525T020054/metrics.yaml`
- `runs/orientation_gate_acceptance_review_audit/20260525T020055/metrics.yaml`

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
contact-patch and orientation-gate-semantics worksheet coverage, v93 made
orientation-gate acceptance a separate not-accepted boundary in metrics,
finalizer output, and audit checks, and v94 added a separate non-default
orientation gate-acceptance review scaffold/audit path. All these steps still
forbid robot motion, configuration writes, zeroing/biasing, force control,
contact-model updates, gate relaxation, hardware claims, and hardware
readiness.

Concrete v95 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or keep work offline and audit whether any remaining completion requirement can
be advanced without live bench access. Do not move the real UR10e. Do not
write TCP, payload, CoG, URCap settings, OnRobot settings, RTDE registers,
zero/bias/filter settings, or run force control unless the user separately
approves that exact SOP step.
```

## Current Verified V94 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v94-gate-acceptance-review-template
```

V94 orientation gate-acceptance review artifacts:

```text
templates/orientation_gate_acceptance_review/
scripts/create_orientation_gate_acceptance_review.py
scripts/audit_orientation_gate_acceptance_review.py
runs/orientation_gate_acceptance_review/20260525T020054
runs/orientation_gate_acceptance_review_audit/20260525T020055
reports/orientation_gate_acceptance_review_template_report.md
```

Key result:

```text
review_status = review_scaffold_not_executed
source_read_only_run = null
approved_read_only_audit_passed = false
orientation_gate_acceptance.decision = not_accepted
orientation_gate_acceptance.review_only = true
accepted gate fields = null
gate relaxation = false
hardware readiness = false
scaffold audit passed with violations = []
```

## Recommended V95 Work

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

The gate-acceptance review scaffold should remain unused until a passed
approved-read-only evidence run exists and a separate review is explicitly
authorized.

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
