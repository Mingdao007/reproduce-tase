# Base-Z Plus1mm Split Summary

Run root: `runs/base_z_plus1mm_split/20260525T071440`

- Exact planned cell status: `executed_unresolved`
- Exact closure passed: `False`
- Broader start search passed: `True`
- Terminal force/x-y/contact passed: `True`
- Terminal diagnostic orientation passed: `False`
- Terminal orientation: `0.11948560786548146` rad
- Exact gate: `0.08` rad
- Relaxed gate margin: `0.0005143921345185376` rad
- Relaxed path passed: `True`
- Relaxed stitched recovered: `False`
- Failed cell closed: `False`

| evidence slice | pass | key value | interpretation |
| --- | --- | ---: | --- |
| exact start | `False` | `['force_error_N', 'target_contact_count']` | `planned seed misses contact` |
| broader start | `True` | `0.14209391841232932` N | `start contact is local seed-limited` |
| terminal force/x-y/contact | `True` | `2.3037127760972e-15` rad yaw gap | `not a force/x-y/contact failure` |
| terminal orientation gate | `False` | `0.039485607865481456` rad excess | `0.08 rad gate blocks terminal/path` |
| relaxed Stage A/path | `True` | `10.018584837157274` s | `run-local 0.12 rad gate recovers endpoint/path` |
| relaxed stitched | `False` | `3/4, 3/4` | `Stage B handoff remains blocked` |

Interpretation:

- The exact v99 `base_z_plus1mm` command remains executed-unresolved.
- The start-contact miss is not fundamental for `+1.0 mm`; broader seeds recover a 5 N target-pair contact.
- The terminal/path blocker is the current `0.08 rad` orientation gate under the contact-point model, not force, x/y, contact count, or yaw handling.
- The run-local `0.12 rad` gate recovers Stage A endpoint/path evidence, but stitched Stage B still fails, so no failed cell is closed.
