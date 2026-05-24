# Positive Terminal Orientation Report

## Summary

v69 follows up v68 by isolating the positive-side terminal orientation failure.
It compares the current v54 contact-point model against the older sphere-center
model as a non-solution comparison, and it evaluates full-rotation orientation
error versus force-normal-only orientation error for the same positive base-z
deltas.

The formal run is:

- `runs/positive_terminal_orientation/20260524T171705`
- command: `scripts/audit_positive_terminal_orientation.py`
- parent commit before v69 changes: `cb2f85805ce32945fc91775bdfadc85552023dc1`

For the current contact-point model, all `8 / 8` positive terminal candidates
satisfy force, x/y, and target-pair contact, but `0 / 8` pass the diagnostic
`0.08 rad` orientation gate. Full-rotation and force-normal-only errors are
identical to numerical precision, so yaw about the normal is not the limiter.
The wrong-sign `-z` convention is also ruled out by errors near `3 rad`.

## Metrics

From `runs/positive_terminal_orientation/20260524T171705/metrics.yaml`:

| variant | diagnostic pass | force/x-y/contact pass | max diagnostic delta | threshold for all force/x-y/contact cases | max yaw gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| current contact-point model | `0 / 8` | `8 / 8` | `none` | `0.11948560786548146 rad` | `4.884981308350689e-15 rad` |
| legacy sphere-center model | `6 / 8` | `8 / 8` | `+0.5 mm` | `0.09525838838593075 rad` | `2.400857290751901e-15 rad` |

Current contact-point model terminal errors:

| delta mm | diagnostic pass | full rotation rad | force-normal-only rad |
| ---: | --- | ---: | ---: |
| `+0.05` | `false` | `0.0838175590896232` | `0.08381755908962295` |
| `+0.10` | `false` | `0.08565245135290023` | `0.08565245135289722` |
| `+0.15` | `false` | `0.0874945141256073` | `0.08749451412560418` |
| `+0.20` | `false` | `0.08934348318237911` | `0.08934348318237903` |
| `+0.25` | `false` | `0.09119904265401833` | `0.09119904265401542` |
| `+0.50` | `false` | `0.10056247728510045` | `0.10056247728509893` |
| `+0.75` | `false` | `0.11002164736335575` | `0.11002164736335086` |
| `+1.00` | `false` | `0.11948560786548146` | `0.11948560786547915` |

## Interpretation

The current positive-side terminal failure is an orientation-margin issue under
the current contact-point model and diagnostic gate. It is not caused by yaw
handling in `rotation_aligning_local_z_to_normal`: the full-rotation error and
force-normal-only error differ by less than `5e-15 rad`.

The legacy sphere-center model has a wider orientation margin and passes the
diagnostic gate through `+0.5 mm`, but it is already known to put the 85 mm TCP
site at the colliding sphere center. It is retained here only as evidence that
the contact-point geometry convention changes the terminal orientation margin,
not as a hardware-ready fix.

## Claim Boundary

This is terminal-state diagnostic simulation evidence only. It is not:

- strict paper-equivalent feasibility
- a path or stitched trajectory recovery
- a robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

## Next Step

If the diagnostic label can justify a `0.12 rad` terminal orientation envelope,
the next branch should test whether the current contact-point model can recover
positive-side path and stitched feasibility under that explicit relaxed gate.
If `0.12 rad` is not acceptable, the next branch should revisit the physical
contact-point model or terminal target definition rather than changing yaw or
normal-only orientation handling.
