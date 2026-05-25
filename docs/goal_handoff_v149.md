# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V149

Date: 2026-05-25

Use this after the v148 calibrated diagnostic contact overlay audit. Verify
every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v148 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v149.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/readable_state_sim_seed_v147_report.md`
- `reports/calibrated_contact_overlay_v148_report.md`
- `runs/calibrated_mjcf_replay_after_v147/20260525T212000/metrics.yaml`
- `runs/calibrated_contact_overlay_after_v147/20260525T220000/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: v147 backs up the readable UR10e state
and creates calibrated kinematic seed infrastructure; v148 adds an unaccepted
diagnostic contact overlay so offline simulation can start from the backed-up
pose with a deterministic tilted-plane contact geometry. The overlay config is
`configs/mujoco_ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.yaml`
and the overlay MJCF is
`assets/mjcf/ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.xml`.

V148 reports `simulation_can_start_from_diagnostic_overlay = true`,
`current_tcp_site_on_diagnostic_plane = true`,
`contact_tip_surface_tangent_to_plane = true`,
`diagnostic_overlay_acceptance_status = not_accepted`,
`completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.

Do not treat the v148 overlay plane, tip radius, local offset, or start-contact
geometry as accepted contact calibration or setup-target evidence. It is only
an offline diagnostic scaffold for the next simulation experiment. The exact
first approved-evidence candidate remains
`phase1_mounted_stack_tcp_contact_measurement`, scoped to
`tcp_contact_measurements.csv`, and still requires explicit user confirmation
with the exact registered phrase `I approve this read-only measurement step`.
Do not move or configure the real UR10e; real hardware work is read-only
unless a separate approved SOP exists.
```

## Current V148 Evidence

Expected branch:

```text
exp/tase-ur10e-v148-calibrated-contact-overlay
```

V148 artifacts:

```text
scripts/audit_calibrated_contact_overlay_after_v147.py
tests/test_calibrated_contact_overlay_after_v147.py
assets/mjcf/ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.xml
configs/mujoco_ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.yaml
runs/calibrated_contact_overlay_after_v147/20260525T220000
reports/calibrated_contact_overlay_v148_report.md
```

Key result:

```text
audit_passed = true
simulation_can_start_from_diagnostic_overlay = true
current_tcp_site_on_diagnostic_plane = true
contact_tip_surface_tangent_to_plane = true
diagnostic_overlay_acceptance_status = not_accepted
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

## Recommended V149 Work

Run the next offline diagnostic simulation against
`configs/mujoco_ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.yaml`.
Keep it explicitly non-final unless contact/setup-target acceptance and
approved evidence gates are separately satisfied.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Do not treat the diagnostic overlay as accepted contact-model or
  force-control validation.

## Validation

- Focused v148 tests reported `4 passed in 0.27s`.
- Full tests passed with `308 passed in 32.99s`.
- YAML anchor scan found no anchors in the new overlay metrics/config YAML
  files.
- Raw/heavy artifact scan found no payloads in the new overlay artifacts.
- `git diff --check` passed.
