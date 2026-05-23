# Hardware Gate SOP

## Scope

Define the evidence required before any real UR10e motion or force-control
experiment.

## Assumptions

- Current repository state authorizes no real robot motion.
- Hardware checks are read-only unless a later user-approved SOP says
  otherwise.

## Exact Files Touched

- `plans/HARDWARE_GATE_SOP.md`
- Future: `reports/hardware_gate_report.md`

## Commands To Run

Use only read-only checks until explicitly approved:

```bash
python3 scripts/check_ubuntu_network.py
python3 scripts/check_ur_interfaces.py
python3 scripts/check_dashboard_state.py
python3 scripts/read_payload_tcp_state.py
```

These helper scripts are expected in the UR10e bench workspace, not necessarily
inside this reproduction repo.

## Expected Outputs

- Stable Dashboard and RTDE connection evidence.
- Force source decision: UR RTDE, OnRobot URCap registers, or other.
- Measured TCP, payload, CoG, EOAT contact point.
- Emergency stop and protective-stop recovery plan.
- Low-speed, low-force SOP.

## Pass/Fail Criteria

Pass:

- Simulation gates are complete and hardware read-only state is stable.
- User explicitly approves the SOP before any motion.

Fail:

- Motion is proposed while TCP/payload/force source remain unresolved.

## Rollback Point Or Recovery Command

No hardware writes are made in this phase, so rollback is documentation-only.
If a future write is proposed, create a separate rollback plan first.

## Unresolved Risks

- OnRobot force reference mismatch.
- Unverified EOAT TCP and payload.
- Hand-guide issue remains separate and unresolved.

## Next Executable Step

Do not run hardware checks until the user asks. Continue simulation and
documentation first.

