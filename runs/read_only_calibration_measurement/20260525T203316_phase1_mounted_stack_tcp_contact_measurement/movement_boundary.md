# Movement Boundary

This run was created for the approved read-only step
`phase1_mounted_stack_tcp_contact_measurement`.

User approval phrase:

```text
I approve this read-only measurement step
```

Current run rule:

- do not move the robot as part of this run
- do not use Freedrive, Play, jog, URScript, ROS 2 control, or force-control
  motion to collect evidence for this run
- do not write TCP, payload, CoG, URCap, OnRobot, or RTDE register settings
- physical caliper/height-gauge measurement is allowed while the robot remains
  static and safe

If the current pose makes physical measurement inaccessible, this run should
remain unfinalized. The operator may manually move the robot outside this run,
then Codex should create a fresh read-only measurement run after the robot is
again static, not touching the environment, and no program is running.

After any manual repositioning, the operator confirmation needed before a fresh
run is:

```text
Moved and stable; no contact; no program running; ready for a fresh read-only run.
```

Codex may then read Dashboard and RTDE state again, but must still not command
motion or write robot configuration.
