# Read-Only Phase1 Approval Request Freeze Audit

Run id: `20260525T112000`

Audit passed: `True`
Freeze complete: `True`
Frozen step ID: `phase1_mounted_stack_tcp_contact_measurement`
Frozen worksheet: `tcp_contact_measurements.csv`
Approval phrase required: `I approve this read-only measurement step`
Exact step ID required: `True`
Packet status: `approval_packet_created_not_approved`
Packet audit passed: `True`
Packet approval status: `not_approved`
Freeze authorizes execution: `False`
Approved read-only evidence created: `False`
Completion claim allowed: `False`
Do not mark goal complete: `True`

Frozen approval request:

- Approve read-only step `phase1_mounted_stack_tcp_contact_measurement` only with the exact phrase `I approve this read-only measurement step`. Worksheet scope: `tcp_contact_measurements.csv`.
- Allowed worksheet: `tcp_contact_measurements.csv`
- Forbidden actions: `robot_motion, force_control, zeroing_or_biasing, tcp_payload_cog_urcap_onrobot_or_rtde_writes`

Post-approval command plan, only after future explicit approval:

- python3 scripts/create_read_only_calibration_measurement_run.py --run-id <fresh_run_id>
- Fill only the approved worksheet(s): tcp_contact_measurements.csv; leave all other worksheet CSVs empty.
- python3 scripts/finalize_read_only_calibration_measurement_evidence.py runs/read_only_calibration_measurement/<fresh_run_id> --confirmation-phrase 'I approve this read-only measurement step' --approved-step-id phase1_mounted_stack_tcp_contact_measurement --operator <operator> --live-hardware-accessed <true|false>
- python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/<fresh_run_id> --audit-mode approved-read-only --run-id <fresh_audit_id>

Violations:

- None

Interpretation:

The selected phase1 packet is frozen as a not-approved approval request. This artifact clarifies exactly what a future approval would need to name, but it is not itself approval and authorizes no live access or execution.
