# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V111

Date: 2026-05-25

Use this after the v110 weighted-priority profile-boundary audit. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v110 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v111.md`
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
- `runs/positive_fast_weighted_full_cell/20260525T064719/metrics.yaml`
- `runs/relaxed_base_z_weighted_handoff/20260525T073012/metrics.yaml`
- `runs/weighted_priority_profile_boundary/20260525T074100/metrics.yaml`
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
all four remain `executed_unresolved`. V104 classifies the remaining
`+1.0 mm` signatures. V105 shows qdot-limit increases alone do not recover the
fast E2 row at `paper_time_scale = 0.0075`. V106 shows weighted priority
clears the isolated E2 row at fixed `qdot_limit = 0.15 rad/s` and the fixed
`0.12 rad` orientation gate. V107 reruns the exact `+1.0 mm` full E1-E4
fast-timing face: the linear-primary baseline still fails E2, while both
weighted rows pass `4 / 4`; this remains diagnostic because `weighted` is not
canonical. V108 splits `base_z_plus1mm`. V109 shows weighted priority recovers
the relaxed `base_z_plus1mm` Stage B handoff at the tested durations. V110
supports naming `weighted_zero_angular_stage_b_diagnostic` as a diagnostic
profile for the covered v107/v109 faces, while keeping
`canonical_controller_change = false`, `canonical_orientation_gate_change =
false`, `failed_cell_closed = false`, and `robustness_claim = false`.

Concrete v111 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. With no
approval, the clean next offline candidate is to audit whether the v98/v99
diagnostic robustness matrix can be restated with the named weighted
diagnostic profile while preserving canonical controller/gate changes,
failed-cell closure, and robustness claims as false. Do not move the real
UR10e. Do not write TCP, payload, CoG, URCap settings, OnRobot settings, RTDE
registers, zero/bias/filter settings, or run force control unless the user
separately approves that exact SOP step.
```

## Current Verified V110 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v110-weighted-priority-profile-boundary
```

Verified implementation commit:

```text
f48240c72188e8d4fd4e18bd69fe37c38e1e1d90
```

V110 weighted-priority profile-boundary artifacts:

```text
scripts/audit_weighted_priority_profile_boundary.py
tests/test_weighted_priority_profile_boundary.py
runs/weighted_priority_profile_boundary/20260525T074100
reports/weighted_priority_profile_boundary_report.md
```

Key result:

```text
profile_name = weighted_zero_angular_stage_b_diagnostic
diagnostic_profile_naming_supported = true
evidence_face_count = 2
weighted_all_faces_recovered = true
baseline_failure_reproduced_all_faces = true
can_name_diagnostic_profile = true
canonical_controller_change = false
canonical_orientation_gate_change = false
failed_cell_closed = false
robustness_claim = false
hardware_readiness = false
```

## Recommended V111 Work

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

- Use v110 as the named diagnostic-profile boundary.
- Audit whether the v98/v99 diagnostic robustness matrix can be restated with
  the profile as a non-canonical candidate.
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
