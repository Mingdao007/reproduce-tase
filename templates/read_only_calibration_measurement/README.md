# Read-Only Calibration Measurement Template

This template instantiates the v87 SOP artifact:

`reports/read_only_calibration_measurement_sop.md`

It is for planning and read-only evidence capture only. Creating a run folder
from this template does not authorize robot motion, force control, zeroing, TCP
or payload writes, URCap changes, OnRobot settings changes, or RTDE register
writes.

Expected run root:

```text
runs/read_only_calibration_measurement/<YYYYMMDDTHHMMSS>/
```

Before filling any worksheet, confirm:

- the user explicitly approved the exact read-only step
- the robot will not be moved
- no configuration write or zeroing operation is planned
- direct OnRobot TCP DAQ `READFT` is informational only until reconciled
