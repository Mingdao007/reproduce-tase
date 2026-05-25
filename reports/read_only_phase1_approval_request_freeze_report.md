# Read-Only Phase1 Approval Request Freeze Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v129-readonly-phase1-approval-request-freeze`

Run: `runs/read_only_phase1_approval_request_freeze/20260525T112000`

## Scope

This v129 audit freezes the exact not-approved approval request for the v128
first candidate. It checks the selected phase1 packet metrics, packet audit,
packet Markdown, and post-approval command plan. It does not ask for approval,
approve the packet, instantiate an evidence run, collect live measurements, or
authorize execution.

## Result

Key metrics:

```text
audit_passed = true
approval_request_freeze_complete = true
frozen_step_id = phase1_mounted_stack_tcp_contact_measurement
frozen_worksheet = tcp_contact_measurements.csv
approval_phrase_required = I approve this read-only measurement step
exact_step_id_required = true
packet_markdown_sha256 = 91d27eac0d13b988d989353614b0400e1149092af9a631b91f18794d9cdbe93d
packet_status = approval_packet_created_not_approved
packet_audit_passed = true
packet_approval_status = not_approved
approved_packet_count = 0
execution_authorizing_packet_count = 0
live_access_authorizing_packet_count = 0
approved_read_only_evidence_created = false
freeze_authorizes_live_access = false
freeze_authorizes_execution = false
freeze_creates_approved_evidence = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

Frozen request:

```text
Approve read-only step `phase1_mounted_stack_tcp_contact_measurement` only with
the exact phrase `I approve this read-only measurement step`. Worksheet scope:
`tcp_contact_measurements.csv`.
```

Forbidden actions remain:

```text
robot_motion
force_control
zeroing_or_biasing
tcp_payload_cog_urcap_onrobot_or_rtde_writes
```

## Interpretation

V129 makes the future approval request unambiguous without turning it into an
approval record. If a future user approves, the step to name is
`phase1_mounted_stack_tcp_contact_measurement`, the only worksheet in scope is
`tcp_contact_measurements.csv`, and the same scaffold, finalizer, and
approved-read-only audit path remains required.

## Validation

- `python3 -m py_compile scripts/audit_read_only_phase1_approval_request_freeze.py`
- `scripts/run_tests.sh tests/test_read_only_phase1_approval_request_freeze.py`
  reported `3 passed in 0.11s`.
- `python3 scripts/audit_read_only_phase1_approval_request_freeze.py --run-id 20260525T112000`
- YAML anchor check found no anchors in
  `runs/read_only_phase1_approval_request_freeze/20260525T112000/metrics.yaml`.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v129 run
  directory.
- Full tests passed with `220 passed in 11.97s`.
- `git diff --check` passed.

## Limit

This is offline approval-request bookkeeping only. It does not collect live
measurements, approve a read-only SOP step, create approved calibration
evidence, accept a contact model, accept a setup target, relax a gate, prove
strict paper-equivalent feasibility, prove robustness, establish hardware
readiness, or authorize hardware work.
