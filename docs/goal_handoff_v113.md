# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V113

Date: 2026-05-25

Use this after the v112 remaining-blocker prioritization. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v112 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v113.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/offline_completion_blockers_report.md`
- `reports/strict_feasibility_blockers_report.md`
- `reports/robustness_blockers_report.md`
- `reports/weighted_profile_matrix_restatement_report.md`
- `reports/remaining_blocker_prioritization_report.md`
- `runs/weighted_profile_matrix_restatement/20260525T075040/metrics.yaml`
- `runs/remaining_blocker_prioritization/20260525T072557/metrics.yaml`
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
simulation only. V111 restates the v98/v99 diagnostic robustness matrix with
`weighted_zero_angular_stage_b_diagnostic` as a non-canonical overlay:
`base_z_plus1mm` and `positive_fast_timing_0p0075` have profile overlay
support, while `positive_orientation_gate_0p119` and
`weighted_plus1mm_0p119_gate` remain gate-acceptance blocked. V112 ranks the
remaining blockers: top priority is `approved_read_only_calibration_evidence`,
remaining blocker count is `6`, live/approval-blocked count is `4`,
offline-actionable non-final count is `2`, profile-overlay supported cells are
`2`, gate-acceptance blocked cells are `2`, closed cells remain `0`, candidate
matrix complete is `false`, accepted-as-robustness-proof is `false`, and
`do_not_mark_goal_complete = true`.

Concrete v113 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. With no
approval, the clean next offline candidate is a strict-feasibility policy probe,
because v112 identifies strict feasibility as the highest-priority blocker
that can advance offline without approval. Do not move the real UR10e. Do not
write TCP, payload, CoG, URCap settings, OnRobot settings, RTDE registers,
zero/bias/filter settings, or run force control unless the user separately
approves that exact SOP step.
```

## Current Verified V112 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v112-remaining-blocker-prioritization
```

Verified implementation commit:

```text
8ed1b881fae6d27e815feecf0b59724f64cb2a9a
```

V112 remaining-blocker prioritization artifacts:

```text
scripts/audit_remaining_blocker_prioritization.py
tests/test_remaining_blocker_prioritization.py
runs/remaining_blocker_prioritization/20260525T072557
reports/remaining_blocker_prioritization_report.md
```

Key result:

```text
overall_goal_complete = false
completion_blocked = true
top_priority_blocker_id = approved_read_only_calibration_evidence
remaining_blocker_count = 6
live_or_approval_blocked_count = 4
offline_actionable_nonfinal_count = 2
profile_overlay_supported_cell_count = 2
gate_acceptance_blocked_cell_count = 2
closed_cell_count = 0
candidate_matrix_complete = false
accepted_as_robustness_proof = false
do_not_mark_goal_complete = true
```

## Recommended V113 Work

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

If no live read-only step is approved, continue only non-final offline probes:

- Use v112 as the latest blocker prioritization boundary.
- Treat `approved_read_only_calibration_evidence` as the top overall blocker.
- Treat strict feasibility as the highest-priority offline-actionable blocker.
- Keep gate acceptance, contact calibration, hardware readiness, failed-cell
  closure, canonical controller changes, and robustness claims false unless a
  later audit supplies stronger evidence.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Do not use OnRobot direct TCP DAQ as control truth until the force-source
  discrepancy is resolved.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user.
