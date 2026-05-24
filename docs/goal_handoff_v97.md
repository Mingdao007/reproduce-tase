# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V97

Date: 2026-05-25

Use this after the v96 strict-feasibility blocker audit. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v96 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v97.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/offline_completion_blockers_report.md`
- `runs/offline_completion_blockers/20260525T020734/metrics.yaml`
- `reports/strict_feasibility_blockers_report.md`
- `runs/strict_feasibility_blockers/20260525T051640/metrics.yaml`
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
approval/evidence. V96 audits the strict-feasibility item and confirms that
strict setup is still incomplete: posture-regularized rows have trajectory
feasibility `4 / 4` and orientation within the strict setup gate, but strict
full staged feasibility remains `0 / 4`; three-phase settle rows have setup
terminal state `0 / 10`, trajectory feasibility `8 / 10`, and full staged
feasibility `0 / 10`.

Concrete v97 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. The
offline candidates are: search for a strict setup terminal policy that meets
tangential, orientation, force, and qdot gates simultaneously, or work on the
separate robustness blocker from the v95 audit. Do not move the real UR10e. Do
not write TCP, payload, CoG, URCap settings, OnRobot settings, RTDE registers,
zero/bias/filter settings, or run force control unless the user separately
approves that exact SOP step.
```

## Current Verified V96 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v96-strict-feasibility-blockers
```

V96 strict-feasibility blocker artifacts:

```text
scripts/audit_strict_feasibility_blockers.py
tests/test_strict_feasibility_blockers.py
runs/strict_feasibility_blockers/20260525T051640
reports/strict_feasibility_blockers_report.md
```

Key result:

```text
overall_goal_complete = false
strict_feasibility_complete = false
strict_setup_gate_complete = false
strict_full_staged_feasibility_pass_count = 0 / 4
three_phase_setup_terminal_state_pass_count = 0 / 10
three_phase_trajectory_feasibility_pass_count = 8 / 10
primary_blocker = strict_setup_terminal_tradeoff
do_not_mark_goal_complete = true
```

## Recommended V97 Work

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

If no live read-only step is approved, use the v95 and v96 audits to choose
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
