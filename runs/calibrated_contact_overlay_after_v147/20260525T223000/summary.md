# Calibrated Diagnostic Contact Overlay Summary

Run root: `/home/andy/reproduce-tase/runs/calibrated_contact_overlay_after_v147/20260525T223000`

- Audit passed: `True`
- Overlay model loads: `True`
- Current TCP site on diagnostic plane: `True`
- Contact tip surface tangent to plane: `True`
- Seed non-target contact count: `0`
- Activation probe target contact count: `1`
- Activation probe non-target contact count: `0`
- TCP site shift: `0.0` m
- Tip surface gap: `0.0` m
- Simulation can start from diagnostic overlay: `True`
- Diagnostic overlay acceptance status: `not_accepted`
- Completion claim allowed: `False`

Interpretation:

- The generated overlay adds an unaccepted diagnostic plane and tip sphere to the v147 calibrated kinematic seed.
- Existing visual/primitive geoms are collision-masked so the diagnostic plane is reserved for the named tip pair.
- It is a start-contact geometry scaffold for offline simulation only, not contact calibration or setup-target acceptance.
