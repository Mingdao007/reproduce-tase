# Mounted Stack Visual Assumption Audit

Run id: `20260525T213125_phase1_post_manual_reposition`

Inspection date: 2026-05-26

This note records a visual audit of four freshly transferred mounted-stack
photos. It is not a distance measurement and does not finalize the physical
measurement CSV.

## Photos Inspected

Photos are indexed in `photos_manifest.md`:

- `photo-mounted-side-left-20260526`
- `photo-mounted-front-oblique-20260526`
- `photo-mounted-side-right-20260526`
- `photo-mounted-front-axis-20260526`

## Visual Findings

- The printed EOAT is visibly mounted on the UR10e / OnRobot HEX-E tool stack.
- The mounted tool geometry is consistent with the v13-style KSM-8N receiver:
  broad printed flange, tapered printed body, front receiver, and side nut
  window are visible.
- The KSM-8N appears centered on the printed tool axis, with the ball exposed
  at the front contact point.
- The side window and visible metal threaded/stud region are consistent with
  the KSM-8N threaded/stud version noted by the operator.
- The front fasteners are present and the printed flange does not show an
  obvious gross gap, tilt, missing fastener, or visible collision state in the
  photos.
- The cable loop is visible and does not appear to be pulling the printed EOAT
  or KSM receiver in the inspected views.

## What The Photos Support

The photos support using `85.0 mm` as a stronger
operator-reported/design-consistent working candidate than before, because the
current mounted tool visually matches the CAD/metadata assumptions already
recorded in `ksm8n_factory_cad_evidence.md`.

They also support the practical tool-axis convention for this note:

```text
OnRobot tool-side stack -> printed EOAT centerline -> KSM-8N ball
```

## What The Photos Do Not Prove

The photos do not prove:

- the exact mounted-stack distance from the selected datum to the KSM ball;
- that every hidden interface is perfectly flush over the full contact face;
- the exact KSM seating depth to sub-millimeter tolerance;
- that the currently mounted print is definitively the v13 CAD file without a
  version mark or independent geometry check;
- that `85.0 mm` is accepted as a UR TCP setting or calibrated hardware claim.

## Decision

For planning and sanity checks, treat:

```text
contact_distance_candidate_mm = 85.0
source = operator measurement + KSM-8N drawing + v13 CAD + mounted visual audit
status = working candidate, not mounted-stack calibration
```

Keep `tcp_contact_measurements.csv` unfinalized until a reliable measurement
method, fixture, or acceptance decision explicitly upgrades this candidate into
calibrated mounted-stack evidence.
