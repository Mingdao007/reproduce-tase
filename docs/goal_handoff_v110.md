# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V110

Date: 2026-05-25

Use this after the v109 relaxed `base_z_plus1mm` weighted handoff probe.
Verify every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v109 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v110.md`
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
- `runs/positive_fast_weighted_full_cell/20260525T064719/metrics.yaml`
- `runs/base_z_plus1mm_split/20260525T071440/metrics.yaml`
- `runs/relaxed_base_z_weighted_handoff/20260525T073012/metrics.yaml`
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
canonical. V108 splits `base_z_plus1mm`: broader seeds recover start contact,
terminal force/x-y/contact passes, terminal/path are blocked by the current
`0.08 rad` orientation gate, and the run-local `0.12 rad` gate recovers
Stage A/path but not stitched Stage B. V109 targets that relaxed handoff
blocker: the linear-primary baseline still fails E2, while both weighted rows
pass `4 / 4` at Stage A durations `15.0 s` and `16.0 s`. V109 still does not
close the original failed cell, accept `0.12 rad` as canonical, or accept
weighted priority as canonical.

Concrete v110 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. With no
approval, the clean next offline candidate is a weighted-priority
acceptance-boundary audit that uses v107 and v109 to decide whether `weighted`
can be named as a diagnostic controller profile without becoming canonical or
closing any original v99 failed cell. Do not move the real UR10e. Do not write
TCP, payload, CoG, URCap settings, OnRobot settings, RTDE registers,
zero/bias/filter settings, or run force control unless the user separately
approves that exact SOP step.
```

## Current Verified V109 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v109-relaxed-base-z-weighted-handoff
```

Verified implementation commit:

```text
V109_IMPLEMENTATION_COMMIT_PENDING
```

V109 relaxed base-z weighted handoff artifacts:

```text
scripts/audit_relaxed_base_z_weighted_handoff.py
tests/test_relaxed_base_z_weighted_handoff.py
runs/relaxed_base_z_weighted_handoff/20260525T073012
reports/relaxed_base_z_weighted_handoff_report.md
```

Key result:

```text
case_count = 6
passing_case_count = 4
baseline_failing_count = 2
weighted_passing_count = 4
weighted_candidate_recovered_all_durations = true
all_weighted_cases_recovered = true
original_failed_cell_closed = false
canonical_orientation_gate_change_accepted = false
canonical_controller_change_accepted = false
```

## Recommended V110 Work

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

- V107 shows weighted priority recovers the full E1-E4 fast-timing face under
  the run-local `0.12 rad` gate.
- V109 shows weighted priority recovers the relaxed `base_z_plus1mm` Stage B
  handoff at the tested Stage A durations.
- A next audit can define a named diagnostic `weighted` profile boundary while
  explicitly preserving `canonical_controller_change = false`,
  `canonical_orientation_gate_change = false`, `failed_cell_closed = false`,
  and `robustness_claim = false`.

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
