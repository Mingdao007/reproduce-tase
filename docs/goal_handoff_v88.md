# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V88

Date: 2026-05-25

Use this after the v87 read-only calibration measurement SOP. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v87 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v88.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_calibration_measurement_sop.md`
- `reports/measured_geometry_readiness_report.md`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, not contact
calibrated, and not hardware-ready. The UR10e adapted line is diagnostic
simulation only. V87 created a read-only measurement/SOP artifact for the
missing mounted-stack TCP/contact point, KSM contact patch convention,
robot-base-frame plane normal, force-source/frame reconciliation, and
orientation-gate semantics evidence. The SOP has not been executed and does
not authorize motion, writes, zeroing, force control, gate relaxation, or
hardware claims.

Concrete v88 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP, or refine the SOP if the measurement path is still ambiguous. Do not
move the real UR10e. Do not write TCP, payload, CoG, URCap settings, OnRobot
settings, RTDE registers, zero/bias/filter settings, or run force control
unless the user separately approves that exact SOP step.
```

## Current Verified V87 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v87-readonly-measurement-sop
```

V87 SOP artifact:

```text
reports/read_only_calibration_measurement_sop.md
```

Key result:

```text
SOP execution = false
robot motion = false
configuration writes = false
gate relaxation = false
hardware readiness = false
```

## Recommended V88 Work

Start with an operator confirmation gate before any live bench reads. If the
user approves read-only checks, collect only the Phase 0 and safe static facts
from the SOP. If the user does not approve live bench interaction, refine the
SOP or prepare worksheets/templates.

Possible read-only deliverables:

- timestamped measurement run folder under `runs/read_only_calibration_measurement/`
- `measurement_plan.md`
- `operator_checklist.md`
- empty or template CSV files for TCP/contact, plane normal, and force-source
  comparison
- `metrics.yaml` stating which gates remain unexecuted
- report update that keeps all hardware claims false

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
