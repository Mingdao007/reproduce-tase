# Provisional 85 mm Contact Experiment Gate

Run id: `20260525T213125_phase1_post_manual_reposition`

Decision date: 2026-05-26

## Problem

The operator does not currently have a height gauge, dial indicator stand, or
depth gauge suitable for a better mounted-stack measurement. Direct mounted
measurement with the available caliper is unreliable because the tool stack is
suspended and the KSM-8N ball can be compressed or disturbed.

The operator has already performed a dismounted/manual measurement and reported:

- end-to-end distance: `85 mm`, estimated error not exceeding `0.1 mm`;
- printed contact-face / KSM interface chain: `73.9 + 9.1 + 2.0 = 85.0 mm`;
- KSM-8N drawing and v13 CAD metadata are consistent with this value;
- mounted visual photos show the current tool is consistent with the v13-style
  KSM-8N receiver and centerline ball layout.

## Engineering Decision

Do not block all contact-force work on a better mounted-stack metrology setup.
Use `85.0 mm` as a provisional contact experiment candidate under a restricted
scope:

```text
contact_distance_candidate_mm = 85.0
status = provisional_for_low_risk_contact_experiment_preparation
not_status = calibrated_mounted_stack_tcp
```

This is an explicit engineering acceptance of the available evidence for
progress, not a claim that mounted-stack calibration is complete.

## Allowed Use

Allowed under this gate:

- planning contact experiments;
- simulation and controller sanity checks using `85.0 mm`;
- no-contact UR/RTDE state checks;
- low-speed, no-contact posture checks if a separate motion SOP and explicit
  user approval exist;
- preparing a temporary/run-local TCP candidate value for a future explicitly
  approved experiment.

## Not Allowed By This Gate Alone

This gate does not authorize:

- writing a permanent UR TCP setting;
- writing ROS 2 launch/config files as if the value were calibrated truth;
- claiming mounted-stack TCP calibration is complete;
- claiming hardware readiness;
- running force-control contact motion without a separate explicit contact
  experiment SOP, stop conditions, and user approval;
- using direct OnRobot Compute Box TCP DAQ `READFT` values as force truth while
  the current zero/reference mismatch remains unresolved.

## Required Next Stage Before Contact Force Control

Before any contact-force experiment, perform the staged readiness ladder in
`pre_contact_readiness_ladder.md`. At minimum:

1. Read-only state check:
   - Dashboard safety mode normal.
   - Program not running unless intentionally required.
   - No current force-control program.
   - No zeroing, TCP write, payload write, URCap setting change, or RTDE
     register write in this gate.

2. Physical inspection:
   - KSM-8N is still seated.
   - Printed flange fasteners are present.
   - Cable has slack.
   - No visible collision risk.
   - Contact target is clear and low-risk.

3. Force-signal route decision:
   - Prefer UR RTDE `actual_TCP_force` for UR-side monitoring.
   - Treat OnRobot direct TCP DAQ `READFT` as separate/unreconciled until the
     PolyScope variable / RTDE output-register route is verified.

4. Motion/contact approval:
   - Use a dedicated contact experiment SOP.
   - Start with no-contact verification.
   - Then use the smallest possible low-speed approach and low force threshold.
   - Stop on unexpected force, cable strain, fixture movement, safety-mode
     change, or confusing UI state.

## Current Conclusion

The project may proceed past the metrology blocker by using `85.0 mm` as a
provisional working candidate. The correct wording is:

```text
85.0 mm is accepted for provisional low-risk contact experiment preparation,
based on dismounted operator measurement, KSM-8N drawing, v13 CAD metadata, and
mounted visual audit. It is not yet a calibrated mounted-stack TCP.
```

Keep `metrics.yaml` calibration and hardware-readiness claims false until a
later experiment explicitly upgrades the evidence.
