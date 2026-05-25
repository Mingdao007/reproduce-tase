# Calibrated Contact Overlay Collision Mask V149 Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v149-overlay-collision-mask`

## Scope

V149 corrects and audits the v148 diagnostic contact overlay so the diagnostic
plane is reserved for the named contact pair:

```text
diagnostic_contact_plane_unaccepted
diagnostic_contact_tip_unaccepted
```

The v148 overlay established the geometry, but it did not explicitly audit
non-target MuJoCo contacts. V149 collision-masks the existing visual/primitive
geoms, keeps the diagnostic plane and tip collidable, and adds a contact
activation probe.

## Result

The v149 audit is:

```text
runs/calibrated_contact_overlay_after_v147/20260525T223000
```

Key metrics:

```text
audit_passed = true
model_ncon_at_seed = 1
target_contact_pair_count_at_seed = 1
non_target_contact_count_at_seed = 0
seed_has_no_non_target_contacts = true
activation_probe_penetration_m = 0.001
activation_probe_target_contact_pair_count = 1
activation_probe_non_target_contact_count = 0
activation_probe_target_normal_force_N = 11.078794158483424
activation_probe_clean_target_contact = true
simulation_can_start_from_diagnostic_overlay = true
diagnostic_overlay_acceptance_status = not_accepted
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

This confirms the overlay is a usable offline diagnostic contact-start scaffold
without non-target contact contamination at the backed-up pose or the 1 mm
activation probe.

## Validation

- `python3 -m py_compile scripts/audit_calibrated_contact_overlay_after_v147.py`
- `scripts/run_tests.sh tests/test_calibrated_contact_overlay_after_v147.py`
  reported `4 passed in 0.28s`.
- `python3 scripts/audit_calibrated_contact_overlay_after_v147.py --run-id 20260525T223000`
- Full `scripts/run_tests.sh` reported `308 passed in 33.10s`.
- YAML anchor scan found no anchors in the v149 overlay metrics/config YAML
  files.
- Raw/heavy artifact scan found no payloads in the v149 overlay artifacts.
- `git diff --check` passed.

## Limit

V149 is still offline diagnostic simulation scaffolding only. It does not
collect live measurements, approve a read-only SOP step, authorize live access,
authorize execution, create approved calibration evidence, accept a contact
model, accept a setup target, relax an orientation gate, prove strict
paper-equivalent feasibility, prove robustness, establish hardware readiness,
or close the completion gate.
