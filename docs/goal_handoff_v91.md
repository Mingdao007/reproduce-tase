# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V91

Date: 2026-05-25

Use this after the v90 read-only audit-mode refinement. Verify every claim from
repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v90 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v91.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_calibration_measurement_sop.md`
- `reports/read_only_calibration_measurement_template_report.md`
- `reports/read_only_calibration_measurement_run_audit_report.md`
- `reports/read_only_calibration_measurement_audit_modes_report.md`
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
non-executed template/scaffold, v89 added an offline audit gate, and v90 split
the audit gate into `scaffold` and `approved-read-only` modes. The new
approved-read-only mode still forbids robot motion, configuration writes,
zeroing/biasing, force control, contact-model updates, gate relaxation,
hardware claims, and hardware readiness.

Concrete v91 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v88 scaffold and v90 verifier, or refine the worksheets and
audit gates if the measurement path is still ambiguous. Do not move the real
UR10e. Do not write TCP, payload, CoG, URCap settings, OnRobot settings, RTDE
registers, zero/bias/filter settings, or run force control unless the user
separately approves that exact SOP step.
```

## Current Verified V90 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v90-readonly-evidence-audit-modes
```

V90 audit-mode artifacts:

```text
scripts/audit_read_only_calibration_measurement_run.py
runs/read_only_calibration_measurement_run_audit/20260525T013421
reports/read_only_calibration_measurement_audit_modes_report.md
```

Key result:

```text
audit_mode = scaffold
audit_passed = true
violations = []
approved-read-only mode exists and is tested
robot motion = false
configuration writes = false
zeroing/biasing = false
force control = false
gate relaxation = false
hardware readiness = false
```

## Recommended V91 Work

Start with explicit user approval before any live bench read. If a specific
read-only step is approved, instantiate a fresh run folder, collect only the
approved worksheet rows, set `status = approved_read_only_evidence`, and run:

```bash
python3 scripts/audit_read_only_calibration_measurement_run.py <run-folder> --audit-mode approved-read-only
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
