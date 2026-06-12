# KSM-8N Factory And CAD Evidence

Run id: `20260525T213125_phase1_post_manual_reposition`

This note records the 2026-05-26 photo/CAD evidence review for the mounted
stack TCP/contact measurement planning. It does not finalize the physical
measurement CSV.

## User Supplement

The operator clarified:

- In `KSM-8N`, `8` means an 8 mm ball diameter.
- `N` indicates the threaded/stud version.
- The purchased KSM-8N drawing gives approximately `2.1 + 9 = 11.1 mm`.
- The operator measured the cylinder body, excluding the ball, at about
  `9 mm`; given the caliper uncertainty, visual checking of the full ball plus
  housing length is consistent with `11.1 mm`.
- In the interrupted goal context, the operator also reported a direct
  dismounted/manual measurement of the end-to-end stack as `85 mm`, with
  estimated error not exceeding `0.1 mm`.
- The operator separately reported `73.9 mm` from the large circular base /
  printed contact face reference to the KSM-8N interface, with estimated error
  not exceeding `0.1 mm`.
- The operator's consistency check was `73.9 + 9.1 + 2.0 = 85.0 mm`, matching
  the KSM drawing/CAD split between visible housing height and exposed ball.
- The operator also reported that the OnRobot FT sensor contact face and the
  printed part contact face are flat, with no observed recess or protrusion.

## Photo Evidence

Source photos are indexed in `photos_manifest.md`.

- `photo-caliper-label-20260526`: caliper label shows `Resolution:
  0.1mm/0.01"` and `Accuracy: +/-0.2mm/+/-0.01"`.
- `photo-caliper-manual-20260526`: manual/spec sheet is consistent with
  `0-150 mm` range, `0.1 mm / 0.01 in` resolution, and `+/-0.2 mm` accuracy.
- `photo-ksm8n-drawing-20260526`: KSM-8N drawing shows ball size `phi 8 mm`,
  threaded stem `M6`, housing diameter `phi 15`, thread length `12 mm`, and
  the `11.1 mm` / `9.1 mm` height relationship.

## CAD Cross-Check

Local EOAT metadata source:

```text
/home/andy/ur10e_ros2_ws/experiments/onrobot_hex_e_v2_3010007655/eoat_design/v13_ksm8n_receiver_5p3mm_side_window_85mm/verification.json
```

Relevant metadata values:

- `ksm_ball_diameter_mm`: `8.0`
- `ksm_housing_total_height_to_ball_top_mm`: `11.1`
- `ksm_visible_housing_height_mm`: `9.1`
- `ksm_ball_exposed_height_mm`: `2.0`
- `ksm_thread_diameter_mm`: `6.0`
- `ksm_thread_length_mm`: `12.0`
- `contact_point_from_flange_face_mm`: `85.0`

The v13 README also describes the contact module as a purchased KSM-8N held by
a captive M6 hex nut, and records an 85.0 mm design contact point from the CAD
flange face.

## Decision Boundary

The purchased KSM-8N photo/drawing and v13 CAD metadata are usable as auxiliary
evidence for:

- checking that the purchased KSM-8N is dimensionally plausible;
- bounding the expected ball/housing contribution to the contact datum;
- explaining why a physical reading near the v13 CAD contact point would be
  plausible if the mounted EOAT is the same v13 design.
- treating `85.0 mm` as the current operator-reported/design-consistent working
  contact-distance candidate for planning and sanity checks.

They are not sufficient by themselves to finalize `tcp_contact_measurements.csv`
or to write a robot TCP setting, because the mounted stack still depends on:

- confirming the currently mounted printed EOAT is the v13 design;
- confirming the KSM-8N is seated to the same depth assumed by the CAD model;
- accounting for OnRobot HEX-E / adapter / any extra stack-up between the
  selected datum and the printed EOAT flange face;
- confirming the current tool-axis sign convention and actual mounted
  orientation.

Until those conditions are checked, `tcp_contact_measurements.csv` must remain
unfinalized and the `85.0 mm` value should be treated as an
operator-reported/design-consistent candidate, not accepted mounted-stack
calibration evidence.
