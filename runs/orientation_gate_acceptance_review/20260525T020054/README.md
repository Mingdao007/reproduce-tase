# Orientation Gate Acceptance Review Template

This template is a separate, non-default review path for a future replacement
orientation gate. It is not part of read-only evidence finalization and cannot
be invoked by `scripts/finalize_read_only_calibration_measurement_evidence.py`.

Expected review root:

```text
runs/orientation_gate_acceptance_review/<YYYYMMDDTHHMMSS>/
```

Creating a review scaffold does not accept any gate and does not authorize
robot motion, force control, zeroing, TCP or payload writes, URCap changes,
OnRobot settings changes, RTDE register writes, or hardware-readiness claims.

Before any future gate can be accepted, a separate approved review must cite a
passed approved-read-only evidence run and compare the uncertainty budget
against the v85 margins:

- `0.03245531101442353 deg`
- `14.963398168061882 um`
