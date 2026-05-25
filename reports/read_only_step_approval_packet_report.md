# Read-Only Step Approval Packet Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v120-readonly-step-approval-packet`

Implementation commit: `c897dfa467b823c8cf6fc68b54f290a29942a704`

## Objective

Create a non-executing approval packet path for one exact registered
read-only SOP step. The packet is intended to make future approval review
concrete by naming the registry step ID, allowed worksheet rows, required
confirmation phrase, and forbidden actions before any live read-only evidence
collection is attempted.

No hardware command, live read, robot motion, configuration write, zeroing,
force-control step, approved evidence finalization, contact/setup-target
acceptance, orientation-gate acceptance, or hardware-readiness claim is
performed.

## Artifacts

- New packet creator:
  `scripts/create_read_only_step_approval_packet.py`
- New packet auditor:
  `scripts/audit_read_only_step_approval_packet.py`
- New packet run:
  `runs/read_only_step_approval_packet/20260525T095500`
- New packet audit:
  `runs/read_only_step_approval_packet_audit/20260525T095501`
- New tests:
  `tests/test_read_only_step_approval_packet.py`

## Result

The generated packet is for:

```text
step_id = phase1_mounted_stack_tcp_contact_measurement
title = Mounted stack TCP/contact point read-only measurement
allowed_worksheets = [tcp_contact_measurements.csv]
required_confirmation_phrase = I approve this read-only measurement step
approval_status = not_approved
packet_authorizes_execution = false
packet_authorizes_live_access = false
```

The packet audit reports:

```text
audit_passed = true
violations = []
packet_status = approval_packet_created_not_approved
approval_request.approval_status = not_approved
execution.live_hardware_accessed = false
execution.robot_motion_commanded = false
execution.configuration_written = false
execution.zeroing_or_biasing_performed = false
execution.force_control_run = false
claim_boundary.hardware_readiness = false
claim_boundary.do_not_mark_goal_complete = true
```

The packet forbids:

```text
robot_motion
force_control
zeroing_or_biasing
tcp_payload_cog_urcap_onrobot_or_rtde_writes
```

## Claim Boundary

V120 is offline approval-scoping work only. It does not collect live
measurements, execute the read-only SOP, move the UR10e, write configuration,
zero/bias/filter the force sensor, run force control, reconcile force-source
frames, accept a contact model, accept a setup target, relax a gate, calibrate
contact geometry, prove robustness, prove strict paper-equivalent feasibility,
or make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/create_read_only_step_approval_packet.py scripts/audit_read_only_step_approval_packet.py`
  passed.
- `scripts/run_tests.sh tests/test_read_only_step_approval_packet.py`
  passed with `4 passed in 0.32s`.
- `python3 scripts/create_read_only_step_approval_packet.py --step-id phase1_mounted_stack_tcp_contact_measurement --packet-id 20260525T095500`
  created the v120 packet.
- `python3 scripts/audit_read_only_step_approval_packet.py runs/read_only_step_approval_packet/20260525T095500 --run-id 20260525T095501`
  passed.
- `rg -n "&id|\*id" runs/read_only_step_approval_packet/20260525T095500/metrics.yaml runs/read_only_step_approval_packet_audit/20260525T095501/metrics.yaml`
  found no YAML anchors in the root summary metrics.
- `find runs/read_only_step_approval_packet/20260525T095500 runs/read_only_step_approval_packet_audit/20260525T095501 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `192 passed in 8.56s`.
- `git diff --check`
  passed.
- Branch push was verified at
  `c897dfa467b823c8cf6fc68b54f290a29942a704`.

## Next Step

The top blocker remains explicit approval for one exact read-only SOP step.
This packet is not approval. If the user approves this exact packet later,
instantiate a fresh read-only measurement run, fill only
`tcp_contact_measurements.csv`, finalize with
`--approved-step-id phase1_mounted_stack_tcp_contact_measurement`, and audit in
approved-read-only mode. Without approval, continue only non-final offline work
and keep all contact/setup-target, orientation-gate, robustness,
strict-feasibility, and hardware-readiness claims false.
