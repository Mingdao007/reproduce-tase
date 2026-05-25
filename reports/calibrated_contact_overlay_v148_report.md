# Calibrated Contact Overlay V148 Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v148-calibrated-contact-overlay`

## Scope

V148 continues the offline simulation work after the v147 readable-state backup
by generating a diagnostic contact overlay on top of the calibrated v147 MJCF.
The overlay is intentionally marked unaccepted and diagnostic-only.

New offline artifacts:

```text
assets/mjcf/ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.xml
configs/mujoco_ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.yaml
runs/calibrated_contact_overlay_after_v147/20260525T220000
```

The overlay translates the existing v54 tilted 10 degree diagnostic normal
through the current v147 backed-up TCP site. It adds:

```text
diagnostic_contact_plane_unaccepted
diagnostic_contact_tip_unaccepted
```

This creates a deterministic offline start-contact geometry for the current
backed-up UR10e pose. It does not accept the contact model, tip radius, setup
target, force-frame semantics, or orientation gate.

## Result

The v148 audit is:

```text
runs/calibrated_contact_overlay_after_v147/20260525T220000
```

Key metrics:

```text
audit_passed = true
overlay_model_loads = true
model_nq = 6
model_nv = 6
model_ngeom = 9
model_nsite = 1
current_tcp_site_on_diagnostic_plane = true
contact_tip_surface_tangent_to_plane = true
plane_normal_matches_expected = true
tcp_site_shift_m = 0.0
tip_center_error_m = 0.0
tcp_plane_signed_distance_m = 0.0
tip_surface_gap_m = 0.0
plane_normal_error = 3.4120107557038376e-11
contact_tip_radius_m = 0.045
simulation_can_start_from_diagnostic_overlay = true
diagnostic_overlay_acceptance_status = not_accepted
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

The generated overlay can be used as the next offline simulation base when a
diagnostic contact plane is needed. It is not claim-closing evidence.

## Validation

- `python3 -m py_compile scripts/audit_calibrated_contact_overlay_after_v147.py`
- `scripts/run_tests.sh tests/test_calibrated_contact_overlay_after_v147.py`
  reported `4 passed in 0.27s`.
- `python3 scripts/audit_calibrated_contact_overlay_after_v147.py --run-id 20260525T220000`
- Full `scripts/run_tests.sh` reported `308 passed in 32.99s`.
- YAML anchor scan found no anchors in the new overlay metrics/config YAML
  files.
- Raw/heavy artifact scan found no payloads in the new overlay artifacts.
- `git diff --check` passed.

## Limit

V148 is an offline diagnostic contact-geometry scaffold only. It does not
collect live measurements, approve a read-only SOP step, authorize live access,
authorize execution, create approved calibration evidence, accept a contact
model, accept a setup target, relax an orientation gate, prove strict
paper-equivalent feasibility, prove robustness, establish hardware readiness,
or close the completion gate.
