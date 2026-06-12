# Post-Manual-Reposition Next Steps

The operator reported that the robot has been moved, possibly not to the
suggested pose. Treat the old run as unfinalized. Do not use post-move data to
finalize this run.

## Objective

Recover into a safe, static, read-only state, then start a fresh read-only
measurement run if physical TCP/contact measurement is possible.

## Operator Steps

1. Stop all manual movement.
   - Release Freedrive/jog controls.
   - Do not press Play.
   - Do not run force control.
   - Do not enter TCP, payload, zero, installation, URCap setup, or OnRobot
     setup screens.

2. Check immediate safety.
   - If there is contact risk, cable tension, fixture collision, or confusing
     robot state, stop and do not continue.
   - If the situation is unsafe, use the lab's normal emergency stop procedure.

3. Confirm the robot is static.
   - Robot is not moving.
   - Tool is not touching the environment.
   - EOAT/KSM/contact datum is visible.
   - A caliper or height gauge can reach the datum without pushing the robot or
     cables.

4. Check the teach pendant at a high level.
   - Program is stopped or not running.
   - Safety mode appears normal.
   - No force-control program is running.
   - No setup/write operation is active.

5. If the pose is not physically measurable, move manually again only if it is
   safe.
   - Use the smallest movement needed.
   - Prefer preserving the current tool orientation.
   - Prefer raising or clearing the tool rather than changing the contact
     datum convention.
   - Stop immediately on contact risk or cable strain.

6. When the pose is stable and measurable, send Codex exactly:

```text
Moved and stable; no contact; no program running; ready for a fresh read-only run.
```

## Codex Steps After Confirmation

1. Create a fresh read-only measurement run.
2. Read Dashboard state.
3. Read RTDE state once.
4. Verify no motion, no force control, no configuration write, and no zeroing.
5. Ask the operator for physical measurement rows.

## Measurement Rows Needed After Verification

Provide at least one row, preferably three repeated rows:

```csv
sample_id,datum,tool_axis_sign,distance_mm,instrument,resolution_mm,operator,notes
```

Example format:

```csv
tcp01,UR flange face,+z,122.54,digital caliper,0.01,Mingdao,calibrated; measured on mounted stack
tcp02,UR flange face,+z,122.55,digital caliper,0.01,Mingdao,repeat 2
tcp03,UR flange face,+z,122.54,digital caliper,0.01,Mingdao,repeat 3
```
