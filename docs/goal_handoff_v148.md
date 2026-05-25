# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V148

Date: 2026-05-25

Use this after the v147 readable-state simulation seed backup and calibrated
MuJoCo replay audit. Verify every claim from repository state before editing
files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v147 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v148.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/readable_state_sim_seed_v147_report.md`
- `runs/current_real_snapshot_sim_seed_after_v146/20260525T210000/metrics.yaml`
- `runs/calibrated_urdf_fk_snapshot_after_v147/20260525T211000/metrics.yaml`
- `runs/calibrated_mjcf_replay_after_v147/20260525T212000/metrics.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: v147 backs up the currently readable real
UR10e state and provides a calibrated offline simulation seed. The repository
seed and calibration are in
`data/ur10e_real_snapshot_20260525T1641/`, the calibrated URDF is
`assets/urdf/ur10e_calibrated_20260525T1641.urdf`, and the calibrated MuJoCo
seed is `assets/mjcf/ur10e_calibrated_20260525T1641_tcp_offset.xml`.

The calibrated MJCF loads in MuJoCo and reproduces the backed-up RTDE TCP pose
with `position_error_m = 2.016003536429377e-06` and
`orientation_error_rad = 6.278799181396437e-06`, while the previous nominal
primitive MuJoCo model mismatched the same RTDE pose by
`1.1351349451303372 m` and `2.840514162594206 rad`.

V147 is offline kinematic seed infrastructure only:
`completion_claim_allowed = false` and `do_not_mark_goal_complete = true`.
It is not approved read-only calibration evidence, not contact/setup-target
acceptance, not orientation-gate acceptance, not robustness proof, not
hardware readiness, and not completion evidence.

The exact first approved-evidence candidate remains
`phase1_mounted_stack_tcp_contact_measurement`, scoped to
`tcp_contact_measurements.csv`, but it may only be executed after explicit user
confirmation with the exact registered phrase
`I approve this read-only measurement step` and exact step scope. Without that
approval, continue only non-final offline work. Do not upgrade v127-v147
readiness/status/frontier/freshness/criterion/boundary/backup artifacts into
evidence. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V147 Evidence

Expected branch:

```text
exp/tase-ur10e-v147-readable-state-sim-seed
```

V147 artifacts:

```text
scripts/audit_current_real_snapshot_sim_seed_after_v146.py
tests/test_current_real_snapshot_sim_seed_after_v146.py
runs/current_real_snapshot_sim_seed_after_v146/20260525T210000
scripts/audit_calibrated_urdf_fk_snapshot_after_v147.py
tests/test_calibrated_urdf_fk_snapshot_after_v147.py
runs/calibrated_urdf_fk_snapshot_after_v147/20260525T211000
scripts/audit_calibrated_mjcf_replay_after_v147.py
tests/test_calibrated_mjcf_replay_after_v147.py
runs/calibrated_mjcf_replay_after_v147/20260525T212000
reports/readable_state_sim_seed_v147_report.md
```

Key result:

```text
calibration_hash = calib_7367377276742883610
offline_simulation_can_continue_from_seed = true
calibrated_urdf_fk_matches_rtde_tcp = true
calibrated_mjcf_replay_matches_rtde_tcp = true
position_error_m = 2.016003536429377e-06
orientation_error_rad = 6.278799181396437e-06
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

## Recommended V148 Work

Use `configs/mujoco_ur10e_calibrated_20260525T1641_tcp_offset.yaml` as the
offline kinematic basis for the next simulation step. Add contact plane,
contact patch, and force-frame assumptions only through the existing
contact/setup-target acceptance path; do not treat the readable-state backup
as contact calibration evidence.

If the user gives the exact approval phrase and exact phase1 scope, use only
that one audited packet and registered step. Otherwise continue offline only.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Do not treat read-only force traces or direct OnRobot TCP DAQ values as
  accepted contact-model or force-control validation.

## Validation

- Focused v147 tests reported `4 passed`, `5 passed`, and `4 passed`.
- Full tests passed with `304 passed in 32.86s`.
- YAML anchor scan found no anchors in the new generated metrics/data/config
  YAML files.
- Raw/heavy artifact scan found no payloads in the new lightweight artifacts.
- `git diff --check` passed.
