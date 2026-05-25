# Contact Setup Target Acceptance Review Template

This template is a separate, non-default review path for a future contact
model or setup-target definition change. It is not part of read-only evidence
finalization and cannot be invoked by
`scripts/finalize_read_only_calibration_measurement_evidence.py`.

Expected review root:

```text
runs/contact_setup_target_acceptance_review/<YYYYMMDDTHHMMSS>/
```

Creating a review scaffold does not accept any contact model, setup target,
gate change, calibration claim, hardware-readiness claim, or controller
change. It does not authorize robot motion, force control, zeroing, TCP or
payload writes, URCap changes, OnRobot settings changes, or RTDE register
writes.

Before any future contact/setup-target definition can be accepted, a separate
approved review must cite approved read-only evidence, a passed
approved-read-only audit, measurement uncertainty, contact datum evidence,
force-source reconciliation, and the exact replacement definition.
