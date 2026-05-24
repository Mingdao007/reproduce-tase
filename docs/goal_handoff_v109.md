# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V109

Date: 2026-05-25

Use this after the v108 `base_z_plus1mm` split audit. Verify every claim from
repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v108 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v109.md`
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
- `runs/positive_fast_weighted_full_cell/20260525T064719/metrics.yaml`
- `runs/base_z_plus1mm_split/20260525T071440/metrics.yaml`
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
Stage A/path but not stitched Stage B. V108 still does not close the original
failed cell or accept a replacement gate.

Concrete v109 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. With no
approval, clean offline candidates are a weighted-priority acceptance-boundary
audit before treating weighted priority as a named diagnostic profile, or a
targeted relaxed `base_z_plus1mm` Stage B handoff timing/qdot audit that keeps
the relaxed gate non-canonical. Do not move the real UR10e. Do not write TCP,
payload, CoG, URCap settings, OnRobot settings, RTDE registers,
zero/bias/filter settings, or run force control unless the user separately
approves that exact SOP step.
```

## Current Verified V108 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v108-base-z-plus1mm-split
```

Verified implementation commit:

```text
987e360d9244bf8c98ce549c21c7787ab163868a
```

V108 split artifacts:

```text
scripts/audit_base_z_plus1mm_split.py
tests/test_base_z_plus1mm_split.py
runs/base_z_plus1mm_split/20260525T071440
reports/base_z_plus1mm_split_report.md
```

Key result:

```text
exact_planned_cell_status = executed_unresolved
exact_closure_passed = false
broader_start_search_passed = true
terminal_force_xy_contact_passed = true
terminal_diagnostic_passed = false
terminal_orientation_error_rad = 0.11948560786548146
exact_orientation_gate_rad = 0.08
relaxed_gate_rad = 0.12
relaxed_terminal_passed = true
relaxed_path_passed = true
relaxed_stitched_recovered = false
failed_cell_closed = false
```

## Recommended V109 Work

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

- For `positive_fast_timing_0p0075`, V107 shows weighted priority recovers the
  full E1-E4 face, but canonical adoption is not accepted. A next audit can
  define the acceptance boundary for promoting weighted priority into a named
  diagnostic controller profile without claiming robustness or hardware
  readiness.
- For `base_z_plus1mm`, V108 shows start contact and Stage A/path are not the
  remaining blocker under the run-local `0.12 rad` gate. A next audit can
  target Stage B handoff timing/qdot margin while keeping the original v99
  cell unresolved and the relaxed gate non-canonical.

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
