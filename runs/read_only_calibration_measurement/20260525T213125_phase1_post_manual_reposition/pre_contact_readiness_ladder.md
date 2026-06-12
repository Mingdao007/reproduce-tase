# Pre-Contact Readiness Ladder

Run id: `20260525T213125_phase1_post_manual_reposition`

Decision date: 2026-05-26

## Purpose

This ladder adds small experiments before any real contact force-control test.
Its purpose is not to make contact physically risk-free. Instead, it separates
all checks that can be done with no robot motion, no contact, and no
configuration writes from later checks that require explicit motion/contact
approval.

Use this wording:

```text
Before contact, we can run non-contact / read-only gates. Passing those gates
reduces unknowns; it does not make commanded contact a zero-risk operation.
```

## Current Basis

Already recorded evidence:

- `85.0 mm` provisional contact-distance candidate;
- dismounted/manual operator measurement;
- KSM-8N drawing;
- v13 CAD metadata;
- mounted visual audit;
- current metrics still keep calibration and hardware-readiness claims false.

## When To Run These Gates

Do not wait until the full manual is finished before starting N1/N2. Manual
reading and no-contact readiness can proceed in parallel.

Recommended timing:

- Continue reading `manual4UR`, especially sections that affect safety,
  enabling, program run/stop state, Freedrive/hand guiding, TCP/payload, and
  force-control behavior.
- Run N1 now if the bench is static and the operator can confirm the required
  no-motion/no-contact condition. N1 is a system/connection/state health check,
  so it is useful before C0 exists.
- Run N2 after N1 passes. N2 creates a no-contact force baseline and may expose
  signal or state issues early.
- Repeat N1 and N2 immediately before any future C0 contact SOP, because robot
  state, cable state, program state, and force baseline are time-dependent.
- Defer N3 until a likely contact direction/target is known. It is still
  no-contact, but it becomes more meaningful when the future C0 geometry is
  defined.
- Defer N4 until just before C0 and only if a qualitative signal sanity check is
  still useful. N4 is not required and is not non-risk.

Short rule:

```text
N1/N2 can be done early and repeated later.
N3 waits for contact geometry.
N4 waits until just before C0, if needed at all.
C0 requires its own separate SOP and approval.
```

## Gate N0: Evidence Closure

Status: done.

Pass criteria:

- `ksm8n_factory_cad_evidence.md` records the 85 mm / 73.9 mm / KSM-8N chain.
- `mounted_stack_visual_assumption_audit.md` records the mounted visual audit.
- `provisional_85mm_contact_experiment_gate.md` states `85.0 mm` is provisional,
  not calibrated mounted-stack TCP.

## Gate N1: Static Bench State, No Motion

Type: read-only / no robot motion / no contact.

Operator checks:

- Robot is not touching the environment.
- KSM-8N remains seated.
- Printed flange fasteners are present.
- Cable has slack and does not pull the EOAT.
- Contact target area is clear.
- No one will press Play, Freedrive, Zero, payload setup, TCP setup, URCap
  settings, or OnRobot setup during this gate.

Codex checks after operator confirmation:

```bash
python3 /home/andy/codex-private-skills/skills/ur10e-realsetup/scripts/check_ubuntu_network.py
python3 /home/andy/codex-private-skills/skills/ur10e-realsetup/scripts/check_ur_interfaces.py
python3 /home/andy/codex-private-skills/skills/ur10e-realsetup/scripts/check_dashboard_state.py
python3 /home/andy/codex-private-skills/skills/ur10e-realsetup/scripts/read_payload_tcp_state.py
```

Required confirmation phrase before running these checks:

```text
静态检查通过；机器人未接触环境；不按 Play；允许只读状态检查。
```

## Gate N2: No-Contact Force Baseline

Type: read-only sampling / no robot motion / no contact / no zeroing.

Purpose:

- Confirm UR RTDE `actual_TCP_force` is readable in the current static mounted
  state.
- Record the no-contact noise/bias level before any approach or force-control
  work.
- Avoid using direct OnRobot Compute Box TCP DAQ `READFT` as force truth while
  the zero/reference mismatch remains unresolved.

Codex check after operator confirmation:

```bash
python3 /home/andy/codex-private-skills/skills/ur10e-realsetup/scripts/sample_tcp_force.py --seconds 30
```

Pass criteria:

- Dashboard remains normal.
- Program state is not unexpectedly running.
- No contact occurs.
- Force trace is finite and has no obvious discontinuity caused by bumping or
  cable strain.
- Results are saved as a baseline only, not as contact evidence.

Required confirmation phrase:

```text
允许进行 30 秒只读 no-contact force baseline；不移动；不 zero；不接触。
```

## Gate N3: No-Contact Clearance And Axis Sanity

Type: visual/manual inspection first; motion only if a separate no-contact
motion SOP is written and explicitly approved.

Purpose:

- Confirm the KSM ball points along the intended tool centerline.
- Confirm there is enough free space for a future approach path.
- Confirm the provisional `+z`/tool-axis interpretation is not obviously
  reversed.

Allowed without motion:

- Compare current mounted photos to the v13 centerline assumption.
- Read `actual_TCP_pose` / `tcp_offset` read-only.
- Mark the expected contact direction in notes.

Not allowed by this ladder alone:

- Jogging toward a surface.
- Running any approach motion.
- Starting a force-control program.

## Gate N4: Zero-Motion Manual Signal Sanity, Optional

Type: optional low-risk check, not non-risk; robot motion still forbidden.

Only consider this if N1-N3 pass and the operator explicitly wants a final
signal sanity check before commanded contact.

Concept:

- Robot remains stopped.
- No program runs.
- Operator may lightly touch the KSM ball by hand or with a soft object while
  Codex records force signals, only if this is physically safe and does not
  move the robot, EOAT, cable, or fixture.

This is not required for the next stage and is not a substitute for a contact
experiment SOP. It exists only to verify sign/response qualitatively.

## Gate C0: First Real Contact SOP, Separate Document

Entering this gate requires a new explicit approval. It is not authorized by
this ladder.

Minimum contents of the later contact SOP:

- exact contact target and fixture;
- exact approach direction;
- max speed;
- max force threshold;
- stop conditions;
- who watches the teach pendant;
- what signal Codex records;
- abort phrase and physical stop action;
- rollback plan if the force signal, contact geometry, or safety mode is
  unexpected.

## Current Recommendation

Proceed next to Gate N1, then Gate N2. Do not attempt commanded contact until
those pass and a separate first-contact SOP exists.
