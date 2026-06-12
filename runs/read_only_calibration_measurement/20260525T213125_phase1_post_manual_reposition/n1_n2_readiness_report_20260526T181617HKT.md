# N1/N2 Readiness Report

Run id: `20260525T213125_phase1_post_manual_reposition`

Execution time: 2026-05-26 18:16 HKT

Scope: read-only UR10e state checks and no-contact RTDE
`actual_TCP_force` baseline. No robot motion, no TCP/payload write, no
zeroing/biasing, no URCap setting change, and no force-control program was
started by Codex.

Operator context: the operator asked Codex to run N1/N2 while continuing to read
`manual4UR`. Codex cannot independently observe the physical bench, so the
physical no-contact state remains an operator-side condition.

## N1 Machine-Side Checks

Commands run:

```bash
python3 /home/andy/codex-private-skills/skills/ur10e-realsetup/scripts/check_ubuntu_network.py
python3 /home/andy/codex-private-skills/skills/ur10e-realsetup/scripts/check_ur_interfaces.py
python3 /home/andy/codex-private-skills/skills/ur10e-realsetup/scripts/check_dashboard_state.py
python3 /home/andy/codex-private-skills/skills/ur10e-realsetup/scripts/read_payload_tcp_state.py
```

Results:

- Ubuntu direct link: OK.
  - device: `enp3s0`
  - connection: `Profile 2`
  - Ubuntu IPv4: `192.168.1.10/24`
  - robot ping: OK
  - no default route on the direct UR link
- UR interfaces: OK.
  - required ports open: `29999`, `30002`, `30004`
  - additional observed open ports: `22`, `30001`, `30003`, `30011`, `30012`,
    `30013`
- Dashboard:
  - initial read had one inconsistent response: `Program running: true` while
    `programState: STOPPED <unnamed>`.
  - two immediate repeat reads both reported `Program running: false` and
    `programState: STOPPED <unnamed>`.
  - final post-N2 Dashboard read also reported `Program running: false`,
    `programState: STOPPED <unnamed>`, `Safetymode: NORMAL`, and
    `Robotmode: RUNNING`.
- Payload/TCP readback:
  - payload: `0.44 kg`
  - payload CoG: `[0.005, -0.005, 0.025] m`
  - TCP offset: `[0.0, 0.0, 0.12254, 0.0, 0.0, 0.0]`
  - one-shot `actual_TCP_force`: approximately
    `Fx=-0.031 N`, `Fy=-0.030 N`, `Fz=0.223 N`, `|F|=0.227 N`

N1 machine-side verdict: pass with note. The transient Dashboard inconsistency
was not reproduced on two repeat reads or the post-N2 read.

## N2 No-Contact Force Baseline

Command run:

```bash
python3 /home/andy/codex-private-skills/skills/ur10e-realsetup/scripts/sample_tcp_force.py --seconds 30 --output-dir /home/andy/reproduce-tase/runs/read_only_calibration_measurement/20260525T213125_phase1_post_manual_reposition/n2_no_contact_force_baseline_20260526T181617HKT --prefix n2_no_contact_20260526T181617HKT
```

Artifacts:

- CSV:
  `n2_no_contact_force_baseline_20260526T181617HKT/n2_no_contact_20260526T181617HKT_20260526_181653.csv`
- Plot:
  `n2_no_contact_force_baseline_20260526T181617HKT/n2_no_contact_20260526T181617HKT_20260526_181653.png`
- Fz plot:
  `n2_no_contact_force_baseline_20260526T181617HKT/n2_no_contact_20260526T181617HKT_20260526_181653_fz.png`
- Fxy plot:
  `n2_no_contact_force_baseline_20260526T181617HKT/n2_no_contact_20260526T181617HKT_20260526_181653_fxy.png`

Sampling summary:

- duration request: `30 s`
- requested sample rate: `20 Hz`
- samples: `601`
- all parsed values finite: yes
- time step mean: `0.0499995 s`
- time step min/max: `0.0497119 s` / `0.0503139 s`
- time step p99: `0.0500798 s`

Force summary:

| signal | mean | std | min | max | max step |
| --- | ---: | ---: | ---: | ---: | ---: |
| `Fx_N` | `2.0930` | `0.2776` | `1.3039` | `2.8475` | `1.0677` |
| `Fy_N` | `1.9160` | `0.2076` | `1.2702` | `2.6743` | `1.0651` |
| `Fz_N` | `-1.2978` | `0.3653` | `-2.3033` | `-0.4692` | `0.8864` |
| `F_norm_N` | `3.1472` | `0.2916` | `2.2233` | `3.9738` | `1.0843` |

N2 verdict: baseline captured successfully. Treat this as a no-contact UR RTDE
force baseline only, not as contact evidence and not as mounted-stack
calibration.

## Next Step

Continue reading `manual4UR`. Before any C0/micro-contact SOP, repeat N1/N2 in
the final bench state, then write a separate first-contact SOP with explicit
target, speed, force threshold, operator stop action, and approval phrase.
