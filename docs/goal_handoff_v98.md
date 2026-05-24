# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V98

Date: 2026-05-25

Use this after the v97 robustness blocker audit. Verify every claim from
repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v97 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v98.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/offline_completion_blockers_report.md`
- `runs/offline_completion_blockers/20260525T020734/metrics.yaml`
- `reports/strict_feasibility_blockers_report.md`
- `runs/strict_feasibility_blockers/20260525T051640/metrics.yaml`
- `reports/robustness_blockers_report.md`
- `runs/robustness_blockers/20260525T052457/metrics.yaml`
- `reports/read_only_calibration_measurement_sop.md`
- `reports/read_only_calibration_measurement_orientation_acceptance_boundary_report.md`
- `reports/orientation_gate_acceptance_review_template_report.md`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, not contact
calibrated, and not hardware-ready. The UR10e adapted line is diagnostic
simulation only. V95 classifies strict paper-equivalent full staged
feasibility and robustness as non-final offline-actionable items, while
approved read-only calibration evidence, calibrated contact geometry,
orientation-gate acceptance, and hardware readiness remain blocked on explicit
approval/evidence. V96 confirms strict setup remains incomplete: strict full
staged feasibility is `0 / 4`, three-phase setup terminal state is `0 / 10`,
and three-phase trajectory feasibility is `8 / 10`. V97 confirms robustness
also remains incomplete: baseline diagnostic stitched sensitivity is `4 / 9`,
positive stitched sensitivity is `37 / 40`, and recovered qdot012/positive
faces remain diagnostic non-final evidence rather than a robustness proof.

Concrete v98 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. Offline
candidates are: define and stress a single accepted diagnostic robustness
matrix, search for a strict setup terminal policy that meets tangential,
orientation, force, and qdot gates simultaneously, or refine paper-platform
parity without upgrading claim scope. Do not move the real UR10e. Do not write
TCP, payload, CoG, URCap settings, OnRobot settings, RTDE registers,
zero/bias/filter settings, or run force control unless the user separately
approves that exact SOP step.
```

## Current Verified V97 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v97-robustness-blockers
```

V97 robustness blocker artifacts:

```text
scripts/audit_robustness_blockers.py
tests/test_robustness_blockers.py
runs/robustness_blockers/20260525T052457
reports/robustness_blockers_report.md
```

Key result:

```text
overall_goal_complete = false
robustness_complete = false
baseline_stitched_pass_count = 4 / 9
positive_matrix_pass_count = 37 / 40
primary_blocker = accepted_model_robustness_not_closed
do_not_mark_goal_complete = true
```

## Recommended V98 Work

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

If no live read-only step is approved, use the v95-v97 audits to choose
non-final offline work only. Do not claim completion from offline work unless
every completion blocker in the v95 audit is actually closed by concrete
evidence.

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
