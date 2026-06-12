# Manual Reposition Reference

Captured at: `2026-05-25T21:08:18+08:00`

This is a read-only reference for deciding whether the operator needs to move
the robot outside the current approved read-only run. It is not evidence that
can finalize the current run after movement.

## Current Read-Only Pose

- Robot host: `192.168.1.18`
- `actual_q` radians:
  `[0.5923577547073364, -1.3196546000293274, -2.041857957839966, -1.3558802616647263, 1.573241114616394, -0.9888723532306116]`
- `actual_q` degrees:
  `[33.93959930657605, -75.61063899670518, -116.98984334943123, -77.68621651848252, 90.14007602397679, -56.65821231728398]`
- `actual_TCP_pose`:
  `[0.5320148987471166, 0.14820153735577757, 0.41122946324169585, 3.137414942968011, 0.014772635528874943, -0.006382953367449369]`
- `actual_TCP_force`:
  `[-0.19579837145127849, 0.28718290486791104, -2.875970902414155, -0.017803572847880374, -0.025730835478767325, -0.1620676403148187]`
- Force norm: `2.896898281722062 N`
- Torque norm: `0.16506048327143183 Nm`

## If Current Pose Is Measurable

Do not move. Keep this run open and collect physical caliper/height-gauge rows
for `tcp_contact_measurements.csv`.

## If Current Pose Is Not Measurable

Manual operator movement is outside this run. Use the smallest movement that
exposes the mounted stack datum and KSM/contact datum for a physical
measurement.

Conservative after-move acceptance targets before starting a fresh run:

- robot is static and not touching the environment
- no program is running
- safety mode is normal
- cables are slack
- TCP is clear of the bench and contact surfaces
- contact datum is visible and reachable by the measuring instrument
- no TCP, payload, CoG, URCap, OnRobot, or RTDE register settings were changed

Because Codex does not have live visual collision/fixture information, do not
treat the current joint values as a commanded path or target. The operator
should choose a safe visible pose manually, then report:

```text
Moved and stable; no contact; no program running; ready for a fresh read-only run.
```

Codex will then create a fresh read-only measurement run and re-read Dashboard
and RTDE state.
