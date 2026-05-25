# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V121

Date: 2026-05-25

Use this after the v120 read-only step approval packet. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v120 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v121.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_step_approval_packet_report.md`
- `runs/read_only_step_approval_packet/20260525T095500/metrics.yaml`
- `runs/read_only_step_approval_packet_audit/20260525T095501/metrics.yaml`
- `reports/read_only_sop_step_registry_guard_report.md`
- `configs/read_only_sop_step_registry.yaml`
- `reports/post_v117_evidence_readiness_report.md`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, not contact
calibrated, and not hardware-ready. The UR10e adapted line is diagnostic
simulation only. V118 scans the actual post-v117 repository state and reports
no approved read-only evidence, no accepted orientation review, no accepted
contact/setup-target review, strict terminal pass `0`, closed robustness cells
`0`, and no hardware gate report. V119 adds an exact read-only SOP step
registry and guards finalization/audit. V120 creates an audited
not-approved approval packet for
`phase1_mounted_stack_tcp_contact_measurement`; it allows only
`tcp_contact_measurements.csv`, authorizes no live access, motion, writes,
zeroing, force control, acceptance, hardware readiness, or goal completion.

Concrete v121 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the audited v120 packet or another registered finalizer-eligible
step ID, the v93 read-only scaffold, v91/v119 finalizer, and v90/v119 verifier,
or, if no such approval exists, continue only offline non-final work. With no
approval, avoid repeating v113-v116 matrices over the same policy, timing,
seed, and objective families. Use the v117 scaffold before accepting any
contact/setup-target definition. Do not move the real UR10e. Do not write TCP,
payload, CoG, URCap settings, OnRobot settings, RTDE registers,
zero/bias/filter settings, or run force control unless the user separately
approves that exact SOP step.
```

## Current Verified V120 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v120-readonly-step-approval-packet
```

Verified implementation commit:

```text
IMPLEMENTATION_COMMIT_PENDING
```

V120 artifacts:

```text
scripts/create_read_only_step_approval_packet.py
scripts/audit_read_only_step_approval_packet.py
tests/test_read_only_step_approval_packet.py
runs/read_only_step_approval_packet/20260525T095500
runs/read_only_step_approval_packet_audit/20260525T095501
reports/read_only_step_approval_packet_report.md
```

Key result:

```text
packet_status = approval_packet_created_not_approved
audit_passed = true
violations = []
selected_step.step_id = phase1_mounted_stack_tcp_contact_measurement
selected_step.allowed_worksheets = [tcp_contact_measurements.csv]
approval_request.approval_status = not_approved
packet_authorizes_execution = false
packet_authorizes_live_access = false
live_hardware_accessed = false
robot_motion_commanded = false
configuration_written = false
zeroing_or_biasing_performed = false
force_control_run = false
hardware_readiness = false
do_not_mark_goal_complete = true
```

## Recommended V121 Work

Start with explicit user approval before any live bench read. If the user
approves the v120 packet exactly, instantiate a fresh run folder, fill only
`tcp_contact_measurements.csv`, finalize with the registered step ID, and audit
in approved-read-only mode.

If no live read-only step is approved, continue only non-final offline probes:

- Treat `approved_read_only_calibration_evidence` as the top overall blocker.
- Keep contact/setup-target acceptance, orientation gate acceptance, contact
  calibration, robustness proof, strict feasibility, and hardware readiness
  false unless a later audit supplies stronger evidence.
- Avoid repeating v113-v116 policy, command-limiting, explicit-constraint, or
  terminal minimax experiments over the same accepted model and seeds.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Do not use OnRobot direct TCP DAQ as control truth until the force-source
  discrepancy is resolved.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user.
