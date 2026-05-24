# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V99

Date: 2026-05-25

Use this after the v98 diagnostic robustness matrix candidate. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v98 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v99.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/offline_completion_blockers_report.md`
- `reports/strict_feasibility_blockers_report.md`
- `reports/robustness_blockers_report.md`
- `reports/diagnostic_robustness_matrix_candidate_report.md`
- `runs/diagnostic_robustness_matrix_candidate/20260525T053101/metrics.yaml`
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
approval/evidence. V96 confirms strict setup remains incomplete. V97 confirms
robustness remains incomplete. V98 defines a single diagnostic robustness
matrix candidate with 12 cells: 7 diagnostic passes, 1 non-final diagnostic
recovery, and 4 failed cells (`base_z_plus1mm`,
`positive_fast_timing_0p0075`, `positive_orientation_gate_0p119`, and
`weighted_plus1mm_0p119_gate`). The v75 qdot012 positive matrix remains
`passed_diagnostic_nonfinal`, not an accepted robustness proof.

Concrete v99 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. The
clearest offline candidate is to convert the four failed v98 matrix cells into
an executable experiment matrix or continue strict setup policy search without
upgrading claim scope. Do not move the real UR10e. Do not write TCP, payload,
CoG, URCap settings, OnRobot settings, RTDE registers, zero/bias/filter
settings, or run force control unless the user separately approves that exact
SOP step.
```

## Current Verified V98 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v98-diagnostic-robustness-matrix
```

V98 diagnostic robustness matrix artifacts:

```text
scripts/audit_diagnostic_robustness_matrix_candidate.py
tests/test_diagnostic_robustness_matrix_candidate.py
runs/diagnostic_robustness_matrix_candidate/20260525T053101
reports/diagnostic_robustness_matrix_candidate_report.md
```

Key result:

```text
overall_goal_complete = false
candidate_matrix_complete = false
accepted_as_robustness_proof = false
cell_count = 12
failed_cell_count = 4
do_not_mark_goal_complete = true
```

## Recommended V99 Work

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

If no live read-only step is approved, use the v95-v98 audits to choose
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
