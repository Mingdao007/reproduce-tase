# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V90

Date: 2026-05-25

Use this after the v89 read-only measurement run-audit iteration. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v89 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v90.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_calibration_measurement_sop.md`
- `reports/read_only_calibration_measurement_template_report.md`
- `reports/read_only_calibration_measurement_run_audit_report.md`
- `runs/read_only_calibration_measurement/20260525T012234/metrics.yaml`
- `runs/read_only_calibration_measurement_run_audit/20260525T012835/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, not contact
calibrated, and not hardware-ready. The UR10e adapted line is diagnostic
simulation only. V87 defined a read-only measurement SOP, v88 created a
non-executed template/scaffold, and v89 added an offline audit gate that
verifies the scaffold remains non-executed and claim-safe. The v89 audit run
passed with no violations, but it is not collected hardware evidence.

Concrete v90 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v88 scaffold and v89 verifier, or refine the worksheets and
audit gates if the measurement path is still ambiguous. Do not move the real
UR10e. Do not write TCP, payload, CoG, URCap settings, OnRobot settings, RTDE
registers, zero/bias/filter settings, or run force control unless the user
separately approves that exact SOP step.
```

## Current Verified V89 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v89-readonly-run-audit
```

V89 audit artifacts:

```text
scripts/audit_read_only_calibration_measurement_run.py
runs/read_only_calibration_measurement_run_audit/20260525T012835
reports/read_only_calibration_measurement_run_audit_report.md
```

Key result:

```text
audit_passed = true
violations = []
run status = scaffold_created_not_executed
robot motion = false
configuration writes = false
zeroing/biasing = false
force control = false
gate relaxation = false
hardware readiness = false
```

## Recommended V90 Work

Start with explicit user approval before any live bench read. If a specific
read-only step is approved, instantiate a fresh run folder, collect only the
approved worksheet rows, and run:

```bash
python3 scripts/audit_read_only_calibration_measurement_run.py <run-folder>
```

If the user does not approve live bench interaction, refine the worksheets,
acceptance gates, or force-source reconciliation notes without touching
hardware.

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
