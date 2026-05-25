# Phase1 Packet Freshness After V143 Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v144-phase1-packet-freshness`

Run: `runs/phase1_packet_freshness_after_v143/20260525T180000`

## Scope

This v144 audit checks whether the exact phase1 read-only approval packet is
still current after the v143 post-v142 completion gate. It compares the
current registry, v129 frozen approval request, current packet metrics,
packet audit, packet Markdown hash, and v143 completion gate.

It performs no live access, no measurement collection, no approval, and no
evidence finalization.

## Result

Key metrics:

```text
audit_passed = true
phase1_packet_fresh = true
registry_matches_frozen_packet = true
packet_hash_unchanged = true
frozen_step_id = phase1_mounted_stack_tcp_contact_measurement
frozen_worksheet = tcp_contact_measurements.csv
approval_phrase_required = I approve this read-only measurement step
exact_step_id_required = true
phase1_packet_still_not_approved = true
post_v143_completion_gate_binding = true
approved_read_only_run_count = 0
approved_read_only_audit_passed_count = 0
readiness_completion_evidence_ids = []
approval_record_created = false
live_access_authorized_now = false
execution_authorized_now = false
approved_read_only_evidence_created = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

The packet Markdown hash remains:

```text
91d27eac0d13b988d989353614b0400e1149092af9a631b91f18794d9cdbe93d
```

## Interpretation

The exact first approval candidate is still:

```text
step: phase1_mounted_stack_tcp_contact_measurement
worksheet: tcp_contact_measurements.csv
phrase: I approve this read-only measurement step
```

The packet is still `not_approved`. It remains an approval request template,
not an approval record. It still authorizes no live access, no execution, no
robot motion, no writes, no zeroing/biasing, no force control, and no approved
read-only evidence.

## Validation

- `python3 -m py_compile scripts/audit_phase1_packet_freshness_after_v143.py`
- `scripts/run_tests.sh tests/test_phase1_packet_freshness_after_v143.py`
  reported `4 passed in 0.20s`.
- `python3 scripts/audit_phase1_packet_freshness_after_v143.py --run-id 20260525T180000`
- Full tests passed with `283 passed in 31.89s`.
- YAML anchor scan found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads in the v144 run artifact.
- `git diff --check` passed.
- Implementation commit:
  `fd86daa91ea7a3201bb567ebf59cceb2f27e96d4`

## Limit

This is offline packet freshness bookkeeping only. It does not collect live
measurements, approve a read-only SOP step, create repository approved
calibration evidence, accept a contact model, accept a setup target, relax a
gate, prove strict paper-equivalent feasibility, prove robustness, establish
hardware readiness, authorize live access, authorize execution, or authorize
hardware work.
