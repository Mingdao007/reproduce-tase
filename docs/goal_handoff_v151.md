# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V151

Date: 2026-05-25

Use this after the v150 calibrated overlay force-response ladder audit.
Verify every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v150 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v151.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/readable_state_sim_seed_v147_report.md`
- `reports/calibrated_contact_overlay_collision_mask_v149_report.md`
- `reports/calibrated_overlay_force_response_v150_report.md`
- `runs/calibrated_overlay_force_response_after_v149/20260525T230000/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: v150 verifies a clean offline diagnostic
force-response ladder on the v149 collision-masked overlay. It reports
`force_response_ladder_passed = true`,
`clean_target_contact_all_rows = true`,
`positive_target_force_strictly_increasing = true`,
`force_at_1mm_N = 11.078794158483424`,
`max_force_N = 14.36943859842967`,
`diagnostic_overlay_acceptance_status = not_accepted`,
`completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.

Do not treat the v150 ladder as accepted contact calibration, setup-target
evidence, force-control validation, robustness proof, or hardware evidence.
It is only an offline diagnostic force-response probe for simulation debugging.
The exact first approved-evidence candidate remains
`phase1_mounted_stack_tcp_contact_measurement`, scoped to
`tcp_contact_measurements.csv`, and still requires explicit user confirmation
with the exact registered phrase `I approve this read-only measurement step`.
Do not move or configure the real UR10e; real hardware work is read-only
unless a separate approved SOP exists.
```

## Current V150 Evidence

Expected branch:

```text
exp/tase-ur10e-v150-overlay-force-response
```

V150 artifacts:

```text
scripts/audit_calibrated_overlay_force_response_after_v149.py
tests/test_calibrated_overlay_force_response_after_v149.py
runs/calibrated_overlay_force_response_after_v149/20260525T230000
reports/calibrated_overlay_force_response_v150_report.md
```

## Recommended V151 Work

Use the v150 ladder only as a simulation-debugging baseline. The next offline
step should connect this clean diagnostic contact response to a non-final
controller or setup-target experiment, while keeping contact/setup acceptance
and approved evidence gates separate.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Do not treat the diagnostic ladder as accepted contact-model or
  force-control validation.

## Validation

- Focused v150 tests reported `4 passed in 0.27s`.
- Full tests passed with `312 passed in 33.58s`.
- YAML anchor scan found no anchors in the v150 force-response metrics.
- Raw/heavy artifact scan found no payloads in the v150 run artifact.
- `git diff --check` passed.
