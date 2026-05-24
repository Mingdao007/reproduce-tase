# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V112

Date: 2026-05-25

Use this after the v111 weighted-profile matrix restatement. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v111 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v112.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/offline_completion_blockers_report.md`
- `reports/strict_feasibility_blockers_report.md`
- `reports/robustness_blockers_report.md`
- `reports/diagnostic_robustness_matrix_candidate_report.md`
- `reports/failed_diagnostic_robustness_experiment_matrix_report.md`
- `reports/failed_diagnostic_robustness_experiment_execution_report.md`
- `reports/weighted_plus1mm_gate_failed_cell_execution_report.md`
- `reports/plus1mm_unresolved_diagnostic_probe_report.md`
- `reports/positive_fast_timing_e2_qdot_isolation_report.md`
- `reports/positive_fast_e2_orientation_margin_report.md`
- `reports/positive_fast_weighted_full_cell_report.md`
- `reports/base_z_plus1mm_split_report.md`
- `reports/relaxed_base_z_weighted_handoff_report.md`
- `reports/weighted_priority_profile_boundary_report.md`
- `reports/weighted_profile_matrix_restatement_report.md`
- `runs/weighted_priority_profile_boundary/20260525T074100/metrics.yaml`
- `runs/weighted_profile_matrix_restatement/20260525T075040/metrics.yaml`
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
simulation only. V100-v103 execute all four v99 planned failed-cell commands;
all four remain `executed_unresolved`. V110 supports naming
`weighted_zero_angular_stage_b_diagnostic` as a diagnostic profile for the
covered v107/v109 faces. V111 restates the v98/v99 diagnostic robustness
matrix with that named profile as a non-canonical overlay: `base_z_plus1mm`
and `positive_fast_timing_0p0075` have profile overlay support, while
`positive_orientation_gate_0p119` and `weighted_plus1mm_0p119_gate` remain
gate-acceptance blocked. V111 still keeps `closed_cell_count = 0`,
`candidate_matrix_complete = false`, `accepted_as_robustness_proof = false`,
`canonical_controller_change = false`, `canonical_orientation_gate_change =
false`, and `do_not_mark_goal_complete = true`.

Concrete v112 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. With no
approval, the clean next offline candidate is a blocker-prioritization audit
over the remaining non-profile-covered rows: orientation gate acceptance,
contact calibration, strict feasibility, and hardware-readiness evidence. Do
not move the real UR10e. Do not write TCP, payload, CoG, URCap settings,
OnRobot settings, RTDE registers, zero/bias/filter settings, or run force
control unless the user separately approves that exact SOP step.
```

## Current Verified V111 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v111-weighted-profile-matrix-restatement
```

Verified implementation commit:

```text
V111_IMPLEMENTATION_COMMIT_PENDING
```

V111 weighted-profile matrix restatement artifacts:

```text
scripts/audit_weighted_profile_matrix_restatement.py
tests/test_weighted_profile_matrix_restatement.py
runs/weighted_profile_matrix_restatement/20260525T075040
reports/weighted_profile_matrix_restatement_report.md
```

Key result:

```text
restatement_supported = true
source_cell_count = 12
source_failed_cell_count = 4
profile_overlay_supported_count = 2
profile_overlay_supported_cell_ids = base_z_plus1mm, positive_fast_timing_0p0075
gate_acceptance_blocked_cell_ids = positive_orientation_gate_0p119, weighted_plus1mm_0p119_gate
closed_cell_count = 0
candidate_matrix_complete = false
accepted_as_robustness_proof = false
do_not_mark_goal_complete = true
```

## Recommended V112 Work

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

- Use v111 as the latest matrix-restatement boundary.
- Prioritize the remaining non-profile-covered blockers: orientation gate
  acceptance, contact calibration, strict feasibility, and hardware readiness.
- Keep `failed_cell_closed = false`, `canonical_controller_change = false`,
  `canonical_orientation_gate_change = false`, and `robustness_claim = false`
  unless a later audit supplies stronger evidence.

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
