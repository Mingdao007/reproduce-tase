# Awaiting Physical Measurement

Current blocker: `tcp_contact_measurements.csv` has no physical measurement
rows, so the run cannot be finalized as approved read-only evidence.

Required next input from the bench:

```csv
sample_id,datum,tool_axis_sign,distance_mm,instrument,resolution_mm,operator,notes
```

Minimum to unblock finalization:

- one non-placeholder row in `tcp_contact_measurements.csv`
- `tool_axis_sign` must be one of `+x`, `-x`, `+y`, `-y`, `+z`, `-z`
- `distance_mm` must be the measured physical distance, not the RTDE TCP
  readback
- `resolution_mm` must be finite and positive

Preferred for the Phase 1 SOP pass gate:

- three repeated measurements from the same named datum
- notes state the instrument calibration state
- photo paths and hashes are listed in `photos_manifest.md`
- photos show datum, measurement setup, KSM seating, and contact point

Still forbidden in this run:

- robot motion
- force control
- zeroing or biasing
- TCP, payload, CoG, URCap, OnRobot, or RTDE register writes
