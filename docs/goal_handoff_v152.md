# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V152

Date: 2026-05-25

Use this after the v151 overlay target-force coverage audit. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v151 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v152.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/calibrated_overlay_force_response_v150_report.md`
- `reports/overlay_target_force_coverage_v151_report.md`
- `runs/overlay_target_force_coverage_after_v150/20260525T231000/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: v151 confirms the unaccepted diagnostic
overlay cannot cover a `5.0 N` static target by penetration alone. It reports
`minimum_positive_force_N = 7.136494172695263`,
`best_force_N = 7.136494172695263`,
`best_abs_error_N = 2.1364941726952633`,
`target_force_reachable_in_scan = false`,
`coverage_gap_identified = true`,
`diagnostic_overlay_acceptance_status = not_accepted`,
`completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.

Do not treat the v151 coverage gap as accepted contact calibration,
setup-target evidence, force-control validation, robustness proof, or hardware
evidence. The next offline step should be a non-final contact-parameter or
target-definition diagnostic. The exact first approved-evidence candidate
remains `phase1_mounted_stack_tcp_contact_measurement`, scoped to
`tcp_contact_measurements.csv`, and still requires explicit user confirmation
with the exact registered phrase `I approve this read-only measurement step`.
Do not move or configure the real UR10e; real hardware work is read-only
unless a separate approved SOP exists.
```

## Current V151 Evidence

Expected branch:

```text
exp/tase-ur10e-v151-overlay-target-force-coverage
```

V151 artifacts:

```text
scripts/audit_overlay_target_force_coverage_after_v150.py
tests/test_overlay_target_force_coverage_after_v150.py
runs/overlay_target_force_coverage_after_v150/20260525T231000
reports/overlay_target_force_coverage_v151_report.md
```

## Recommended V152 Work

Run a non-final contact-parameter diagnostic to see whether a simulation-only
contact setting can cover the `5.0 N` target while preserving clean target-pair
contact. Do not promote any tuned parameter to accepted evidence without the
contact/setup-target review path.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Do not treat target-force coverage diagnostics as accepted contact-model or
  force-control validation.
