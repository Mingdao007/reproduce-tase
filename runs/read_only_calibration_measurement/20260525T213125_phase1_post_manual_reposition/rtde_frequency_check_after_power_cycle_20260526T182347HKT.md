# RTDE Frequency Check After Power Cycle

Run id: `20260525T213125_phase1_post_manual_reposition`

Execution time: 2026-05-26 18:23 HKT

Scope: read-only UR10e state check and RTDE `actual_TCP_force` frequency check
after the operator reported the robot had been powered off while away.

No robot motion, no TCP/payload write, no zeroing/biasing, no URCap setting
change, and no force-control program was started by Codex.

## Pre-Sampling State

- Ubuntu direct link: OK.
  - robot host: `192.168.1.18`
  - device: `enp3s0`
  - Ubuntu IPv4: `192.168.1.10/24`
  - robot ping: OK
- UR required ports: OK.
  - `29999`, `30002`, and `30004` were open.
- Dashboard before sampling:
  - `remote=false`
  - `Safetymode: NORMAL`
  - `Robotmode: RUNNING`
  - `Program running: false`
  - `programState: STOPPED <unnamed>`
- Payload/TCP readback:
  - payload: `0.44 kg`
  - payload CoG: `[0.005, -0.005, 0.025] m`
  - TCP offset: `[0.0, 0.0, 0.12254, 0.0, 0.0, 0.0]`
  - one-shot `actual_TCP_force`: approximately
    `Fx=0.018 N`, `Fy=0.872 N`, `Fz=-1.385 N`, `|F|=1.636 N`

## Frequency Check

Command run:

```bash
python3 /home/andy/codex-private-skills/skills/ur10e-realsetup/scripts/sample_tcp_force.py --seconds 10 --hz 1000 --plot fz --output-dir /home/andy/reproduce-tase/runs/read_only_calibration_measurement/20260525T213125_phase1_post_manual_reposition/rtde_frequency_check_after_power_cycle_20260526T182347HKT --prefix rtde_1000hz_request_actual_tcp_force_20260526T182347HKT
```

Artifacts:

- CSV:
  `rtde_frequency_check_after_power_cycle_20260526T182347HKT/rtde_1000hz_request_actual_tcp_force_20260526T182347HKT_20260526_182422.csv`
- Fz plot:
  `rtde_frequency_check_after_power_cycle_20260526T182347HKT/rtde_1000hz_request_actual_tcp_force_20260526T182347HKT_20260526_182422_fz.png`

Measured timing:

- requested frequency: `1000 Hz`
- requested duration: `10 s`
- samples returned: `4999`
- sample count per requested duration: `499.9 Hz`
- first-to-last timestamp span: `9.994718 s`
- first-to-last measured frequency: `500.064 Hz`
- mean inter-sample interval: `0.00199974 s`
- median inter-sample interval: `0.00199914 s`
- p95 inter-sample interval: `0.00204206 s`
- p99 inter-sample interval: `0.00208306 s`
- all parsed values finite: yes
- exact repeated consecutive wrench tuples: `0`

Post-sampling Dashboard:

- `Program running: false`
- `programState: STOPPED <unnamed>`
- `Safetymode: NORMAL`
- `Robotmode: RUNNING`

## Conclusion

The current UR RTDE `actual_TCP_force` readback is not `1 kHz`. Even when the
client requested `1000 Hz`, the observed rate was approximately `500 Hz`.

Use this wording:

```text
After the power cycle, UR RTDE actual_TCP_force is currently reading at about
500 Hz, not 1 kHz, under this read-only test.
```

This result is for UR RTDE `actual_TCP_force` on port `30004`. It does not
answer the separate OnRobot Compute Box direct TCP DAQ / PolyScope variable
export frequency question.
