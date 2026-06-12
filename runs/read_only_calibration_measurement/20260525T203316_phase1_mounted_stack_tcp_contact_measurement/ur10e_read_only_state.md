# UR10e Read-Only State Snapshot

Captured at: `2026-05-25T20:35:32+08:00`

Scope: read-only observation after user approved the exact phrase
`I approve this read-only measurement step`.

No robot motion, force control, zeroing/biasing, configuration write, TCP write,
payload write, CoG write, URCap write, OnRobot write, or RTDE register write was
performed.

## Network

- Robot host: `192.168.1.18`
- Ubuntu direct-link device: `enp3s0`
- Ubuntu IPv4: `192.168.1.10/24`
- Same subnet: `true`
- Default route on direct link: `false`
- Ping: `2 transmitted, 2 received, 0% packet loss`

## Interface Ports

- Open ports: `22, 29999, 30001, 30002, 30003, 30004, 30011, 30012, 30013`
- Required read-only ports open: `29999, 30002, 30004`

## Dashboard

- Remote control: `false`
- Safety mode: `Safetymode: NORMAL`
- Robot mode: `Robotmode: RUNNING`
- Program running: `false`
- Program state: `STOPPED <unnamed>`
- Loaded program: `/programs/<unnamed>.urp`
- PolyScope version: `URSoftware 5.11.9.1010452 (Jan 24 2022)`

## RTDE One-Shot Read

- Payload: `0.44`
- Payload CoG: `[0.005, -0.005, 0.025]`
- TCP offset: `[0.0, 0.0, 0.12254000000000001, 0.0, 0.0, 0.0]`
- Actual TCP force:
  - Fx: `-0.46176808021186105`
  - Fy: `0.02528826999436101`
  - Fz: `-3.0929884771286873`
  - Tx: `0.0026244842882380067`
  - Ty: `-0.012659006338312663`
  - Tz: `-0.017206151115417432`
- Force norm: `3.1273706170124274`
- Torque norm: `0.021521849257422766`

This snapshot is not a substitute for the required physical
`tcp_contact_measurements.csv` row.
