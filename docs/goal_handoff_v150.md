# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V150

Date: 2026-05-25

Use this after the v149 diagnostic contact overlay collision-mask audit.
Verify every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v149 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v150.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/readable_state_sim_seed_v147_report.md`
- `reports/calibrated_contact_overlay_v148_report.md`
- `reports/calibrated_contact_overlay_collision_mask_v149_report.md`
- `runs/calibrated_contact_overlay_after_v147/20260525T223000/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: v149 fixes the calibrated diagnostic
contact overlay so the diagnostic plane is reserved for the named plane/tip
contact pair. It reports `target_contact_pair_count_at_seed = 1`,
`non_target_contact_count_at_seed = 0`,
`activation_probe_target_contact_pair_count = 1`,
`activation_probe_non_target_contact_count = 0`,
`activation_probe_target_normal_force_N = 11.078794158483424`,
`simulation_can_start_from_diagnostic_overlay = true`,
`diagnostic_overlay_acceptance_status = not_accepted`,
`completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.

Do not treat the v149 overlay plane, tip radius, local offset, contact pair,
or activation force as accepted contact calibration or setup-target evidence.
It is only an offline diagnostic scaffold for the next simulation experiment.
The exact first approved-evidence candidate remains
`phase1_mounted_stack_tcp_contact_measurement`, scoped to
`tcp_contact_measurements.csv`, and still requires explicit user confirmation
with the exact registered phrase `I approve this read-only measurement step`.
Do not move or configure the real UR10e; real hardware work is read-only
unless a separate approved SOP exists.
```

## Current V149 Evidence

Expected branch:

```text
exp/tase-ur10e-v149-overlay-collision-mask
```

V149 artifacts:

```text
scripts/audit_calibrated_contact_overlay_after_v147.py
tests/test_calibrated_contact_overlay_after_v147.py
assets/mjcf/ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.xml
runs/calibrated_contact_overlay_after_v147/20260525T223000
reports/calibrated_contact_overlay_collision_mask_v149_report.md
```

## Recommended V150 Work

Run the next offline diagnostic force/contact simulation against
`configs/mujoco_ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.yaml`.
Keep it explicitly non-final unless contact/setup-target acceptance and
approved evidence gates are separately satisfied.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Do not treat the diagnostic overlay or activation probe as accepted
  contact-model or force-control validation.

## Validation

- Focused v149 tests reported `4 passed in 0.28s`.
- Full tests passed with `308 passed in 33.10s`.
- YAML anchor scan found no anchors in the v149 overlay metrics/config YAML
  files.
- Raw/heavy artifact scan found no payloads in the v149 overlay artifacts.
- `git diff --check` passed.
