# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V89

Date: 2026-05-25

Use this after the v88 read-only measurement template/scaffold iteration.
Verify every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v88 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v89.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_calibration_measurement_sop.md`
- `reports/read_only_calibration_measurement_template_report.md`
- `templates/read_only_calibration_measurement/README.md`
- `runs/read_only_calibration_measurement/20260525T012234/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, not contact
calibrated, and not hardware-ready. The UR10e adapted line is diagnostic
simulation only. V87 defined a read-only measurement SOP for the missing
mounted-stack TCP/contact point, KSM contact patch convention,
robot-base-frame plane normal, force-source/frame reconciliation, and
orientation-gate semantics evidence. V88 created a non-executed template and
scaffold command for future evidence capture. The template run has status
`scaffold_created_not_executed` and all hardware, calibration,
gate-relaxation, and hardware-readiness flags remain false.

Concrete v89 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v88 scaffold, or refine the worksheets if the measurement
path is still ambiguous. Do not move the real UR10e. Do not write TCP, payload,
CoG, URCap settings, OnRobot settings, RTDE registers, zero/bias/filter
settings, or run force control unless the user separately approves that exact
SOP step.
```

## Current Verified V88 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v88-readonly-measurement-templates
```

V87 SOP artifact:

```text
reports/read_only_calibration_measurement_sop.md
```

V88 template/scaffold artifacts:

```text
templates/read_only_calibration_measurement/
scripts/create_read_only_calibration_measurement_run.py
runs/read_only_calibration_measurement/20260525T012234
reports/read_only_calibration_measurement_template_report.md
tests/test_read_only_calibration_measurement_template.py
```

Key result:

```text
template run status = scaffold_created_not_executed
SOP execution = false
robot motion = false
configuration writes = false
zeroing/biasing = false
force control = false
gate relaxation = false
hardware readiness = false
```

## Recommended V89 Work

Start with an operator confirmation gate before any live bench reads. If the
user approves a specific read-only check, instantiate a fresh run folder with:

```bash
python3 scripts/create_read_only_calibration_measurement_run.py
```

Then fill only the worksheets corresponding to the approved read-only step. If
the user does not approve live bench interaction, refine the worksheets,
acceptance gates, or force-source reconciliation notes without touching
hardware.

Possible read-only deliverables after approval:

- timestamped measurement run folder under `runs/read_only_calibration_measurement/`
- completed subset of `measurement_plan.md`
- completed `operator_checklist.md`
- populated CSV rows for approved TCP/contact, plane-normal, or force-source
  observations
- updated `metrics.yaml` and `summary.md` keeping unsupported claims false
- report update that distinguishes collected facts from unresolved gates

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
