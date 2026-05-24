# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V96

Date: 2026-05-25

Use this after the v95 offline completion-blockers audit. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v95 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v96.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/offline_completion_blockers_report.md`
- `runs/offline_completion_blockers/20260525T020734/metrics.yaml`
- `reports/read_only_calibration_measurement_sop.md`
- `reports/read_only_calibration_measurement_orientation_acceptance_boundary_report.md`
- `reports/orientation_gate_acceptance_review_template_report.md`
- `runs/read_only_calibration_measurement/20260525T015400/metrics.yaml`
- `runs/orientation_gate_acceptance_review/20260525T020054/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, not contact
calibrated, and not hardware-ready. The UR10e adapted line is diagnostic
simulation only. V95 adds `scripts/audit_offline_completion_blockers.py` and
`runs/offline_completion_blockers/20260525T020734`, which classify the
remaining blockers. The only achieved completion item is the scoped slowed
UR10e adapted relaxed simulation claim. Strict paper-equivalent full staged
feasibility and robustness are offline-actionable but non-final. Approved
read-only calibration evidence, calibrated contact geometry, orientation-gate
acceptance, and hardware readiness remain blocked on explicit read-only
approval/evidence or separate authorization.

Concrete v96 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline simulation/paper-platform
work that the v95 blocker audit marks as non-final offline-actionable. Do not
move the real UR10e. Do not write TCP, payload, CoG, URCap settings, OnRobot
settings, RTDE registers, zero/bias/filter settings, or run force control
unless the user separately approves that exact SOP step.
```

## Current Verified V95 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v95-offline-completion-blockers
```

V95 offline blocker artifacts:

```text
scripts/audit_offline_completion_blockers.py
runs/offline_completion_blockers/20260525T020734
reports/offline_completion_blockers_report.md
tests/test_offline_completion_blockers.py
```

Key result:

```text
overall_goal_complete = false
completion_blocked = true
do_not_mark_goal_complete = true
offline-actionable non-final items =
  strict_paper_equivalent_full_staged_feasibility
  robustness_to_contact_model_perturbations
live/approval blocked items =
  approved_read_only_calibration_evidence
  calibrated_contact_geometry
  orientation_gate_acceptance
  hardware_readiness
```

## Recommended V96 Work

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

If no live read-only step is approved, use the v95 audit to choose non-final
offline simulation or paper-platform work only. Do not claim completion from
offline work unless every completion blocker in the v95 audit is actually
closed by concrete evidence.

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
