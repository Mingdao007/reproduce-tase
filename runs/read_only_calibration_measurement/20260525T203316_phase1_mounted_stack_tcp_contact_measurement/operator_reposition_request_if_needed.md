# Operator Reposition Request If Needed

Use this only if the current static pose cannot be measured physically. Any
movement is outside the current approved read-only run.

Current read-only TCP pose:

```text
[0.5320, 0.1482, 0.4112, 3.1374, 0.0148, -0.0064]
```

Suggested manual reposition objective:

- keep approximately the same TCP orientation
- keep approximately the same `x` and `y`
- raise the TCP in base `z` by about `+0.08 m` to `+0.12 m`
- target TCP pose range after manual movement:

```text
x: 0.50 m to 0.56 m
y: 0.12 m to 0.18 m
z: 0.49 m to 0.53 m
rx: 3.05 rad to 3.20 rad
ry: -0.08 rad to 0.10 rad
rz: -0.10 rad to 0.10 rad
```

Reason: this preserves the existing downward/near-vertical tool orientation
while giving more clearance for a caliper or height gauge.

Operator stop conditions:

- any contact risk
- cable strain
- confusing PolyScope state
- unexpected safety mode
- program starts running
- TCP/payload/zero/setup screen is entered

After movement, stop the robot, do not run a program, and report:

```text
Moved and stable; no contact; no program running; ready for a fresh read-only run.
```

Codex will then create a fresh read-only measurement run and verify Dashboard
and RTDE state before accepting any physical measurement rows.
